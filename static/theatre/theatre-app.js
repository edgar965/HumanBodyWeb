/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const js={ROTATE:0,DOLLY:1,PAN:2},zs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},oT=0,Tp=1,aT=2,cg=1,lg=2,zi=3,Xi=0,Bn=1,Fn=2,mr=0,Xs=1,Ep=2,Ap=3,wp=4,cT=5,Jr=100,lT=101,uT=102,hT=103,dT=104,fT=200,pT=201,mT=202,gT=203,ph=204,mh=205,_T=206,vT=207,yT=208,xT=209,bT=210,ST=211,MT=212,TT=213,ET=214,gh=0,_h=1,vh=2,Zs=3,yh=4,xh=5,bh=6,Sh=7,ug=0,AT=1,wT=2,gr=0,PT=1,RT=2,CT=3,hg=4,IT=5,LT=6,DT=7,Pp="attached",NT="detached",dg=300,$s=301,Js=302,Mh=303,Th=304,Fc=306,Qs=1e3,fr=1001,Ic=1002,In=1003,fg=1004,Go=1005,Zn=1006,Sc=1007,Vi=1008,qi=1009,pg=1010,mg=1011,Jo=1012,ad=1013,ts=1014,di=1015,na=1016,cd=1017,ld=1018,eo=1020,gg=35902,_g=1021,vg=1022,ni=1023,yg=1024,xg=1025,qs=1026,to=1027,ud=1028,hd=1029,bg=1030,dd=1031,fd=1033,Mc=33776,Tc=33777,Ec=33778,Ac=33779,Eh=35840,Ah=35841,wh=35842,Ph=35843,Rh=36196,Ch=37492,Ih=37496,Lh=37808,Dh=37809,Nh=37810,Oh=37811,Uh=37812,Fh=37813,Bh=37814,kh=37815,zh=37816,Hh=37817,Vh=37818,Gh=37819,Wh=37820,jh=37821,wc=36492,Xh=36494,qh=36495,Sg=36283,Yh=36284,Kh=36285,Zh=36286,OT=2200,Mg=2201,UT=2202,Qo=2300,ea=2301,bu=2302,Hs=2400,Vs=2401,Lc=2402,pd=2500,FT=2501,BT=0,Tg=1,$h=2,kT=3200,zT=3201,Eg=0,HT=1,dr="",dn="srgb",Ln="srgb-linear",Bc="linear",Dt="srgb",Es=7680,Rp=519,VT=512,GT=513,WT=514,Ag=515,jT=516,XT=517,qT=518,YT=519,Jh=35044,Cp="300 es",Gi=2e3,Dc=2001;class vr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,a=i.length;s<a;s++)i[s].call(this,e);e.target=null}}}const Mn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Ip=1234567;const Ko=Math.PI/180,no=180/Math.PI;function fi(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Mn[r&255]+Mn[r>>8&255]+Mn[r>>16&255]+Mn[r>>24&255]+"-"+Mn[e&255]+Mn[e>>8&255]+"-"+Mn[e>>16&15|64]+Mn[e>>24&255]+"-"+Mn[t&63|128]+Mn[t>>8&255]+"-"+Mn[t>>16&255]+Mn[t>>24&255]+Mn[n&255]+Mn[n>>8&255]+Mn[n>>16&255]+Mn[n>>24&255]).toLowerCase()}function vn(r,e,t){return Math.max(e,Math.min(t,r))}function md(r,e){return(r%e+e)%e}function KT(r,e,t,n,i){return n+(r-e)*(i-n)/(t-e)}function ZT(r,e,t){return r!==e?(t-r)/(e-r):0}function Zo(r,e,t){return(1-t)*r+t*e}function $T(r,e,t,n){return Zo(r,e,1-Math.exp(-t*n))}function JT(r,e=1){return e-Math.abs(md(r,e*2)-e)}function QT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*(3-2*r))}function eE(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*r*(r*(r*6-15)+10))}function tE(r,e){return r+Math.floor(Math.random()*(e-r+1))}function nE(r,e){return r+Math.random()*(e-r)}function iE(r){return r*(.5-Math.random())}function rE(r){r!==void 0&&(Ip=r);let e=Ip+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function sE(r){return r*Ko}function oE(r){return r*no}function aE(r){return(r&r-1)===0&&r!==0}function cE(r){return Math.pow(2,Math.ceil(Math.log(r)/Math.LN2))}function lE(r){return Math.pow(2,Math.floor(Math.log(r)/Math.LN2))}function uE(r,e,t,n,i){const s=Math.cos,a=Math.sin,c=s(t/2),u=a(t/2),h=s((e+n)/2),f=a((e+n)/2),p=s((e-n)/2),m=a((e-n)/2),g=s((n-e)/2),x=a((n-e)/2);switch(i){case"XYX":r.set(c*f,u*p,u*m,c*h);break;case"YZY":r.set(u*m,c*f,u*p,c*h);break;case"ZXZ":r.set(u*p,u*m,c*f,c*h);break;case"XZX":r.set(c*f,u*x,u*g,c*h);break;case"YXY":r.set(u*g,c*f,u*x,c*h);break;case"ZYZ":r.set(u*x,u*g,c*f,c*h);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function ui(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function Lt(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}const wg={DEG2RAD:Ko,RAD2DEG:no,generateUUID:fi,clamp:vn,euclideanModulo:md,mapLinear:KT,inverseLerp:ZT,lerp:Zo,damp:$T,pingpong:JT,smoothstep:QT,smootherstep:eE,randInt:tE,randFloat:nE,randFloatSpread:iE,seededRandom:rE,degToRad:sE,radToDeg:oE,isPowerOfTwo:aE,ceilPowerOfTwo:cE,floorPowerOfTwo:lE,setQuaternionFromProperEuler:uE,normalize:Lt,denormalize:ui};class Qe{constructor(e=0,t=0){Qe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(vn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*i+e.x,this.y=s*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class ut{constructor(e,t,n,i,s,a,c,u,h){ut.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h)}set(e,t,n,i,s,a,c,u,h){const f=this.elements;return f[0]=e,f[1]=i,f[2]=c,f[3]=t,f[4]=s,f[5]=u,f[6]=n,f[7]=a,f[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[3],u=n[6],h=n[1],f=n[4],p=n[7],m=n[2],g=n[5],x=n[8],M=i[0],v=i[3],_=i[6],A=i[1],P=i[4],S=i[7],k=i[2],O=i[5],U=i[8];return s[0]=a*M+c*A+u*k,s[3]=a*v+c*P+u*O,s[6]=a*_+c*S+u*U,s[1]=h*M+f*A+p*k,s[4]=h*v+f*P+p*O,s[7]=h*_+f*S+p*U,s[2]=m*M+g*A+x*k,s[5]=m*v+g*P+x*O,s[8]=m*_+g*S+x*U,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8];return t*a*f-t*c*h-n*s*f+n*c*u+i*s*h-i*a*u}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=f*a-c*h,m=c*u-f*s,g=h*s-a*u,x=t*p+n*m+i*g;if(x===0)return this.set(0,0,0,0,0,0,0,0,0);const M=1/x;return e[0]=p*M,e[1]=(i*h-f*n)*M,e[2]=(c*n-i*a)*M,e[3]=m*M,e[4]=(f*t-i*u)*M,e[5]=(i*s-c*t)*M,e[6]=g*M,e[7]=(n*u-h*t)*M,e[8]=(a*t-n*s)*M,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,a,c){const u=Math.cos(s),h=Math.sin(s);return this.set(n*u,n*h,-n*(u*a+h*c)+a+e,-i*h,i*u,-i*(-h*a+u*c)+c+t,0,0,1),this}scale(e,t){return this.premultiply(Su.makeScale(e,t)),this}rotate(e){return this.premultiply(Su.makeRotation(-e)),this}translate(e,t){return this.premultiply(Su.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Su=new ut;function Pg(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function ta(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function hE(){const r=ta("canvas");return r.style.display="block",r}const Lp={};function Wo(r){r in Lp||(Lp[r]=!0,console.warn(r))}function dE(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function fE(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function pE(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const bt={enabled:!0,workingColorSpace:Ln,spaces:{},convert:function(r,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Dt&&(r.r=ji(r.r),r.g=ji(r.g),r.b=ji(r.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(r.applyMatrix3(this.spaces[e].toXYZ),r.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Dt&&(r.r=Ys(r.r),r.g=Ys(r.g),r.b=Ys(r.b))),r},fromWorkingColorSpace:function(r,e){return this.convert(r,this.workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===dr?Bc:this.spaces[r].transfer},getLuminanceCoefficients:function(r,e=this.workingColorSpace){return r.fromArray(this.spaces[e].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,e,t){return r.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace}};function ji(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ys(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}const Dp=[.64,.33,.3,.6,.15,.06],Np=[.2126,.7152,.0722],Op=[.3127,.329],Up=new ut().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),Fp=new ut().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);bt.define({[Ln]:{primaries:Dp,whitePoint:Op,transfer:Bc,toXYZ:Up,fromXYZ:Fp,luminanceCoefficients:Np,workingColorSpaceConfig:{unpackColorSpace:dn},outputColorSpaceConfig:{drawingBufferColorSpace:dn}},[dn]:{primaries:Dp,whitePoint:Op,transfer:Dt,toXYZ:Up,fromXYZ:Fp,luminanceCoefficients:Np,outputColorSpaceConfig:{drawingBufferColorSpace:dn}}});let As;class mE{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{As===void 0&&(As=ta("canvas")),As.width=e.width,As.height=e.height;const n=As.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=As}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=ta("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let a=0;a<s.length;a++)s[a]=ji(s[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(ji(t[n]/255)*255):t[n]=ji(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let gE=0;class Rg{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:gE++}),this.uuid=fi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let a=0,c=i.length;a<c;a++)i[a].isDataTexture?s.push(Mu(i[a].image)):s.push(Mu(i[a]))}else s=Mu(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function Mu(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?mE.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let _E=0;class fn extends vr{constructor(e=fn.DEFAULT_IMAGE,t=fn.DEFAULT_MAPPING,n=fr,i=fr,s=Zn,a=Vi,c=ni,u=qi,h=fn.DEFAULT_ANISOTROPY,f=dr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:_E++}),this.uuid=fi(),this.name="",this.source=new Rg(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=a,this.anisotropy=h,this.format=c,this.internalFormat=null,this.type=u,this.offset=new Qe(0,0),this.repeat=new Qe(1,1),this.center=new Qe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ut,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==dg)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Qs:e.x=e.x-Math.floor(e.x);break;case fr:e.x=e.x<0?0:1;break;case Ic:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Qs:e.y=e.y-Math.floor(e.y);break;case fr:e.y=e.y<0?0:1;break;case Ic:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}fn.DEFAULT_IMAGE=null;fn.DEFAULT_MAPPING=dg;fn.DEFAULT_ANISOTROPY=1;class Et{constructor(e=0,t=0,n=0,i=1){Et.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const u=e.elements,h=u[0],f=u[4],p=u[8],m=u[1],g=u[5],x=u[9],M=u[2],v=u[6],_=u[10];if(Math.abs(f-m)<.01&&Math.abs(p-M)<.01&&Math.abs(x-v)<.01){if(Math.abs(f+m)<.1&&Math.abs(p+M)<.1&&Math.abs(x+v)<.1&&Math.abs(h+g+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const P=(h+1)/2,S=(g+1)/2,k=(_+1)/2,O=(f+m)/4,U=(p+M)/4,z=(x+v)/4;return P>S&&P>k?P<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(P),i=O/n,s=U/n):S>k?S<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(S),n=O/i,s=z/i):k<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(k),n=U/s,i=z/s),this.set(n,i,s,t),this}let A=Math.sqrt((v-x)*(v-x)+(p-M)*(p-M)+(m-f)*(m-f));return Math.abs(A)<.001&&(A=1),this.x=(v-x)/A,this.y=(p-M)/A,this.z=(m-f)/A,this.w=Math.acos((h+g+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class vE extends vr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Et(0,0,e,t),this.scissorTest=!1,this.viewport=new Et(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Zn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new fn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let c=0;c<a;c++)this.textures[c]=s.clone(),this.textures[c].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Rg(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class ns extends vE{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Cg extends fn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=In,this.minFilter=In,this.wrapR=fr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class yE extends fn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=In,this.minFilter=In,this.wrapR=fr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Wt{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,a,c){let u=n[i+0],h=n[i+1],f=n[i+2],p=n[i+3];const m=s[a+0],g=s[a+1],x=s[a+2],M=s[a+3];if(c===0){e[t+0]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p;return}if(c===1){e[t+0]=m,e[t+1]=g,e[t+2]=x,e[t+3]=M;return}if(p!==M||u!==m||h!==g||f!==x){let v=1-c;const _=u*m+h*g+f*x+p*M,A=_>=0?1:-1,P=1-_*_;if(P>Number.EPSILON){const k=Math.sqrt(P),O=Math.atan2(k,_*A);v=Math.sin(v*O)/k,c=Math.sin(c*O)/k}const S=c*A;if(u=u*v+m*S,h=h*v+g*S,f=f*v+x*S,p=p*v+M*S,v===1-c){const k=1/Math.sqrt(u*u+h*h+f*f+p*p);u*=k,h*=k,f*=k,p*=k}}e[t]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p}static multiplyQuaternionsFlat(e,t,n,i,s,a){const c=n[i],u=n[i+1],h=n[i+2],f=n[i+3],p=s[a],m=s[a+1],g=s[a+2],x=s[a+3];return e[t]=c*x+f*p+u*g-h*m,e[t+1]=u*x+f*m+h*p-c*g,e[t+2]=h*x+f*g+c*m-u*p,e[t+3]=f*x-c*p-u*m-h*g,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,a=e._order,c=Math.cos,u=Math.sin,h=c(n/2),f=c(i/2),p=c(s/2),m=u(n/2),g=u(i/2),x=u(s/2);switch(a){case"XYZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"YXZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"ZXY":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"ZYX":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"YZX":this._x=m*f*p+h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p-m*g*x;break;case"XZY":this._x=m*f*p-h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p+m*g*x;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],a=t[1],c=t[5],u=t[9],h=t[2],f=t[6],p=t[10],m=n+c+p;if(m>0){const g=.5/Math.sqrt(m+1);this._w=.25/g,this._x=(f-u)*g,this._y=(s-h)*g,this._z=(a-i)*g}else if(n>c&&n>p){const g=2*Math.sqrt(1+n-c-p);this._w=(f-u)/g,this._x=.25*g,this._y=(i+a)/g,this._z=(s+h)/g}else if(c>p){const g=2*Math.sqrt(1+c-n-p);this._w=(s-h)/g,this._x=(i+a)/g,this._y=.25*g,this._z=(u+f)/g}else{const g=2*Math.sqrt(1+p-n-c);this._w=(a-i)/g,this._x=(s+h)/g,this._y=(u+f)/g,this._z=.25*g}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(vn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,a=e._w,c=t._x,u=t._y,h=t._z,f=t._w;return this._x=n*f+a*c+i*h-s*u,this._y=i*f+a*u+s*c-n*h,this._z=s*f+a*h+n*u-i*c,this._w=a*f-n*c-i*u-s*h,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,a=this._w;let c=a*e._w+n*e._x+i*e._y+s*e._z;if(c<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,c=-c):this.copy(e),c>=1)return this._w=a,this._x=n,this._y=i,this._z=s,this;const u=1-c*c;if(u<=Number.EPSILON){const g=1-t;return this._w=g*a+t*this._w,this._x=g*n+t*this._x,this._y=g*i+t*this._y,this._z=g*s+t*this._z,this.normalize(),this}const h=Math.sqrt(u),f=Math.atan2(h,c),p=Math.sin((1-t)*f)/h,m=Math.sin(t*f)/h;return this._w=a*p+this._w*m,this._x=n*p+this._x*m,this._y=i*p+this._y*m,this._z=s*p+this._z*m,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class F{constructor(e=0,t=0,n=0){F.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Bp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Bp.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,a=e.y,c=e.z,u=e.w,h=2*(a*i-c*n),f=2*(c*t-s*i),p=2*(s*n-a*t);return this.x=t+u*h+a*p-c*f,this.y=n+u*f+c*h-s*p,this.z=i+u*p+s*f-a*h,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,a=t.x,c=t.y,u=t.z;return this.x=i*u-s*c,this.y=s*a-n*u,this.z=n*c-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Tu.copy(this).projectOnVector(e),this.sub(Tu)}reflect(e){return this.sub(Tu.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(vn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Tu=new F,Bp=new Wt;class Yi{constructor(e=new F(1/0,1/0,1/0),t=new F(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(oi.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(oi.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=oi.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,c=s.count;a<c;a++)e.isMesh===!0?e.getVertexPosition(a,oi):oi.fromBufferAttribute(s,a),oi.applyMatrix4(e.matrixWorld),this.expandByPoint(oi);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Ga.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Ga.copy(n.boundingBox)),Ga.applyMatrix4(e.matrixWorld),this.union(Ga)}const i=e.children;for(let s=0,a=i.length;s<a;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,oi),oi.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Lo),Wa.subVectors(this.max,Lo),ws.subVectors(e.a,Lo),Ps.subVectors(e.b,Lo),Rs.subVectors(e.c,Lo),nr.subVectors(Ps,ws),ir.subVectors(Rs,Ps),Vr.subVectors(ws,Rs);let t=[0,-nr.z,nr.y,0,-ir.z,ir.y,0,-Vr.z,Vr.y,nr.z,0,-nr.x,ir.z,0,-ir.x,Vr.z,0,-Vr.x,-nr.y,nr.x,0,-ir.y,ir.x,0,-Vr.y,Vr.x,0];return!Eu(t,ws,Ps,Rs,Wa)||(t=[1,0,0,0,1,0,0,0,1],!Eu(t,ws,Ps,Rs,Wa))?!1:(ja.crossVectors(nr,ir),t=[ja.x,ja.y,ja.z],Eu(t,ws,Ps,Rs,Wa))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,oi).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(oi).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Ni[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Ni[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Ni[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Ni[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Ni[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Ni[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Ni[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Ni[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Ni),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Ni=[new F,new F,new F,new F,new F,new F,new F,new F],oi=new F,Ga=new Yi,ws=new F,Ps=new F,Rs=new F,nr=new F,ir=new F,Vr=new F,Lo=new F,Wa=new F,ja=new F,Gr=new F;function Eu(r,e,t,n,i){for(let s=0,a=r.length-3;s<=a;s+=3){Gr.fromArray(r,s);const c=i.x*Math.abs(Gr.x)+i.y*Math.abs(Gr.y)+i.z*Math.abs(Gr.z),u=e.dot(Gr),h=t.dot(Gr),f=n.dot(Gr);if(Math.max(-Math.max(u,h,f),Math.min(u,h,f))>c)return!1}return!0}const xE=new Yi,Do=new F,Au=new F;class bi{constructor(e=new F,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):xE.setFromPoints(e).getCenter(n);let i=0;for(let s=0,a=e.length;s<a;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Do.subVectors(e,this.center);const t=Do.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Do,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Au.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Do.copy(e.center).add(Au)),this.expandByPoint(Do.copy(e.center).sub(Au))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Oi=new F,wu=new F,Xa=new F,rr=new F,Pu=new F,qa=new F,Ru=new F;class oo{constructor(e=new F,t=new F(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Oi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Oi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Oi.copy(this.origin).addScaledVector(this.direction,t),Oi.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){wu.copy(e).add(t).multiplyScalar(.5),Xa.copy(t).sub(e).normalize(),rr.copy(this.origin).sub(wu);const s=e.distanceTo(t)*.5,a=-this.direction.dot(Xa),c=rr.dot(this.direction),u=-rr.dot(Xa),h=rr.lengthSq(),f=Math.abs(1-a*a);let p,m,g,x;if(f>0)if(p=a*u-c,m=a*c-u,x=s*f,p>=0)if(m>=-x)if(m<=x){const M=1/f;p*=M,m*=M,g=p*(p+a*m+2*c)+m*(a*p+m+2*u)+h}else m=s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m=-s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m<=-x?(p=Math.max(0,-(-a*s+c)),m=p>0?-s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h):m<=x?(p=0,m=Math.min(Math.max(-s,-u),s),g=m*(m+2*u)+h):(p=Math.max(0,-(a*s+c)),m=p>0?s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h);else m=a>0?-s:s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;return n&&n.copy(this.origin).addScaledVector(this.direction,p),i&&i.copy(wu).addScaledVector(Xa,m),g}intersectSphere(e,t){Oi.subVectors(e.center,this.origin);const n=Oi.dot(this.direction),i=Oi.dot(Oi)-n*n,s=e.radius*e.radius;if(i>s)return null;const a=Math.sqrt(s-i),c=n-a,u=n+a;return u<0?null:c<0?this.at(u,t):this.at(c,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,a,c,u;const h=1/this.direction.x,f=1/this.direction.y,p=1/this.direction.z,m=this.origin;return h>=0?(n=(e.min.x-m.x)*h,i=(e.max.x-m.x)*h):(n=(e.max.x-m.x)*h,i=(e.min.x-m.x)*h),f>=0?(s=(e.min.y-m.y)*f,a=(e.max.y-m.y)*f):(s=(e.max.y-m.y)*f,a=(e.min.y-m.y)*f),n>a||s>i||((s>n||isNaN(n))&&(n=s),(a<i||isNaN(i))&&(i=a),p>=0?(c=(e.min.z-m.z)*p,u=(e.max.z-m.z)*p):(c=(e.max.z-m.z)*p,u=(e.min.z-m.z)*p),n>u||c>i)||((c>n||n!==n)&&(n=c),(u<i||i!==i)&&(i=u),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,Oi)!==null}intersectTriangle(e,t,n,i,s){Pu.subVectors(t,e),qa.subVectors(n,e),Ru.crossVectors(Pu,qa);let a=this.direction.dot(Ru),c;if(a>0){if(i)return null;c=1}else if(a<0)c=-1,a=-a;else return null;rr.subVectors(this.origin,e);const u=c*this.direction.dot(qa.crossVectors(rr,qa));if(u<0)return null;const h=c*this.direction.dot(Pu.cross(rr));if(h<0||u+h>a)return null;const f=-c*rr.dot(Ru);return f<0?null:this.at(f/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class nt{constructor(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v){nt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v)}set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v){const _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=a,_[9]=c,_[13]=u,_[2]=h,_[6]=f,_[10]=p,_[14]=m,_[3]=g,_[7]=x,_[11]=M,_[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new nt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Cs.setFromMatrixColumn(e,0).length(),s=1/Cs.setFromMatrixColumn(e,1).length(),a=1/Cs.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,a=Math.cos(n),c=Math.sin(n),u=Math.cos(i),h=Math.sin(i),f=Math.cos(s),p=Math.sin(s);if(e.order==="XYZ"){const m=a*f,g=a*p,x=c*f,M=c*p;t[0]=u*f,t[4]=-u*p,t[8]=h,t[1]=g+x*h,t[5]=m-M*h,t[9]=-c*u,t[2]=M-m*h,t[6]=x+g*h,t[10]=a*u}else if(e.order==="YXZ"){const m=u*f,g=u*p,x=h*f,M=h*p;t[0]=m+M*c,t[4]=x*c-g,t[8]=a*h,t[1]=a*p,t[5]=a*f,t[9]=-c,t[2]=g*c-x,t[6]=M+m*c,t[10]=a*u}else if(e.order==="ZXY"){const m=u*f,g=u*p,x=h*f,M=h*p;t[0]=m-M*c,t[4]=-a*p,t[8]=x+g*c,t[1]=g+x*c,t[5]=a*f,t[9]=M-m*c,t[2]=-a*h,t[6]=c,t[10]=a*u}else if(e.order==="ZYX"){const m=a*f,g=a*p,x=c*f,M=c*p;t[0]=u*f,t[4]=x*h-g,t[8]=m*h+M,t[1]=u*p,t[5]=M*h+m,t[9]=g*h-x,t[2]=-h,t[6]=c*u,t[10]=a*u}else if(e.order==="YZX"){const m=a*u,g=a*h,x=c*u,M=c*h;t[0]=u*f,t[4]=M-m*p,t[8]=x*p+g,t[1]=p,t[5]=a*f,t[9]=-c*f,t[2]=-h*f,t[6]=g*p+x,t[10]=m-M*p}else if(e.order==="XZY"){const m=a*u,g=a*h,x=c*u,M=c*h;t[0]=u*f,t[4]=-p,t[8]=h*f,t[1]=m*p+M,t[5]=a*f,t[9]=g*p-x,t[2]=x*p-g,t[6]=c*f,t[10]=M*p+m}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(bE,e,SE)}lookAt(e,t,n){const i=this.elements;return Yn.subVectors(e,t),Yn.lengthSq()===0&&(Yn.z=1),Yn.normalize(),sr.crossVectors(n,Yn),sr.lengthSq()===0&&(Math.abs(n.z)===1?Yn.x+=1e-4:Yn.z+=1e-4,Yn.normalize(),sr.crossVectors(n,Yn)),sr.normalize(),Ya.crossVectors(Yn,sr),i[0]=sr.x,i[4]=Ya.x,i[8]=Yn.x,i[1]=sr.y,i[5]=Ya.y,i[9]=Yn.y,i[2]=sr.z,i[6]=Ya.z,i[10]=Yn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[4],u=n[8],h=n[12],f=n[1],p=n[5],m=n[9],g=n[13],x=n[2],M=n[6],v=n[10],_=n[14],A=n[3],P=n[7],S=n[11],k=n[15],O=i[0],U=i[4],z=i[8],I=i[12],w=i[1],H=i[5],ee=i[9],J=i[13],oe=i[2],ce=i[6],$=i[10],le=i[14],ne=i[3],ge=i[7],Te=i[11],Oe=i[15];return s[0]=a*O+c*w+u*oe+h*ne,s[4]=a*U+c*H+u*ce+h*ge,s[8]=a*z+c*ee+u*$+h*Te,s[12]=a*I+c*J+u*le+h*Oe,s[1]=f*O+p*w+m*oe+g*ne,s[5]=f*U+p*H+m*ce+g*ge,s[9]=f*z+p*ee+m*$+g*Te,s[13]=f*I+p*J+m*le+g*Oe,s[2]=x*O+M*w+v*oe+_*ne,s[6]=x*U+M*H+v*ce+_*ge,s[10]=x*z+M*ee+v*$+_*Te,s[14]=x*I+M*J+v*le+_*Oe,s[3]=A*O+P*w+S*oe+k*ne,s[7]=A*U+P*H+S*ce+k*ge,s[11]=A*z+P*ee+S*$+k*Te,s[15]=A*I+P*J+S*le+k*Oe,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],a=e[1],c=e[5],u=e[9],h=e[13],f=e[2],p=e[6],m=e[10],g=e[14],x=e[3],M=e[7],v=e[11],_=e[15];return x*(+s*u*p-i*h*p-s*c*m+n*h*m+i*c*g-n*u*g)+M*(+t*u*g-t*h*m+s*a*m-i*a*g+i*h*f-s*u*f)+v*(+t*h*p-t*c*g-s*a*p+n*a*g+s*c*f-n*h*f)+_*(-i*c*f-t*u*p+t*c*m+i*a*p-n*a*m+n*u*f)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=e[9],m=e[10],g=e[11],x=e[12],M=e[13],v=e[14],_=e[15],A=p*v*h-M*m*h+M*u*g-c*v*g-p*u*_+c*m*_,P=x*m*h-f*v*h-x*u*g+a*v*g+f*u*_-a*m*_,S=f*M*h-x*p*h+x*c*g-a*M*g-f*c*_+a*p*_,k=x*p*u-f*M*u-x*c*m+a*M*m+f*c*v-a*p*v,O=t*A+n*P+i*S+s*k;if(O===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const U=1/O;return e[0]=A*U,e[1]=(M*m*s-p*v*s-M*i*g+n*v*g+p*i*_-n*m*_)*U,e[2]=(c*v*s-M*u*s+M*i*h-n*v*h-c*i*_+n*u*_)*U,e[3]=(p*u*s-c*m*s-p*i*h+n*m*h+c*i*g-n*u*g)*U,e[4]=P*U,e[5]=(f*v*s-x*m*s+x*i*g-t*v*g-f*i*_+t*m*_)*U,e[6]=(x*u*s-a*v*s-x*i*h+t*v*h+a*i*_-t*u*_)*U,e[7]=(a*m*s-f*u*s+f*i*h-t*m*h-a*i*g+t*u*g)*U,e[8]=S*U,e[9]=(x*p*s-f*M*s-x*n*g+t*M*g+f*n*_-t*p*_)*U,e[10]=(a*M*s-x*c*s+x*n*h-t*M*h-a*n*_+t*c*_)*U,e[11]=(f*c*s-a*p*s-f*n*h+t*p*h+a*n*g-t*c*g)*U,e[12]=k*U,e[13]=(f*M*i-x*p*i+x*n*m-t*M*m-f*n*v+t*p*v)*U,e[14]=(x*c*i-a*M*i-x*n*u+t*M*u+a*n*v-t*c*v)*U,e[15]=(a*p*i-f*c*i+f*n*u-t*p*u-a*n*m+t*c*m)*U,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,a=e.x,c=e.y,u=e.z,h=s*a,f=s*c;return this.set(h*a+n,h*c-i*u,h*u+i*c,0,h*c+i*u,f*c+n,f*u-i*a,0,h*u-i*c,f*u+i*a,s*u*u+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,a){return this.set(1,n,s,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,a=t._y,c=t._z,u=t._w,h=s+s,f=a+a,p=c+c,m=s*h,g=s*f,x=s*p,M=a*f,v=a*p,_=c*p,A=u*h,P=u*f,S=u*p,k=n.x,O=n.y,U=n.z;return i[0]=(1-(M+_))*k,i[1]=(g+S)*k,i[2]=(x-P)*k,i[3]=0,i[4]=(g-S)*O,i[5]=(1-(m+_))*O,i[6]=(v+A)*O,i[7]=0,i[8]=(x+P)*U,i[9]=(v-A)*U,i[10]=(1-(m+M))*U,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=Cs.set(i[0],i[1],i[2]).length();const a=Cs.set(i[4],i[5],i[6]).length(),c=Cs.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],ai.copy(this);const h=1/s,f=1/a,p=1/c;return ai.elements[0]*=h,ai.elements[1]*=h,ai.elements[2]*=h,ai.elements[4]*=f,ai.elements[5]*=f,ai.elements[6]*=f,ai.elements[8]*=p,ai.elements[9]*=p,ai.elements[10]*=p,t.setFromRotationMatrix(ai),n.x=s,n.y=a,n.z=c,this}makePerspective(e,t,n,i,s,a,c=Gi){const u=this.elements,h=2*s/(t-e),f=2*s/(n-i),p=(t+e)/(t-e),m=(n+i)/(n-i);let g,x;if(c===Gi)g=-(a+s)/(a-s),x=-2*a*s/(a-s);else if(c===Dc)g=-a/(a-s),x=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+c);return u[0]=h,u[4]=0,u[8]=p,u[12]=0,u[1]=0,u[5]=f,u[9]=m,u[13]=0,u[2]=0,u[6]=0,u[10]=g,u[14]=x,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,n,i,s,a,c=Gi){const u=this.elements,h=1/(t-e),f=1/(n-i),p=1/(a-s),m=(t+e)*h,g=(n+i)*f;let x,M;if(c===Gi)x=(a+s)*p,M=-2*p;else if(c===Dc)x=s*p,M=-1*p;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+c);return u[0]=2*h,u[4]=0,u[8]=0,u[12]=-m,u[1]=0,u[5]=2*f,u[9]=0,u[13]=-g,u[2]=0,u[6]=0,u[10]=M,u[14]=-x,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Cs=new F,ai=new nt,bE=new F(0,0,0),SE=new F(1,1,1),sr=new F,Ya=new F,Yn=new F,kp=new nt,zp=new Wt;class pi{constructor(e=0,t=0,n=0,i=pi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],a=i[4],c=i[8],u=i[1],h=i[5],f=i[9],p=i[2],m=i[6],g=i[10];switch(t){case"XYZ":this._y=Math.asin(vn(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-f,g),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(m,h),this._z=0);break;case"YXZ":this._x=Math.asin(-vn(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(c,g),this._z=Math.atan2(u,h)):(this._y=Math.atan2(-p,s),this._z=0);break;case"ZXY":this._x=Math.asin(vn(m,-1,1)),Math.abs(m)<.9999999?(this._y=Math.atan2(-p,g),this._z=Math.atan2(-a,h)):(this._y=0,this._z=Math.atan2(u,s));break;case"ZYX":this._y=Math.asin(-vn(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(m,g),this._z=Math.atan2(u,s)):(this._x=0,this._z=Math.atan2(-a,h));break;case"YZX":this._z=Math.asin(vn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(-f,h),this._y=Math.atan2(-p,s)):(this._x=0,this._y=Math.atan2(c,g));break;case"XZY":this._z=Math.asin(-vn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(m,h),this._y=Math.atan2(c,s)):(this._x=Math.atan2(-f,g),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return kp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(kp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return zp.setFromEuler(this),this.setFromQuaternion(zp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}pi.DEFAULT_ORDER="XYZ";class gd{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let ME=0;const Hp=new F,Is=new Wt,Ui=new nt,Ka=new F,No=new F,TE=new F,EE=new Wt,Vp=new F(1,0,0),Gp=new F(0,1,0),Wp=new F(0,0,1),jp={type:"added"},AE={type:"removed"},Ls={type:"childadded",child:null},Cu={type:"childremoved",child:null};class Ht extends vr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:ME++}),this.uuid=fi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Ht.DEFAULT_UP.clone();const e=new F,t=new pi,n=new Wt,i=new F(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new nt},normalMatrix:{value:new ut}}),this.matrix=new nt,this.matrixWorld=new nt,this.matrixAutoUpdate=Ht.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Ht.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new gd,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.multiply(Is),this}rotateOnWorldAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.premultiply(Is),this}rotateX(e){return this.rotateOnAxis(Vp,e)}rotateY(e){return this.rotateOnAxis(Gp,e)}rotateZ(e){return this.rotateOnAxis(Wp,e)}translateOnAxis(e,t){return Hp.copy(e).applyQuaternion(this.quaternion),this.position.add(Hp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Vp,e)}translateY(e){return this.translateOnAxis(Gp,e)}translateZ(e){return this.translateOnAxis(Wp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Ui.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Ka.copy(e):Ka.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),No.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ui.lookAt(No,Ka,this.up):Ui.lookAt(Ka,No,this.up),this.quaternion.setFromRotationMatrix(Ui),i&&(Ui.extractRotation(i.matrixWorld),Is.setFromRotationMatrix(Ui),this.quaternion.premultiply(Is.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(jp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(AE),Cu.child=e,this.dispatchEvent(Cu),Cu.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Ui.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Ui.multiply(e.parent.matrixWorld)),e.applyMatrix4(Ui),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(jp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,e,TE),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,EE,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(c=>({boxInitialized:c.boxInitialized,boxMin:c.box.min.toArray(),boxMax:c.box.max.toArray(),sphereInitialized:c.sphereInitialized,sphereRadius:c.sphere.radius,sphereCenter:c.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(c,u){return c[u.uuid]===void 0&&(c[u.uuid]=u.toJSON(e)),u.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const c=this.geometry.parameters;if(c!==void 0&&c.shapes!==void 0){const u=c.shapes;if(Array.isArray(u))for(let h=0,f=u.length;h<f;h++){const p=u[h];s(e.shapes,p)}else s(e.shapes,u)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const c=[];for(let u=0,h=this.material.length;u<h;u++)c.push(s(e.materials,this.material[u]));i.material=c}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let c=0;c<this.children.length;c++)i.children.push(this.children[c].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let c=0;c<this.animations.length;c++){const u=this.animations[c];i.animations.push(s(e.animations,u))}}if(t){const c=a(e.geometries),u=a(e.materials),h=a(e.textures),f=a(e.images),p=a(e.shapes),m=a(e.skeletons),g=a(e.animations),x=a(e.nodes);c.length>0&&(n.geometries=c),u.length>0&&(n.materials=u),h.length>0&&(n.textures=h),f.length>0&&(n.images=f),p.length>0&&(n.shapes=p),m.length>0&&(n.skeletons=m),g.length>0&&(n.animations=g),x.length>0&&(n.nodes=x)}return n.object=i,n;function a(c){const u=[];for(const h in c){const f=c[h];delete f.metadata,u.push(f)}return u}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}Ht.DEFAULT_UP=new F(0,1,0);Ht.DEFAULT_MATRIX_AUTO_UPDATE=!0;Ht.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const ci=new F,Fi=new F,Iu=new F,Bi=new F,Ds=new F,Ns=new F,Xp=new F,Lu=new F,Du=new F,Nu=new F,Ou=new Et,Uu=new Et,Fu=new Et;class hi{constructor(e=new F,t=new F,n=new F){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),ci.subVectors(e,t),i.cross(ci);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){ci.subVectors(i,t),Fi.subVectors(n,t),Iu.subVectors(e,t);const a=ci.dot(ci),c=ci.dot(Fi),u=ci.dot(Iu),h=Fi.dot(Fi),f=Fi.dot(Iu),p=a*h-c*c;if(p===0)return s.set(0,0,0),null;const m=1/p,g=(h*u-c*f)*m,x=(a*f-c*u)*m;return s.set(1-g-x,x,g)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,Bi)===null?!1:Bi.x>=0&&Bi.y>=0&&Bi.x+Bi.y<=1}static getInterpolation(e,t,n,i,s,a,c,u){return this.getBarycoord(e,t,n,i,Bi)===null?(u.x=0,u.y=0,"z"in u&&(u.z=0),"w"in u&&(u.w=0),null):(u.setScalar(0),u.addScaledVector(s,Bi.x),u.addScaledVector(a,Bi.y),u.addScaledVector(c,Bi.z),u)}static getInterpolatedAttribute(e,t,n,i,s,a){return Ou.setScalar(0),Uu.setScalar(0),Fu.setScalar(0),Ou.fromBufferAttribute(e,t),Uu.fromBufferAttribute(e,n),Fu.fromBufferAttribute(e,i),a.setScalar(0),a.addScaledVector(Ou,s.x),a.addScaledVector(Uu,s.y),a.addScaledVector(Fu,s.z),a}static isFrontFacing(e,t,n,i){return ci.subVectors(n,t),Fi.subVectors(e,t),ci.cross(Fi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return ci.subVectors(this.c,this.b),Fi.subVectors(this.a,this.b),ci.cross(Fi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return hi.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return hi.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return hi.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return hi.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return hi.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let a,c;Ds.subVectors(i,n),Ns.subVectors(s,n),Lu.subVectors(e,n);const u=Ds.dot(Lu),h=Ns.dot(Lu);if(u<=0&&h<=0)return t.copy(n);Du.subVectors(e,i);const f=Ds.dot(Du),p=Ns.dot(Du);if(f>=0&&p<=f)return t.copy(i);const m=u*p-f*h;if(m<=0&&u>=0&&f<=0)return a=u/(u-f),t.copy(n).addScaledVector(Ds,a);Nu.subVectors(e,s);const g=Ds.dot(Nu),x=Ns.dot(Nu);if(x>=0&&g<=x)return t.copy(s);const M=g*h-u*x;if(M<=0&&h>=0&&x<=0)return c=h/(h-x),t.copy(n).addScaledVector(Ns,c);const v=f*x-g*p;if(v<=0&&p-f>=0&&g-x>=0)return Xp.subVectors(s,i),c=(p-f)/(p-f+(g-x)),t.copy(i).addScaledVector(Xp,c);const _=1/(v+M+m);return a=M*_,c=m*_,t.copy(n).addScaledVector(Ds,a).addScaledVector(Ns,c)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Ig={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},or={h:0,s:0,l:0},Za={h:0,s:0,l:0};function Bu(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class Ke{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=dn){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,bt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=bt.workingColorSpace){return this.r=e,this.g=t,this.b=n,bt.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=bt.workingColorSpace){if(e=md(e,1),t=vn(t,0,1),n=vn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=Bu(a,s,e+1/3),this.g=Bu(a,s,e),this.b=Bu(a,s,e-1/3)}return bt.toWorkingColorSpace(this,i),this}setStyle(e,t=dn){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=i[1],c=i[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=dn){const n=Ig[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=ji(e.r),this.g=ji(e.g),this.b=ji(e.b),this}copyLinearToSRGB(e){return this.r=Ys(e.r),this.g=Ys(e.g),this.b=Ys(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=dn){return bt.fromWorkingColorSpace(Tn.copy(this),e),Math.round(vn(Tn.r*255,0,255))*65536+Math.round(vn(Tn.g*255,0,255))*256+Math.round(vn(Tn.b*255,0,255))}getHexString(e=dn){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=bt.workingColorSpace){bt.fromWorkingColorSpace(Tn.copy(this),t);const n=Tn.r,i=Tn.g,s=Tn.b,a=Math.max(n,i,s),c=Math.min(n,i,s);let u,h;const f=(c+a)/2;if(c===a)u=0,h=0;else{const p=a-c;switch(h=f<=.5?p/(a+c):p/(2-a-c),a){case n:u=(i-s)/p+(i<s?6:0);break;case i:u=(s-n)/p+2;break;case s:u=(n-i)/p+4;break}u/=6}return e.h=u,e.s=h,e.l=f,e}getRGB(e,t=bt.workingColorSpace){return bt.fromWorkingColorSpace(Tn.copy(this),t),e.r=Tn.r,e.g=Tn.g,e.b=Tn.b,e}getStyle(e=dn){bt.fromWorkingColorSpace(Tn.copy(this),e);const t=Tn.r,n=Tn.g,i=Tn.b;return e!==dn?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(or),this.setHSL(or.h+e,or.s+t,or.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(or),e.getHSL(Za);const n=Zo(or.h,Za.h,t),i=Zo(or.s,Za.s,t),s=Zo(or.l,Za.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Tn=new Ke;Ke.NAMES=Ig;let wE=0;class xi extends vr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:wE++}),this.uuid=fi(),this.name="",this.blending=Xs,this.side=Xi,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=ph,this.blendDst=mh,this.blendEquation=Jr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ke(0,0,0),this.blendAlpha=0,this.depthFunc=Zs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Rp,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Es,this.stencilZFail=Es,this.stencilZPass=Es,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Xs&&(n.blending=this.blending),this.side!==Xi&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==ph&&(n.blendSrc=this.blendSrc),this.blendDst!==mh&&(n.blendDst=this.blendDst),this.blendEquation!==Jr&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Zs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Rp&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Es&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Es&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Es&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const a=[];for(const c in s){const u=s[c];delete u.metadata,a.push(u)}return a}if(t){const s=i(e.textures),a=i(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class ii extends xi{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new Ke(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new pi,this.combine=ug,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Jt=new F,$a=new Qe;class Qt{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Jh,this.updateRanges=[],this.gpuType=di,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)$a.fromBufferAttribute(this,t),$a.applyMatrix3(e),this.setXY(t,$a.x,$a.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Jt.fromBufferAttribute(this,t),Jt.applyMatrix3(e),this.setXYZ(t,Jt.x,Jt.y,Jt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Jt.fromBufferAttribute(this,t),Jt.applyMatrix4(e),this.setXYZ(t,Jt.x,Jt.y,Jt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Jt.fromBufferAttribute(this,t),Jt.applyNormalMatrix(e),this.setXYZ(t,Jt.x,Jt.y,Jt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Jt.fromBufferAttribute(this,t),Jt.transformDirection(e),this.setXYZ(t,Jt.x,Jt.y,Jt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=ui(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Lt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=ui(t,this.array)),t}setX(e,t){return this.normalized&&(t=Lt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=ui(t,this.array)),t}setY(e,t){return this.normalized&&(t=Lt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=ui(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Lt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=ui(t,this.array)),t}setW(e,t){return this.normalized&&(t=Lt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Lt(t,this.array),n=Lt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=Lt(t,this.array),n=Lt(n,this.array),i=Lt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=Lt(t,this.array),n=Lt(n,this.array),i=Lt(i,this.array),s=Lt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Jh&&(e.usage=this.usage),e}}class Lg extends Qt{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Dg extends Qt{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class jt extends Qt{constructor(e,t,n){super(new Float32Array(e),t,n)}}let PE=0;const ei=new nt,ku=new Ht,Os=new F,Kn=new Yi,Oo=new Yi,hn=new F;class sn extends vr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:PE++}),this.uuid=fi(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Pg(e)?Dg:Lg)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new ut().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return ei.makeRotationFromQuaternion(e),this.applyMatrix4(ei),this}rotateX(e){return ei.makeRotationX(e),this.applyMatrix4(ei),this}rotateY(e){return ei.makeRotationY(e),this.applyMatrix4(ei),this}rotateZ(e){return ei.makeRotationZ(e),this.applyMatrix4(ei),this}translate(e,t,n){return ei.makeTranslation(e,t,n),this.applyMatrix4(ei),this}scale(e,t,n){return ei.makeScale(e,t,n),this.applyMatrix4(ei),this}lookAt(e){return ku.lookAt(e),ku.updateMatrix(),this.applyMatrix4(ku.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Os).negate(),this.translate(Os.x,Os.y,Os.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let i=0,s=e.length;i<s;i++){const a=e[i];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new jt(n,3))}else{for(let n=0,i=t.count;n<i;n++){const s=e[n];t.setXYZ(n,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Yi);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new F(-1/0,-1/0,-1/0),new F(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];Kn.setFromBufferAttribute(s),this.morphTargetsRelative?(hn.addVectors(this.boundingBox.min,Kn.min),this.boundingBox.expandByPoint(hn),hn.addVectors(this.boundingBox.max,Kn.max),this.boundingBox.expandByPoint(hn)):(this.boundingBox.expandByPoint(Kn.min),this.boundingBox.expandByPoint(Kn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new bi);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new F,1/0);return}if(e){const n=this.boundingSphere.center;if(Kn.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const c=t[s];Oo.setFromBufferAttribute(c),this.morphTargetsRelative?(hn.addVectors(Kn.min,Oo.min),Kn.expandByPoint(hn),hn.addVectors(Kn.max,Oo.max),Kn.expandByPoint(hn)):(Kn.expandByPoint(Oo.min),Kn.expandByPoint(Oo.max))}Kn.getCenter(n);let i=0;for(let s=0,a=e.count;s<a;s++)hn.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(hn));if(t)for(let s=0,a=t.length;s<a;s++){const c=t[s],u=this.morphTargetsRelative;for(let h=0,f=c.count;h<f;h++)hn.fromBufferAttribute(c,h),u&&(Os.fromBufferAttribute(e,h),hn.add(Os)),i=Math.max(i,n.distanceToSquared(hn))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Qt(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),c=[],u=[];for(let z=0;z<n.count;z++)c[z]=new F,u[z]=new F;const h=new F,f=new F,p=new F,m=new Qe,g=new Qe,x=new Qe,M=new F,v=new F;function _(z,I,w){h.fromBufferAttribute(n,z),f.fromBufferAttribute(n,I),p.fromBufferAttribute(n,w),m.fromBufferAttribute(s,z),g.fromBufferAttribute(s,I),x.fromBufferAttribute(s,w),f.sub(h),p.sub(h),g.sub(m),x.sub(m);const H=1/(g.x*x.y-x.x*g.y);isFinite(H)&&(M.copy(f).multiplyScalar(x.y).addScaledVector(p,-g.y).multiplyScalar(H),v.copy(p).multiplyScalar(g.x).addScaledVector(f,-x.x).multiplyScalar(H),c[z].add(M),c[I].add(M),c[w].add(M),u[z].add(v),u[I].add(v),u[w].add(v))}let A=this.groups;A.length===0&&(A=[{start:0,count:e.count}]);for(let z=0,I=A.length;z<I;++z){const w=A[z],H=w.start,ee=w.count;for(let J=H,oe=H+ee;J<oe;J+=3)_(e.getX(J+0),e.getX(J+1),e.getX(J+2))}const P=new F,S=new F,k=new F,O=new F;function U(z){k.fromBufferAttribute(i,z),O.copy(k);const I=c[z];P.copy(I),P.sub(k.multiplyScalar(k.dot(I))).normalize(),S.crossVectors(O,I);const H=S.dot(u[z])<0?-1:1;a.setXYZW(z,P.x,P.y,P.z,H)}for(let z=0,I=A.length;z<I;++z){const w=A[z],H=w.start,ee=w.count;for(let J=H,oe=H+ee;J<oe;J+=3)U(e.getX(J+0)),U(e.getX(J+1)),U(e.getX(J+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Qt(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let m=0,g=n.count;m<g;m++)n.setXYZ(m,0,0,0);const i=new F,s=new F,a=new F,c=new F,u=new F,h=new F,f=new F,p=new F;if(e)for(let m=0,g=e.count;m<g;m+=3){const x=e.getX(m+0),M=e.getX(m+1),v=e.getX(m+2);i.fromBufferAttribute(t,x),s.fromBufferAttribute(t,M),a.fromBufferAttribute(t,v),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),c.fromBufferAttribute(n,x),u.fromBufferAttribute(n,M),h.fromBufferAttribute(n,v),c.add(f),u.add(f),h.add(f),n.setXYZ(x,c.x,c.y,c.z),n.setXYZ(M,u.x,u.y,u.z),n.setXYZ(v,h.x,h.y,h.z)}else for(let m=0,g=t.count;m<g;m+=3)i.fromBufferAttribute(t,m+0),s.fromBufferAttribute(t,m+1),a.fromBufferAttribute(t,m+2),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),n.setXYZ(m+0,f.x,f.y,f.z),n.setXYZ(m+1,f.x,f.y,f.z),n.setXYZ(m+2,f.x,f.y,f.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)hn.fromBufferAttribute(e,t),hn.normalize(),e.setXYZ(t,hn.x,hn.y,hn.z)}toNonIndexed(){function e(c,u){const h=c.array,f=c.itemSize,p=c.normalized,m=new h.constructor(u.length*f);let g=0,x=0;for(let M=0,v=u.length;M<v;M++){c.isInterleavedBufferAttribute?g=u[M]*c.data.stride+c.offset:g=u[M]*f;for(let _=0;_<f;_++)m[x++]=h[g++]}return new Qt(m,f,p)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new sn,n=this.index.array,i=this.attributes;for(const c in i){const u=i[c],h=e(u,n);t.setAttribute(c,h)}const s=this.morphAttributes;for(const c in s){const u=[],h=s[c];for(let f=0,p=h.length;f<p;f++){const m=h[f],g=e(m,n);u.push(g)}t.morphAttributes[c]=u}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];t.addGroup(h.start,h.count,h.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const u=this.parameters;for(const h in u)u[h]!==void 0&&(e[h]=u[h]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const u in n){const h=n[u];e.data.attributes[u]=h.toJSON(e.data)}const i={};let s=!1;for(const u in this.morphAttributes){const h=this.morphAttributes[u],f=[];for(let p=0,m=h.length;p<m;p++){const g=h[p];f.push(g.toJSON(e.data))}f.length>0&&(i[u]=f,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const c=this.boundingSphere;return c!==null&&(e.data.boundingSphere={center:c.center.toArray(),radius:c.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const h in i){const f=i[h];this.setAttribute(h,f.clone(t))}const s=e.morphAttributes;for(const h in s){const f=[],p=s[h];for(let m=0,g=p.length;m<g;m++)f.push(p[m].clone(t));this.morphAttributes[h]=f}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let h=0,f=a.length;h<f;h++){const p=a[h];this.addGroup(p.start,p.count,p.materialIndex)}const c=e.boundingBox;c!==null&&(this.boundingBox=c.clone());const u=e.boundingSphere;return u!==null&&(this.boundingSphere=u.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const qp=new nt,Wr=new oo,Ja=new bi,Yp=new F,Qa=new F,ec=new F,tc=new F,zu=new F,nc=new F,Kp=new F,ic=new F;class we extends Ht{constructor(e=new sn,t=new ii){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const c=this.morphTargetInfluences;if(s&&c){nc.set(0,0,0);for(let u=0,h=s.length;u<h;u++){const f=c[u],p=s[u];f!==0&&(zu.fromBufferAttribute(p,e),a?nc.addScaledVector(zu,f):nc.addScaledVector(zu.sub(t),f))}t.add(nc)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Ja.copy(n.boundingSphere),Ja.applyMatrix4(s),Wr.copy(e.ray).recast(e.near),!(Ja.containsPoint(Wr.origin)===!1&&(Wr.intersectSphere(Ja,Yp)===null||Wr.origin.distanceToSquared(Yp)>(e.far-e.near)**2))&&(qp.copy(s).invert(),Wr.copy(e.ray).applyMatrix4(qp),!(n.boundingBox!==null&&Wr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Wr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,a=this.material,c=s.index,u=s.attributes.position,h=s.attributes.uv,f=s.attributes.uv1,p=s.attributes.normal,m=s.groups,g=s.drawRange;if(c!==null)if(Array.isArray(a))for(let x=0,M=m.length;x<M;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),P=Math.min(c.count,Math.min(v.start+v.count,g.start+g.count));for(let S=A,k=P;S<k;S+=3){const O=c.getX(S),U=c.getX(S+1),z=c.getX(S+2);i=rc(this,_,e,n,h,f,p,O,U,z),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),M=Math.min(c.count,g.start+g.count);for(let v=x,_=M;v<_;v+=3){const A=c.getX(v),P=c.getX(v+1),S=c.getX(v+2);i=rc(this,a,e,n,h,f,p,A,P,S),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}else if(u!==void 0)if(Array.isArray(a))for(let x=0,M=m.length;x<M;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),P=Math.min(u.count,Math.min(v.start+v.count,g.start+g.count));for(let S=A,k=P;S<k;S+=3){const O=S,U=S+1,z=S+2;i=rc(this,_,e,n,h,f,p,O,U,z),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),M=Math.min(u.count,g.start+g.count);for(let v=x,_=M;v<_;v+=3){const A=v,P=v+1,S=v+2;i=rc(this,a,e,n,h,f,p,A,P,S),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}}}function RE(r,e,t,n,i,s,a,c){let u;if(e.side===Bn?u=n.intersectTriangle(a,s,i,!0,c):u=n.intersectTriangle(i,s,a,e.side===Xi,c),u===null)return null;ic.copy(c),ic.applyMatrix4(r.matrixWorld);const h=t.ray.origin.distanceTo(ic);return h<t.near||h>t.far?null:{distance:h,point:ic.clone(),object:r}}function rc(r,e,t,n,i,s,a,c,u,h){r.getVertexPosition(c,Qa),r.getVertexPosition(u,ec),r.getVertexPosition(h,tc);const f=RE(r,e,t,n,Qa,ec,tc,Kp);if(f){const p=new F;hi.getBarycoord(Kp,Qa,ec,tc,p),i&&(f.uv=hi.getInterpolatedAttribute(i,c,u,h,p,new Qe)),s&&(f.uv1=hi.getInterpolatedAttribute(s,c,u,h,p,new Qe)),a&&(f.normal=hi.getInterpolatedAttribute(a,c,u,h,p,new F),f.normal.dot(n.direction)>0&&f.normal.multiplyScalar(-1));const m={a:c,b:u,c:h,normal:new F,materialIndex:0};hi.getNormal(Qa,ec,tc,m.normal),f.face=m,f.barycoord=p}return f}class Yt extends sn{constructor(e=1,t=1,n=1,i=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:a};const c=this;i=Math.floor(i),s=Math.floor(s),a=Math.floor(a);const u=[],h=[],f=[],p=[];let m=0,g=0;x("z","y","x",-1,-1,n,t,e,a,s,0),x("z","y","x",1,-1,n,t,-e,a,s,1),x("x","z","y",1,1,e,n,t,i,a,2),x("x","z","y",1,-1,e,n,-t,i,a,3),x("x","y","z",1,-1,e,t,n,i,s,4),x("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(u),this.setAttribute("position",new jt(h,3)),this.setAttribute("normal",new jt(f,3)),this.setAttribute("uv",new jt(p,2));function x(M,v,_,A,P,S,k,O,U,z,I){const w=S/U,H=k/z,ee=S/2,J=k/2,oe=O/2,ce=U+1,$=z+1;let le=0,ne=0;const ge=new F;for(let Te=0;Te<$;Te++){const Oe=Te*H-J;for(let Ye=0;Ye<ce;Ye++){const yt=Ye*w-ee;ge[M]=yt*A,ge[v]=Oe*P,ge[_]=oe,h.push(ge.x,ge.y,ge.z),ge[M]=0,ge[v]=0,ge[_]=O>0?1:-1,f.push(ge.x,ge.y,ge.z),p.push(Ye/U),p.push(1-Te/z),le+=1}}for(let Te=0;Te<z;Te++)for(let Oe=0;Oe<U;Oe++){const Ye=m+Oe+ce*Te,yt=m+Oe+ce*(Te+1),he=m+(Oe+1)+ce*(Te+1),me=m+(Oe+1)+ce*Te;u.push(Ye,yt,me),u.push(yt,he,me),ne+=6}c.addGroup(g,ne,I),g+=ne,m+=le}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Yt(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function io(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Rn(r){const e={};for(let t=0;t<r.length;t++){const n=io(r[t]);for(const i in n)e[i]=n[i]}return e}function CE(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function Ng(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:bt.workingColorSpace}const IE={clone:io,merge:Rn};var LE=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,DE=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class _r extends xi{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=LE,this.fragmentShader=DE,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=io(e.uniforms),this.uniformsGroups=CE(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Og extends Ht{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new nt,this.projectionMatrix=new nt,this.projectionMatrixInverse=new nt,this.coordinateSystem=Gi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ar=new F,Zp=new Qe,$p=new Qe;class Cn extends Og{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=no*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Ko*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return no*2*Math.atan(Math.tan(Ko*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){ar.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(ar.x,ar.y).multiplyScalar(-e/ar.z),ar.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ar.x,ar.y).multiplyScalar(-e/ar.z)}getViewSize(e,t){return this.getViewBounds(e,Zp,$p),t.subVectors($p,Zp)}setViewOffset(e,t,n,i,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Ko*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const u=a.fullWidth,h=a.fullHeight;s+=a.offsetX*i/u,t-=a.offsetY*n/h,i*=a.width/u,n*=a.height/h}const c=this.filmOffset;c!==0&&(s+=e*c/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Us=-90,Fs=1;class NE extends Ht{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new Cn(Us,Fs,e,t);i.layers=this.layers,this.add(i);const s=new Cn(Us,Fs,e,t);s.layers=this.layers,this.add(s);const a=new Cn(Us,Fs,e,t);a.layers=this.layers,this.add(a);const c=new Cn(Us,Fs,e,t);c.layers=this.layers,this.add(c);const u=new Cn(Us,Fs,e,t);u.layers=this.layers,this.add(u);const h=new Cn(Us,Fs,e,t);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,a,c,u]=t;for(const h of t)this.remove(h);if(e===Gi)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),c.up.set(0,1,0),c.lookAt(0,0,1),u.up.set(0,1,0),u.lookAt(0,0,-1);else if(e===Dc)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),c.up.set(0,-1,0),c.lookAt(0,0,1),u.up.set(0,-1,0),u.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const h of t)this.add(h),h.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,c,u,h,f]=this.children,p=e.getRenderTarget(),m=e.getActiveCubeFace(),g=e.getActiveMipmapLevel(),x=e.xr.enabled;e.xr.enabled=!1;const M=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,c),e.setRenderTarget(n,3,i),e.render(t,u),e.setRenderTarget(n,4,i),e.render(t,h),n.texture.generateMipmaps=M,e.setRenderTarget(n,5,i),e.render(t,f),e.setRenderTarget(p,m,g),e.xr.enabled=x,n.texture.needsPMREMUpdate=!0}}class Ug extends fn{constructor(e,t,n,i,s,a,c,u,h,f){e=e!==void 0?e:[],t=t!==void 0?t:$s,super(e,t,n,i,s,a,c,u,h,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class OE extends ns{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Ug(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:Zn}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},i=new Yt(5,5,5),s=new _r({name:"CubemapFromEquirect",uniforms:io(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Bn,blending:mr});s.uniforms.tEquirect.value=t;const a=new we(i,s),c=t.minFilter;return t.minFilter===Vi&&(t.minFilter=Zn),new NE(1,10,this).update(e,a),t.minFilter=c,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(s)}}const Hu=new F,UE=new F,FE=new ut;class hr{constructor(e=new F(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=Hu.subVectors(n,t).cross(UE.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Hu),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||FE.getNormalMatrix(e),i=this.coplanarPoint(Hu).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const jr=new bi,sc=new F;class _d{constructor(e=new hr,t=new hr,n=new hr,i=new hr,s=new hr,a=new hr){this.planes=[e,t,n,i,s,a]}set(e,t,n,i,s,a){const c=this.planes;return c[0].copy(e),c[1].copy(t),c[2].copy(n),c[3].copy(i),c[4].copy(s),c[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Gi){const n=this.planes,i=e.elements,s=i[0],a=i[1],c=i[2],u=i[3],h=i[4],f=i[5],p=i[6],m=i[7],g=i[8],x=i[9],M=i[10],v=i[11],_=i[12],A=i[13],P=i[14],S=i[15];if(n[0].setComponents(u-s,m-h,v-g,S-_).normalize(),n[1].setComponents(u+s,m+h,v+g,S+_).normalize(),n[2].setComponents(u+a,m+f,v+x,S+A).normalize(),n[3].setComponents(u-a,m-f,v-x,S-A).normalize(),n[4].setComponents(u-c,m-p,v-M,S-P).normalize(),t===Gi)n[5].setComponents(u+c,m+p,v+M,S+P).normalize();else if(t===Dc)n[5].setComponents(c,p,M,P).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),jr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),jr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(jr)}intersectsSprite(e){return jr.center.set(0,0,0),jr.radius=.7071067811865476,jr.applyMatrix4(e.matrixWorld),this.intersectsSphere(jr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(sc.x=i.normal.x>0?e.max.x:e.min.x,sc.y=i.normal.y>0?e.max.y:e.min.y,sc.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(sc)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Fg(){let r=null,e=!1,t=null,n=null;function i(s,a){t(s,a),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function BE(r){const e=new WeakMap;function t(c,u){const h=c.array,f=c.usage,p=h.byteLength,m=r.createBuffer();r.bindBuffer(u,m),r.bufferData(u,h,f),c.onUploadCallback();let g;if(h instanceof Float32Array)g=r.FLOAT;else if(h instanceof Uint16Array)c.isFloat16BufferAttribute?g=r.HALF_FLOAT:g=r.UNSIGNED_SHORT;else if(h instanceof Int16Array)g=r.SHORT;else if(h instanceof Uint32Array)g=r.UNSIGNED_INT;else if(h instanceof Int32Array)g=r.INT;else if(h instanceof Int8Array)g=r.BYTE;else if(h instanceof Uint8Array)g=r.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)g=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:m,type:g,bytesPerElement:h.BYTES_PER_ELEMENT,version:c.version,size:p}}function n(c,u,h){const f=u.array,p=u.updateRanges;if(r.bindBuffer(h,c),p.length===0)r.bufferSubData(h,0,f);else{p.sort((g,x)=>g.start-x.start);let m=0;for(let g=1;g<p.length;g++){const x=p[m],M=p[g];M.start<=x.start+x.count+1?x.count=Math.max(x.count,M.start+M.count-x.start):(++m,p[m]=M)}p.length=m+1;for(let g=0,x=p.length;g<x;g++){const M=p[g];r.bufferSubData(h,M.start*f.BYTES_PER_ELEMENT,f,M.start,M.count)}u.clearUpdateRanges()}u.onUploadCallback()}function i(c){return c.isInterleavedBufferAttribute&&(c=c.data),e.get(c)}function s(c){c.isInterleavedBufferAttribute&&(c=c.data);const u=e.get(c);u&&(r.deleteBuffer(u.buffer),e.delete(c))}function a(c,u){if(c.isInterleavedBufferAttribute&&(c=c.data),c.isGLBufferAttribute){const f=e.get(c);(!f||f.version<c.version)&&e.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}const h=e.get(c);if(h===void 0)e.set(c,t(c,u));else if(h.version<c.version){if(h.size!==c.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(h.buffer,c,u),h.version=c.version}}return{get:i,remove:s,update:a}}class ao extends sn{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,a=t/2,c=Math.floor(n),u=Math.floor(i),h=c+1,f=u+1,p=e/c,m=t/u,g=[],x=[],M=[],v=[];for(let _=0;_<f;_++){const A=_*m-a;for(let P=0;P<h;P++){const S=P*p-s;x.push(S,-A,0),M.push(0,0,1),v.push(P/c),v.push(1-_/u)}}for(let _=0;_<u;_++)for(let A=0;A<c;A++){const P=A+h*_,S=A+h*(_+1),k=A+1+h*(_+1),O=A+1+h*_;g.push(P,S,O),g.push(S,k,O)}this.setIndex(g),this.setAttribute("position",new jt(x,3)),this.setAttribute("normal",new jt(M,3)),this.setAttribute("uv",new jt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ao(e.width,e.height,e.widthSegments,e.heightSegments)}}var kE=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,zE=`#ifdef USE_ALPHAHASH
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
#endif`,HE=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,VE=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,GE=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,WE=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,jE=`#ifdef USE_AOMAP
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
#endif`,XE=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,qE=`#ifdef USE_BATCHING
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
#endif`,YE=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,KE=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,ZE=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,$E=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,JE=`#ifdef USE_IRIDESCENCE
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
#endif`,QE=`#ifdef USE_BUMPMAP
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
#endif`,eA=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,tA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,nA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,iA=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,rA=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,sA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,oA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,aA=`#if defined( USE_COLOR_ALPHA )
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
#endif`,cA=`#define PI 3.141592653589793
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
} // validated`,lA=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,uA=`vec3 transformedNormal = objectNormal;
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
#endif`,hA=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,dA=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,fA=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,pA=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,mA="gl_FragColor = linearToOutputTexel( gl_FragColor );",gA=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,_A=`#ifdef USE_ENVMAP
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
#endif`,vA=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,yA=`#ifdef USE_ENVMAP
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
#endif`,xA=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,bA=`#ifdef USE_ENVMAP
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
#endif`,SA=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,MA=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,TA=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,EA=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,AA=`#ifdef USE_GRADIENTMAP
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
}`,wA=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,PA=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,RA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,CA=`uniform bool receiveShadow;
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
#endif`,IA=`#ifdef USE_ENVMAP
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
#endif`,LA=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,DA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,NA=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,OA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,UA=`PhysicalMaterial material;
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
#endif`,FA=`struct PhysicalMaterial {
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
}`,BA=`
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
#endif`,kA=`#if defined( RE_IndirectDiffuse )
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
#endif`,zA=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,HA=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,VA=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,GA=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,WA=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,jA=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,XA=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,qA=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,YA=`#if defined( USE_POINTS_UV )
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
#endif`,KA=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,ZA=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,$A=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,JA=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,QA=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,ew=`#ifdef USE_MORPHTARGETS
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
#endif`,tw=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,nw=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,iw=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,rw=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,sw=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,ow=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,aw=`#ifdef USE_NORMALMAP
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
#endif`,cw=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,lw=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,uw=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,hw=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,dw=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,fw=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,pw=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,mw=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,gw=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,_w=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,vw=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,yw=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,xw=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,bw=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Sw=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,Mw=`float getShadowMask() {
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
}`,Tw=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,Ew=`#ifdef USE_SKINNING
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
#endif`,Aw=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,ww=`#ifdef USE_SKINNING
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
#endif`,Pw=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,Rw=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Cw=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,Iw=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,Lw=`#ifdef USE_TRANSMISSION
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
#endif`,Dw=`#ifdef USE_TRANSMISSION
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
#endif`,Nw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Ow=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Uw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Fw=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const Bw=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,kw=`uniform sampler2D t2D;
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
}`,zw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Hw=`#ifdef ENVMAP_TYPE_CUBE
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
}`,Vw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Gw=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ww=`#include <common>
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
}`,jw=`#if DEPTH_PACKING == 3200
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
}`,Xw=`#define DISTANCE
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
}`,qw=`#define DISTANCE
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
}`,Yw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Kw=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Zw=`uniform float scale;
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
}`,$w=`uniform vec3 diffuse;
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
}`,Jw=`#include <common>
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
}`,Qw=`uniform vec3 diffuse;
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
}`,e1=`#define LAMBERT
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
}`,t1=`#define LAMBERT
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
}`,n1=`#define MATCAP
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
}`,i1=`#define MATCAP
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
}`,r1=`#define NORMAL
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
}`,s1=`#define NORMAL
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
}`,o1=`#define PHONG
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
}`,a1=`#define PHONG
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
}`,c1=`#define STANDARD
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
}`,l1=`#define STANDARD
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
}`,u1=`#define TOON
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
}`,h1=`#define TOON
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
}`,d1=`uniform float size;
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
}`,f1=`uniform vec3 diffuse;
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
}`,p1=`#include <common>
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
}`,m1=`uniform vec3 color;
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
}`,g1=`uniform float rotation;
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
}`,_1=`uniform vec3 diffuse;
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
}`,ft={alphahash_fragment:kE,alphahash_pars_fragment:zE,alphamap_fragment:HE,alphamap_pars_fragment:VE,alphatest_fragment:GE,alphatest_pars_fragment:WE,aomap_fragment:jE,aomap_pars_fragment:XE,batching_pars_vertex:qE,batching_vertex:YE,begin_vertex:KE,beginnormal_vertex:ZE,bsdfs:$E,iridescence_fragment:JE,bumpmap_pars_fragment:QE,clipping_planes_fragment:eA,clipping_planes_pars_fragment:tA,clipping_planes_pars_vertex:nA,clipping_planes_vertex:iA,color_fragment:rA,color_pars_fragment:sA,color_pars_vertex:oA,color_vertex:aA,common:cA,cube_uv_reflection_fragment:lA,defaultnormal_vertex:uA,displacementmap_pars_vertex:hA,displacementmap_vertex:dA,emissivemap_fragment:fA,emissivemap_pars_fragment:pA,colorspace_fragment:mA,colorspace_pars_fragment:gA,envmap_fragment:_A,envmap_common_pars_fragment:vA,envmap_pars_fragment:yA,envmap_pars_vertex:xA,envmap_physical_pars_fragment:IA,envmap_vertex:bA,fog_vertex:SA,fog_pars_vertex:MA,fog_fragment:TA,fog_pars_fragment:EA,gradientmap_pars_fragment:AA,lightmap_pars_fragment:wA,lights_lambert_fragment:PA,lights_lambert_pars_fragment:RA,lights_pars_begin:CA,lights_toon_fragment:LA,lights_toon_pars_fragment:DA,lights_phong_fragment:NA,lights_phong_pars_fragment:OA,lights_physical_fragment:UA,lights_physical_pars_fragment:FA,lights_fragment_begin:BA,lights_fragment_maps:kA,lights_fragment_end:zA,logdepthbuf_fragment:HA,logdepthbuf_pars_fragment:VA,logdepthbuf_pars_vertex:GA,logdepthbuf_vertex:WA,map_fragment:jA,map_pars_fragment:XA,map_particle_fragment:qA,map_particle_pars_fragment:YA,metalnessmap_fragment:KA,metalnessmap_pars_fragment:ZA,morphinstance_vertex:$A,morphcolor_vertex:JA,morphnormal_vertex:QA,morphtarget_pars_vertex:ew,morphtarget_vertex:tw,normal_fragment_begin:nw,normal_fragment_maps:iw,normal_pars_fragment:rw,normal_pars_vertex:sw,normal_vertex:ow,normalmap_pars_fragment:aw,clearcoat_normal_fragment_begin:cw,clearcoat_normal_fragment_maps:lw,clearcoat_pars_fragment:uw,iridescence_pars_fragment:hw,opaque_fragment:dw,packing:fw,premultiplied_alpha_fragment:pw,project_vertex:mw,dithering_fragment:gw,dithering_pars_fragment:_w,roughnessmap_fragment:vw,roughnessmap_pars_fragment:yw,shadowmap_pars_fragment:xw,shadowmap_pars_vertex:bw,shadowmap_vertex:Sw,shadowmask_pars_fragment:Mw,skinbase_vertex:Tw,skinning_pars_vertex:Ew,skinning_vertex:Aw,skinnormal_vertex:ww,specularmap_fragment:Pw,specularmap_pars_fragment:Rw,tonemapping_fragment:Cw,tonemapping_pars_fragment:Iw,transmission_fragment:Lw,transmission_pars_fragment:Dw,uv_pars_fragment:Nw,uv_pars_vertex:Ow,uv_vertex:Uw,worldpos_vertex:Fw,background_vert:Bw,background_frag:kw,backgroundCube_vert:zw,backgroundCube_frag:Hw,cube_vert:Vw,cube_frag:Gw,depth_vert:Ww,depth_frag:jw,distanceRGBA_vert:Xw,distanceRGBA_frag:qw,equirect_vert:Yw,equirect_frag:Kw,linedashed_vert:Zw,linedashed_frag:$w,meshbasic_vert:Jw,meshbasic_frag:Qw,meshlambert_vert:e1,meshlambert_frag:t1,meshmatcap_vert:n1,meshmatcap_frag:i1,meshnormal_vert:r1,meshnormal_frag:s1,meshphong_vert:o1,meshphong_frag:a1,meshphysical_vert:c1,meshphysical_frag:l1,meshtoon_vert:u1,meshtoon_frag:h1,points_vert:d1,points_frag:f1,shadow_vert:p1,shadow_frag:m1,sprite_vert:g1,sprite_frag:_1},Ie={common:{diffuse:{value:new Ke(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ut},alphaMap:{value:null},alphaMapTransform:{value:new ut},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ut}},envmap:{envMap:{value:null},envMapRotation:{value:new ut},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ut}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ut}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ut},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ut},normalScale:{value:new Qe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ut},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ut}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ut}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ut}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ke(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Ke(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ut},alphaTest:{value:0},uvTransform:{value:new ut}},sprite:{diffuse:{value:new Ke(16777215)},opacity:{value:1},center:{value:new Qe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ut},alphaMap:{value:null},alphaMapTransform:{value:new ut},alphaTest:{value:0}}},vi={basic:{uniforms:Rn([Ie.common,Ie.specularmap,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.fog]),vertexShader:ft.meshbasic_vert,fragmentShader:ft.meshbasic_frag},lambert:{uniforms:Rn([Ie.common,Ie.specularmap,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.fog,Ie.lights,{emissive:{value:new Ke(0)}}]),vertexShader:ft.meshlambert_vert,fragmentShader:ft.meshlambert_frag},phong:{uniforms:Rn([Ie.common,Ie.specularmap,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.fog,Ie.lights,{emissive:{value:new Ke(0)},specular:{value:new Ke(1118481)},shininess:{value:30}}]),vertexShader:ft.meshphong_vert,fragmentShader:ft.meshphong_frag},standard:{uniforms:Rn([Ie.common,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.roughnessmap,Ie.metalnessmap,Ie.fog,Ie.lights,{emissive:{value:new Ke(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:ft.meshphysical_vert,fragmentShader:ft.meshphysical_frag},toon:{uniforms:Rn([Ie.common,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.gradientmap,Ie.fog,Ie.lights,{emissive:{value:new Ke(0)}}]),vertexShader:ft.meshtoon_vert,fragmentShader:ft.meshtoon_frag},matcap:{uniforms:Rn([Ie.common,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.fog,{matcap:{value:null}}]),vertexShader:ft.meshmatcap_vert,fragmentShader:ft.meshmatcap_frag},points:{uniforms:Rn([Ie.points,Ie.fog]),vertexShader:ft.points_vert,fragmentShader:ft.points_frag},dashed:{uniforms:Rn([Ie.common,Ie.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:ft.linedashed_vert,fragmentShader:ft.linedashed_frag},depth:{uniforms:Rn([Ie.common,Ie.displacementmap]),vertexShader:ft.depth_vert,fragmentShader:ft.depth_frag},normal:{uniforms:Rn([Ie.common,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,{opacity:{value:1}}]),vertexShader:ft.meshnormal_vert,fragmentShader:ft.meshnormal_frag},sprite:{uniforms:Rn([Ie.sprite,Ie.fog]),vertexShader:ft.sprite_vert,fragmentShader:ft.sprite_frag},background:{uniforms:{uvTransform:{value:new ut},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:ft.background_vert,fragmentShader:ft.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ut}},vertexShader:ft.backgroundCube_vert,fragmentShader:ft.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:ft.cube_vert,fragmentShader:ft.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:ft.equirect_vert,fragmentShader:ft.equirect_frag},distanceRGBA:{uniforms:Rn([Ie.common,Ie.displacementmap,{referencePosition:{value:new F},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:ft.distanceRGBA_vert,fragmentShader:ft.distanceRGBA_frag},shadow:{uniforms:Rn([Ie.lights,Ie.fog,{color:{value:new Ke(0)},opacity:{value:1}}]),vertexShader:ft.shadow_vert,fragmentShader:ft.shadow_frag}};vi.physical={uniforms:Rn([vi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ut},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ut},clearcoatNormalScale:{value:new Qe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ut},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ut},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ut},sheen:{value:0},sheenColor:{value:new Ke(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ut},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ut},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ut},transmissionSamplerSize:{value:new Qe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ut},attenuationDistance:{value:0},attenuationColor:{value:new Ke(0)},specularColor:{value:new Ke(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ut},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ut},anisotropyVector:{value:new Qe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ut}}]),vertexShader:ft.meshphysical_vert,fragmentShader:ft.meshphysical_frag};const oc={r:0,b:0,g:0},Xr=new pi,v1=new nt;function y1(r,e,t,n,i,s,a){const c=new Ke(0);let u=s===!0?0:1,h,f,p=null,m=0,g=null;function x(A){let P=A.isScene===!0?A.background:null;return P&&P.isTexture&&(P=(A.backgroundBlurriness>0?t:e).get(P)),P}function M(A){let P=!1;const S=x(A);S===null?_(c,u):S&&S.isColor&&(_(S,1),P=!0);const k=r.xr.getEnvironmentBlendMode();k==="additive"?n.buffers.color.setClear(0,0,0,1,a):k==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(r.autoClear||P)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function v(A,P){const S=x(P);S&&(S.isCubeTexture||S.mapping===Fc)?(f===void 0&&(f=new we(new Yt(1,1,1),new _r({name:"BackgroundCubeMaterial",uniforms:io(vi.backgroundCube.uniforms),vertexShader:vi.backgroundCube.vertexShader,fragmentShader:vi.backgroundCube.fragmentShader,side:Bn,depthTest:!1,depthWrite:!1,fog:!1})),f.geometry.deleteAttribute("normal"),f.geometry.deleteAttribute("uv"),f.onBeforeRender=function(k,O,U){this.matrixWorld.copyPosition(U.matrixWorld)},Object.defineProperty(f.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(f)),Xr.copy(P.backgroundRotation),Xr.x*=-1,Xr.y*=-1,Xr.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(Xr.y*=-1,Xr.z*=-1),f.material.uniforms.envMap.value=S,f.material.uniforms.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,f.material.uniforms.backgroundBlurriness.value=P.backgroundBlurriness,f.material.uniforms.backgroundIntensity.value=P.backgroundIntensity,f.material.uniforms.backgroundRotation.value.setFromMatrix4(v1.makeRotationFromEuler(Xr)),f.material.toneMapped=bt.getTransfer(S.colorSpace)!==Dt,(p!==S||m!==S.version||g!==r.toneMapping)&&(f.material.needsUpdate=!0,p=S,m=S.version,g=r.toneMapping),f.layers.enableAll(),A.unshift(f,f.geometry,f.material,0,0,null)):S&&S.isTexture&&(h===void 0&&(h=new we(new ao(2,2),new _r({name:"BackgroundMaterial",uniforms:io(vi.background.uniforms),vertexShader:vi.background.vertexShader,fragmentShader:vi.background.fragmentShader,side:Xi,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),Object.defineProperty(h.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(h)),h.material.uniforms.t2D.value=S,h.material.uniforms.backgroundIntensity.value=P.backgroundIntensity,h.material.toneMapped=bt.getTransfer(S.colorSpace)!==Dt,S.matrixAutoUpdate===!0&&S.updateMatrix(),h.material.uniforms.uvTransform.value.copy(S.matrix),(p!==S||m!==S.version||g!==r.toneMapping)&&(h.material.needsUpdate=!0,p=S,m=S.version,g=r.toneMapping),h.layers.enableAll(),A.unshift(h,h.geometry,h.material,0,0,null))}function _(A,P){A.getRGB(oc,Ng(r)),n.buffers.color.setClear(oc.r,oc.g,oc.b,P,a)}return{getClearColor:function(){return c},setClearColor:function(A,P=1){c.set(A),u=P,_(c,u)},getClearAlpha:function(){return u},setClearAlpha:function(A){u=A,_(c,u)},render:M,addToRenderList:v}}function x1(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=m(null);let s=i,a=!1;function c(w,H,ee,J,oe){let ce=!1;const $=p(J,ee,H);s!==$&&(s=$,h(s.object)),ce=g(w,J,ee,oe),ce&&x(w,J,ee,oe),oe!==null&&e.update(oe,r.ELEMENT_ARRAY_BUFFER),(ce||a)&&(a=!1,S(w,H,ee,J),oe!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(oe).buffer))}function u(){return r.createVertexArray()}function h(w){return r.bindVertexArray(w)}function f(w){return r.deleteVertexArray(w)}function p(w,H,ee){const J=ee.wireframe===!0;let oe=n[w.id];oe===void 0&&(oe={},n[w.id]=oe);let ce=oe[H.id];ce===void 0&&(ce={},oe[H.id]=ce);let $=ce[J];return $===void 0&&($=m(u()),ce[J]=$),$}function m(w){const H=[],ee=[],J=[];for(let oe=0;oe<t;oe++)H[oe]=0,ee[oe]=0,J[oe]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ee,attributeDivisors:J,object:w,attributes:{},index:null}}function g(w,H,ee,J){const oe=s.attributes,ce=H.attributes;let $=0;const le=ee.getAttributes();for(const ne in le)if(le[ne].location>=0){const Te=oe[ne];let Oe=ce[ne];if(Oe===void 0&&(ne==="instanceMatrix"&&w.instanceMatrix&&(Oe=w.instanceMatrix),ne==="instanceColor"&&w.instanceColor&&(Oe=w.instanceColor)),Te===void 0||Te.attribute!==Oe||Oe&&Te.data!==Oe.data)return!0;$++}return s.attributesNum!==$||s.index!==J}function x(w,H,ee,J){const oe={},ce=H.attributes;let $=0;const le=ee.getAttributes();for(const ne in le)if(le[ne].location>=0){let Te=ce[ne];Te===void 0&&(ne==="instanceMatrix"&&w.instanceMatrix&&(Te=w.instanceMatrix),ne==="instanceColor"&&w.instanceColor&&(Te=w.instanceColor));const Oe={};Oe.attribute=Te,Te&&Te.data&&(Oe.data=Te.data),oe[ne]=Oe,$++}s.attributes=oe,s.attributesNum=$,s.index=J}function M(){const w=s.newAttributes;for(let H=0,ee=w.length;H<ee;H++)w[H]=0}function v(w){_(w,0)}function _(w,H){const ee=s.newAttributes,J=s.enabledAttributes,oe=s.attributeDivisors;ee[w]=1,J[w]===0&&(r.enableVertexAttribArray(w),J[w]=1),oe[w]!==H&&(r.vertexAttribDivisor(w,H),oe[w]=H)}function A(){const w=s.newAttributes,H=s.enabledAttributes;for(let ee=0,J=H.length;ee<J;ee++)H[ee]!==w[ee]&&(r.disableVertexAttribArray(ee),H[ee]=0)}function P(w,H,ee,J,oe,ce,$){$===!0?r.vertexAttribIPointer(w,H,ee,oe,ce):r.vertexAttribPointer(w,H,ee,J,oe,ce)}function S(w,H,ee,J){M();const oe=J.attributes,ce=ee.getAttributes(),$=H.defaultAttributeValues;for(const le in ce){const ne=ce[le];if(ne.location>=0){let ge=oe[le];if(ge===void 0&&(le==="instanceMatrix"&&w.instanceMatrix&&(ge=w.instanceMatrix),le==="instanceColor"&&w.instanceColor&&(ge=w.instanceColor)),ge!==void 0){const Te=ge.normalized,Oe=ge.itemSize,Ye=e.get(ge);if(Ye===void 0)continue;const yt=Ye.buffer,he=Ye.type,me=Ye.bytesPerElement,Ne=he===r.INT||he===r.UNSIGNED_INT||ge.gpuType===ad;if(ge.isInterleavedBufferAttribute){const Me=ge.data,Xe=Me.stride,Ze=ge.offset;if(Me.isInstancedInterleavedBuffer){for(let tt=0;tt<ne.locationSize;tt++)_(ne.location+tt,Me.meshPerAttribute);w.isInstancedMesh!==!0&&J._maxInstanceCount===void 0&&(J._maxInstanceCount=Me.meshPerAttribute*Me.count)}else for(let tt=0;tt<ne.locationSize;tt++)v(ne.location+tt);r.bindBuffer(r.ARRAY_BUFFER,yt);for(let tt=0;tt<ne.locationSize;tt++)P(ne.location+tt,Oe/ne.locationSize,he,Te,Xe*me,(Ze+Oe/ne.locationSize*tt)*me,Ne)}else{if(ge.isInstancedBufferAttribute){for(let Me=0;Me<ne.locationSize;Me++)_(ne.location+Me,ge.meshPerAttribute);w.isInstancedMesh!==!0&&J._maxInstanceCount===void 0&&(J._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let Me=0;Me<ne.locationSize;Me++)v(ne.location+Me);r.bindBuffer(r.ARRAY_BUFFER,yt);for(let Me=0;Me<ne.locationSize;Me++)P(ne.location+Me,Oe/ne.locationSize,he,Te,Oe*me,Oe/ne.locationSize*Me*me,Ne)}}else if($!==void 0){const Te=$[le];if(Te!==void 0)switch(Te.length){case 2:r.vertexAttrib2fv(ne.location,Te);break;case 3:r.vertexAttrib3fv(ne.location,Te);break;case 4:r.vertexAttrib4fv(ne.location,Te);break;default:r.vertexAttrib1fv(ne.location,Te)}}}}A()}function k(){z();for(const w in n){const H=n[w];for(const ee in H){const J=H[ee];for(const oe in J)f(J[oe].object),delete J[oe];delete H[ee]}delete n[w]}}function O(w){if(n[w.id]===void 0)return;const H=n[w.id];for(const ee in H){const J=H[ee];for(const oe in J)f(J[oe].object),delete J[oe];delete H[ee]}delete n[w.id]}function U(w){for(const H in n){const ee=n[H];if(ee[w.id]===void 0)continue;const J=ee[w.id];for(const oe in J)f(J[oe].object),delete J[oe];delete ee[w.id]}}function z(){I(),a=!0,s!==i&&(s=i,h(s.object))}function I(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:c,reset:z,resetDefaultState:I,dispose:k,releaseStatesOfGeometry:O,releaseStatesOfProgram:U,initAttributes:M,enableAttribute:v,disableUnusedAttributes:A}}function b1(r,e,t){let n;function i(h){n=h}function s(h,f){r.drawArrays(n,h,f),t.update(f,n,1)}function a(h,f,p){p!==0&&(r.drawArraysInstanced(n,h,f,p),t.update(f,n,p))}function c(h,f,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,h,0,f,0,p);let g=0;for(let x=0;x<p;x++)g+=f[x];t.update(g,n,1)}function u(h,f,p,m){if(p===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let x=0;x<h.length;x++)a(h[x],f[x],m[x]);else{g.multiDrawArraysInstancedWEBGL(n,h,0,f,0,m,0,p);let x=0;for(let M=0;M<p;M++)x+=f[M]*m[M];t.update(x,n,1)}}this.setMode=i,this.render=s,this.renderInstances=a,this.renderMultiDraw=c,this.renderMultiDrawInstances=u}function S1(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const U=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(U.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(U){return!(U!==ni&&n.convert(U)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function c(U){const z=U===na&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(U!==qi&&n.convert(U)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&U!==di&&!z)}function u(U){if(U==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";U="mediump"}return U==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=t.precision!==void 0?t.precision:"highp";const f=u(h);f!==h&&(console.warn("THREE.WebGLRenderer:",h,"not supported, using",f,"instead."),h=f);const p=t.logarithmicDepthBuffer===!0,m=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),g=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),x=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),M=r.getParameter(r.MAX_TEXTURE_SIZE),v=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),_=r.getParameter(r.MAX_VERTEX_ATTRIBS),A=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),P=r.getParameter(r.MAX_VARYING_VECTORS),S=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),k=x>0,O=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:u,textureFormatReadable:a,textureTypeReadable:c,precision:h,logarithmicDepthBuffer:p,reverseDepthBuffer:m,maxTextures:g,maxVertexTextures:x,maxTextureSize:M,maxCubemapSize:v,maxAttributes:_,maxVertexUniforms:A,maxVaryings:P,maxFragmentUniforms:S,vertexTextures:k,maxSamples:O}}function M1(r){const e=this;let t=null,n=0,i=!1,s=!1;const a=new hr,c=new ut,u={value:null,needsUpdate:!1};this.uniform=u,this.numPlanes=0,this.numIntersection=0,this.init=function(p,m){const g=p.length!==0||m||n!==0||i;return i=m,n=p.length,g},this.beginShadows=function(){s=!0,f(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(p,m){t=f(p,m,0)},this.setState=function(p,m,g){const x=p.clippingPlanes,M=p.clipIntersection,v=p.clipShadows,_=r.get(p);if(!i||x===null||x.length===0||s&&!v)s?f(null):h();else{const A=s?0:n,P=A*4;let S=_.clippingState||null;u.value=S,S=f(x,m,P,g);for(let k=0;k!==P;++k)S[k]=t[k];_.clippingState=S,this.numIntersection=M?this.numPlanes:0,this.numPlanes+=A}};function h(){u.value!==t&&(u.value=t,u.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function f(p,m,g,x){const M=p!==null?p.length:0;let v=null;if(M!==0){if(v=u.value,x!==!0||v===null){const _=g+M*4,A=m.matrixWorldInverse;c.getNormalMatrix(A),(v===null||v.length<_)&&(v=new Float32Array(_));for(let P=0,S=g;P!==M;++P,S+=4)a.copy(p[P]).applyMatrix4(A,c),a.normal.toArray(v,S),v[S+3]=a.constant}u.value=v,u.needsUpdate=!0}return e.numPlanes=M,e.numIntersection=0,v}}function T1(r){let e=new WeakMap;function t(a,c){return c===Mh?a.mapping=$s:c===Th&&(a.mapping=Js),a}function n(a){if(a&&a.isTexture){const c=a.mapping;if(c===Mh||c===Th)if(e.has(a)){const u=e.get(a).texture;return t(u,a.mapping)}else{const u=a.image;if(u&&u.height>0){const h=new OE(u.height);return h.fromEquirectangularTexture(r,a),e.set(a,h),a.addEventListener("dispose",i),t(h.texture,a.mapping)}else return null}}return a}function i(a){const c=a.target;c.removeEventListener("dispose",i);const u=e.get(c);u!==void 0&&(e.delete(c),u.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class vd extends Og{constructor(e=-1,t=1,n=1,i=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,a=n+e,c=i+t,u=i-t;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=h*this.view.offsetX,a=s+h*this.view.width,c-=f*this.view.offsetY,u=c-f*this.view.height}this.projectionMatrix.makeOrthographic(s,a,c,u,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Gs=4,Jp=[.125,.215,.35,.446,.526,.582],Qr=20,Vu=new vd,Qp=new Ke;let Gu=null,Wu=0,ju=0,Xu=!1;const Zr=(1+Math.sqrt(5))/2,Bs=1/Zr,em=[new F(-Zr,Bs,0),new F(Zr,Bs,0),new F(-Bs,0,Zr),new F(Bs,0,Zr),new F(0,Zr,-Bs),new F(0,Zr,Bs),new F(-1,1,-1),new F(1,1,-1),new F(-1,1,1),new F(1,1,1)];class tm{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){Gu=this._renderer.getRenderTarget(),Wu=this._renderer.getActiveCubeFace(),ju=this._renderer.getActiveMipmapLevel(),Xu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=rm(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=im(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Gu,Wu,ju),this._renderer.xr.enabled=Xu,e.scissorTest=!1,ac(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===$s||e.mapping===Js?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Gu=this._renderer.getRenderTarget(),Wu=this._renderer.getActiveCubeFace(),ju=this._renderer.getActiveMipmapLevel(),Xu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:Zn,minFilter:Zn,generateMipmaps:!1,type:na,format:ni,colorSpace:Ln,depthBuffer:!1},i=nm(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=nm(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=E1(s)),this._blurMaterial=A1(s,e,t)}return i}_compileMaterial(e){const t=new we(this._lodPlanes[0],e);this._renderer.compile(t,Vu)}_sceneToCubeUV(e,t,n,i){const c=new Cn(90,1,t,n),u=[1,-1,1,1,1,1],h=[1,1,1,-1,-1,-1],f=this._renderer,p=f.autoClear,m=f.toneMapping;f.getClearColor(Qp),f.toneMapping=gr,f.autoClear=!1;const g=new ii({name:"PMREM.Background",side:Bn,depthWrite:!1,depthTest:!1}),x=new we(new Yt,g);let M=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,M=!0):(g.color.copy(Qp),M=!0);for(let _=0;_<6;_++){const A=_%3;A===0?(c.up.set(0,u[_],0),c.lookAt(h[_],0,0)):A===1?(c.up.set(0,0,u[_]),c.lookAt(0,h[_],0)):(c.up.set(0,u[_],0),c.lookAt(0,0,h[_]));const P=this._cubeSize;ac(i,A*P,_>2?P:0,P,P),f.setRenderTarget(i),M&&f.render(x,c),f.render(e,c)}x.geometry.dispose(),x.material.dispose(),f.toneMapping=m,f.autoClear=p,e.background=v}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===$s||e.mapping===Js;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=rm()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=im());const s=i?this._cubemapMaterial:this._equirectMaterial,a=new we(this._lodPlanes[0],s),c=s.uniforms;c.envMap.value=e;const u=this._cubeSize;ac(t,0,0,3*u,2*u),n.setRenderTarget(t),n.render(a,Vu)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),c=em[(i-s-1)%em.length];this._blur(e,s-1,s,a,c)}t.autoClear=n}_blur(e,t,n,i,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",s),this._halfBlur(a,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,a,c){const u=this._renderer,h=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const f=3,p=new we(this._lodPlanes[i],h),m=h.uniforms,g=this._sizeLods[n]-1,x=isFinite(s)?Math.PI/(2*g):2*Math.PI/(2*Qr-1),M=s/x,v=isFinite(s)?1+Math.floor(f*M):Qr;v>Qr&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${Qr}`);const _=[];let A=0;for(let U=0;U<Qr;++U){const z=U/M,I=Math.exp(-z*z/2);_.push(I),U===0?A+=I:U<v&&(A+=2*I)}for(let U=0;U<_.length;U++)_[U]=_[U]/A;m.envMap.value=e.texture,m.samples.value=v,m.weights.value=_,m.latitudinal.value=a==="latitudinal",c&&(m.poleAxis.value=c);const{_lodMax:P}=this;m.dTheta.value=x,m.mipInt.value=P-n;const S=this._sizeLods[i],k=3*S*(i>P-Gs?i-P+Gs:0),O=4*(this._cubeSize-S);ac(t,k,O,3*S,2*S),u.setRenderTarget(t),u.render(p,Vu)}}function E1(r){const e=[],t=[],n=[];let i=r;const s=r-Gs+1+Jp.length;for(let a=0;a<s;a++){const c=Math.pow(2,i);t.push(c);let u=1/c;a>r-Gs?u=Jp[a-r+Gs-1]:a===0&&(u=0),n.push(u);const h=1/(c-2),f=-h,p=1+h,m=[f,f,p,f,p,p,f,f,p,p,f,p],g=6,x=6,M=3,v=2,_=1,A=new Float32Array(M*x*g),P=new Float32Array(v*x*g),S=new Float32Array(_*x*g);for(let O=0;O<g;O++){const U=O%3*2/3-1,z=O>2?0:-1,I=[U,z,0,U+2/3,z,0,U+2/3,z+1,0,U,z,0,U+2/3,z+1,0,U,z+1,0];A.set(I,M*x*O),P.set(m,v*x*O);const w=[O,O,O,O,O,O];S.set(w,_*x*O)}const k=new sn;k.setAttribute("position",new Qt(A,M)),k.setAttribute("uv",new Qt(P,v)),k.setAttribute("faceIndex",new Qt(S,_)),e.push(k),i>Gs&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function nm(r,e,t){const n=new ns(r,e,t);return n.texture.mapping=Fc,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function ac(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function A1(r,e,t){const n=new Float32Array(Qr),i=new F(0,1,0);return new _r({name:"SphericalGaussianBlur",defines:{n:Qr,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:yd(),fragmentShader:`

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
		`,blending:mr,depthTest:!1,depthWrite:!1})}function im(){return new _r({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:yd(),fragmentShader:`

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
		`,blending:mr,depthTest:!1,depthWrite:!1})}function rm(){return new _r({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:yd(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:mr,depthTest:!1,depthWrite:!1})}function yd(){return`

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
	`}function w1(r){let e=new WeakMap,t=null;function n(c){if(c&&c.isTexture){const u=c.mapping,h=u===Mh||u===Th,f=u===$s||u===Js;if(h||f){let p=e.get(c);const m=p!==void 0?p.texture.pmremVersion:0;if(c.isRenderTargetTexture&&c.pmremVersion!==m)return t===null&&(t=new tm(r)),p=h?t.fromEquirectangular(c,p):t.fromCubemap(c,p),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),p.texture;if(p!==void 0)return p.texture;{const g=c.image;return h&&g&&g.height>0||f&&g&&i(g)?(t===null&&(t=new tm(r)),p=h?t.fromEquirectangular(c):t.fromCubemap(c),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),c.addEventListener("dispose",s),p.texture):null}}}return c}function i(c){let u=0;const h=6;for(let f=0;f<h;f++)c[f]!==void 0&&u++;return u===h}function s(c){const u=c.target;u.removeEventListener("dispose",s);const h=e.get(u);h!==void 0&&(e.delete(u),h.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function P1(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&Wo("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function R1(r,e,t,n){const i={},s=new WeakMap;function a(p){const m=p.target;m.index!==null&&e.remove(m.index);for(const x in m.attributes)e.remove(m.attributes[x]);for(const x in m.morphAttributes){const M=m.morphAttributes[x];for(let v=0,_=M.length;v<_;v++)e.remove(M[v])}m.removeEventListener("dispose",a),delete i[m.id];const g=s.get(m);g&&(e.remove(g),s.delete(m)),n.releaseStatesOfGeometry(m),m.isInstancedBufferGeometry===!0&&delete m._maxInstanceCount,t.memory.geometries--}function c(p,m){return i[m.id]===!0||(m.addEventListener("dispose",a),i[m.id]=!0,t.memory.geometries++),m}function u(p){const m=p.attributes;for(const x in m)e.update(m[x],r.ARRAY_BUFFER);const g=p.morphAttributes;for(const x in g){const M=g[x];for(let v=0,_=M.length;v<_;v++)e.update(M[v],r.ARRAY_BUFFER)}}function h(p){const m=[],g=p.index,x=p.attributes.position;let M=0;if(g!==null){const A=g.array;M=g.version;for(let P=0,S=A.length;P<S;P+=3){const k=A[P+0],O=A[P+1],U=A[P+2];m.push(k,O,O,U,U,k)}}else if(x!==void 0){const A=x.array;M=x.version;for(let P=0,S=A.length/3-1;P<S;P+=3){const k=P+0,O=P+1,U=P+2;m.push(k,O,O,U,U,k)}}else return;const v=new(Pg(m)?Dg:Lg)(m,1);v.version=M;const _=s.get(p);_&&e.remove(_),s.set(p,v)}function f(p){const m=s.get(p);if(m){const g=p.index;g!==null&&m.version<g.version&&h(p)}else h(p);return s.get(p)}return{get:c,update:u,getWireframeAttribute:f}}function C1(r,e,t){let n;function i(m){n=m}let s,a;function c(m){s=m.type,a=m.bytesPerElement}function u(m,g){r.drawElements(n,g,s,m*a),t.update(g,n,1)}function h(m,g,x){x!==0&&(r.drawElementsInstanced(n,g,s,m*a,x),t.update(g,n,x))}function f(m,g,x){if(x===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,g,0,s,m,0,x);let v=0;for(let _=0;_<x;_++)v+=g[_];t.update(v,n,1)}function p(m,g,x,M){if(x===0)return;const v=e.get("WEBGL_multi_draw");if(v===null)for(let _=0;_<m.length;_++)h(m[_]/a,g[_],M[_]);else{v.multiDrawElementsInstancedWEBGL(n,g,0,s,m,0,M,0,x);let _=0;for(let A=0;A<x;A++)_+=g[A]*M[A];t.update(_,n,1)}}this.setMode=i,this.setIndex=c,this.render=u,this.renderInstances=h,this.renderMultiDraw=f,this.renderMultiDrawInstances=p}function I1(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,c){switch(t.calls++,a){case r.TRIANGLES:t.triangles+=c*(s/3);break;case r.LINES:t.lines+=c*(s/2);break;case r.LINE_STRIP:t.lines+=c*(s-1);break;case r.LINE_LOOP:t.lines+=c*s;break;case r.POINTS:t.points+=c*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function L1(r,e,t){const n=new WeakMap,i=new Et;function s(a,c,u){const h=a.morphTargetInfluences,f=c.morphAttributes.position||c.morphAttributes.normal||c.morphAttributes.color,p=f!==void 0?f.length:0;let m=n.get(c);if(m===void 0||m.count!==p){let w=function(){z.dispose(),n.delete(c),c.removeEventListener("dispose",w)};var g=w;m!==void 0&&m.texture.dispose();const x=c.morphAttributes.position!==void 0,M=c.morphAttributes.normal!==void 0,v=c.morphAttributes.color!==void 0,_=c.morphAttributes.position||[],A=c.morphAttributes.normal||[],P=c.morphAttributes.color||[];let S=0;x===!0&&(S=1),M===!0&&(S=2),v===!0&&(S=3);let k=c.attributes.position.count*S,O=1;k>e.maxTextureSize&&(O=Math.ceil(k/e.maxTextureSize),k=e.maxTextureSize);const U=new Float32Array(k*O*4*p),z=new Cg(U,k,O,p);z.type=di,z.needsUpdate=!0;const I=S*4;for(let H=0;H<p;H++){const ee=_[H],J=A[H],oe=P[H],ce=k*O*4*H;for(let $=0;$<ee.count;$++){const le=$*I;x===!0&&(i.fromBufferAttribute(ee,$),U[ce+le+0]=i.x,U[ce+le+1]=i.y,U[ce+le+2]=i.z,U[ce+le+3]=0),M===!0&&(i.fromBufferAttribute(J,$),U[ce+le+4]=i.x,U[ce+le+5]=i.y,U[ce+le+6]=i.z,U[ce+le+7]=0),v===!0&&(i.fromBufferAttribute(oe,$),U[ce+le+8]=i.x,U[ce+le+9]=i.y,U[ce+le+10]=i.z,U[ce+le+11]=oe.itemSize===4?i.w:1)}}m={count:p,texture:z,size:new Qe(k,O)},n.set(c,m),c.addEventListener("dispose",w)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)u.getUniforms().setValue(r,"morphTexture",a.morphTexture,t);else{let x=0;for(let v=0;v<h.length;v++)x+=h[v];const M=c.morphTargetsRelative?1:1-x;u.getUniforms().setValue(r,"morphTargetBaseInfluence",M),u.getUniforms().setValue(r,"morphTargetInfluences",h)}u.getUniforms().setValue(r,"morphTargetsTexture",m.texture,t),u.getUniforms().setValue(r,"morphTargetsTextureSize",m.size)}return{update:s}}function D1(r,e,t,n){let i=new WeakMap;function s(u){const h=n.render.frame,f=u.geometry,p=e.get(u,f);if(i.get(p)!==h&&(e.update(p),i.set(p,h)),u.isInstancedMesh&&(u.hasEventListener("dispose",c)===!1&&u.addEventListener("dispose",c),i.get(u)!==h&&(t.update(u.instanceMatrix,r.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,r.ARRAY_BUFFER),i.set(u,h))),u.isSkinnedMesh){const m=u.skeleton;i.get(m)!==h&&(m.update(),i.set(m,h))}return p}function a(){i=new WeakMap}function c(u){const h=u.target;h.removeEventListener("dispose",c),t.remove(h.instanceMatrix),h.instanceColor!==null&&t.remove(h.instanceColor)}return{update:s,dispose:a}}class Bg extends fn{constructor(e,t,n,i,s,a,c,u,h,f=qs){if(f!==qs&&f!==to)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&f===qs&&(n=ts),n===void 0&&f===to&&(n=eo),super(null,i,s,a,c,u,f,n,h),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=c!==void 0?c:In,this.minFilter=u!==void 0?u:In,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const kg=new fn,sm=new Bg(1,1),zg=new Cg,Hg=new yE,Vg=new Ug,om=[],am=[],cm=new Float32Array(16),lm=new Float32Array(9),um=new Float32Array(4);function co(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=om[i];if(s===void 0&&(s=new Float32Array(i),om[i]=s),e!==0){n.toArray(s,0);for(let a=1,c=0;a!==e;++a)c+=t,r[a].toArray(s,c)}return s}function on(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function an(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function kc(r,e){let t=am[e];t===void 0&&(t=new Int32Array(e),am[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function N1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function O1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(on(t,e))return;r.uniform2fv(this.addr,e),an(t,e)}}function U1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(on(t,e))return;r.uniform3fv(this.addr,e),an(t,e)}}function F1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(on(t,e))return;r.uniform4fv(this.addr,e),an(t,e)}}function B1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(on(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),an(t,e)}else{if(on(t,n))return;um.set(n),r.uniformMatrix2fv(this.addr,!1,um),an(t,n)}}function k1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(on(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),an(t,e)}else{if(on(t,n))return;lm.set(n),r.uniformMatrix3fv(this.addr,!1,lm),an(t,n)}}function z1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(on(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),an(t,e)}else{if(on(t,n))return;cm.set(n),r.uniformMatrix4fv(this.addr,!1,cm),an(t,n)}}function H1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function V1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(on(t,e))return;r.uniform2iv(this.addr,e),an(t,e)}}function G1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(on(t,e))return;r.uniform3iv(this.addr,e),an(t,e)}}function W1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(on(t,e))return;r.uniform4iv(this.addr,e),an(t,e)}}function j1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function X1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(on(t,e))return;r.uniform2uiv(this.addr,e),an(t,e)}}function q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(on(t,e))return;r.uniform3uiv(this.addr,e),an(t,e)}}function Y1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(on(t,e))return;r.uniform4uiv(this.addr,e),an(t,e)}}function K1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(sm.compareFunction=Ag,s=sm):s=kg,t.setTexture2D(e||s,i)}function Z1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Hg,i)}function $1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Vg,i)}function J1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||zg,i)}function Q1(r){switch(r){case 5126:return N1;case 35664:return O1;case 35665:return U1;case 35666:return F1;case 35674:return B1;case 35675:return k1;case 35676:return z1;case 5124:case 35670:return H1;case 35667:case 35671:return V1;case 35668:case 35672:return G1;case 35669:case 35673:return W1;case 5125:return j1;case 36294:return X1;case 36295:return q1;case 36296:return Y1;case 35678:case 36198:case 36298:case 36306:case 35682:return K1;case 35679:case 36299:case 36307:return Z1;case 35680:case 36300:case 36308:case 36293:return $1;case 36289:case 36303:case 36311:case 36292:return J1}}function eP(r,e){r.uniform1fv(this.addr,e)}function tP(r,e){const t=co(e,this.size,2);r.uniform2fv(this.addr,t)}function nP(r,e){const t=co(e,this.size,3);r.uniform3fv(this.addr,t)}function iP(r,e){const t=co(e,this.size,4);r.uniform4fv(this.addr,t)}function rP(r,e){const t=co(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function sP(r,e){const t=co(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function oP(r,e){const t=co(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function aP(r,e){r.uniform1iv(this.addr,e)}function cP(r,e){r.uniform2iv(this.addr,e)}function lP(r,e){r.uniform3iv(this.addr,e)}function uP(r,e){r.uniform4iv(this.addr,e)}function hP(r,e){r.uniform1uiv(this.addr,e)}function dP(r,e){r.uniform2uiv(this.addr,e)}function fP(r,e){r.uniform3uiv(this.addr,e)}function pP(r,e){r.uniform4uiv(this.addr,e)}function mP(r,e,t){const n=this.cache,i=e.length,s=kc(t,i);on(n,s)||(r.uniform1iv(this.addr,s),an(n,s));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||kg,s[a])}function gP(r,e,t){const n=this.cache,i=e.length,s=kc(t,i);on(n,s)||(r.uniform1iv(this.addr,s),an(n,s));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Hg,s[a])}function _P(r,e,t){const n=this.cache,i=e.length,s=kc(t,i);on(n,s)||(r.uniform1iv(this.addr,s),an(n,s));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Vg,s[a])}function vP(r,e,t){const n=this.cache,i=e.length,s=kc(t,i);on(n,s)||(r.uniform1iv(this.addr,s),an(n,s));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||zg,s[a])}function yP(r){switch(r){case 5126:return eP;case 35664:return tP;case 35665:return nP;case 35666:return iP;case 35674:return rP;case 35675:return sP;case 35676:return oP;case 5124:case 35670:return aP;case 35667:case 35671:return cP;case 35668:case 35672:return lP;case 35669:case 35673:return uP;case 5125:return hP;case 36294:return dP;case 36295:return fP;case 36296:return pP;case 35678:case 36198:case 36298:case 36306:case 35682:return mP;case 35679:case 36299:case 36307:return gP;case 35680:case 36300:case 36308:case 36293:return _P;case 36289:case 36303:case 36311:case 36292:return vP}}class xP{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Q1(t.type)}}class bP{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=yP(t.type)}}class SP{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,a=i.length;s!==a;++s){const c=i[s];c.setValue(e,t[c.id],n)}}}const qu=/(\w+)(\])?(\[|\.)?/g;function hm(r,e){r.seq.push(e),r.map[e.id]=e}function MP(r,e,t){const n=r.name,i=n.length;for(qu.lastIndex=0;;){const s=qu.exec(n),a=qu.lastIndex;let c=s[1];const u=s[2]==="]",h=s[3];if(u&&(c=c|0),h===void 0||h==="["&&a+2===i){hm(t,h===void 0?new xP(c,r,e):new bP(c,r,e));break}else{let p=t.map[c];p===void 0&&(p=new SP(c),hm(t,p)),t=p}}}class Pc{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),a=e.getUniformLocation(t,s.name);MP(s,a,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,a=t.length;s!==a;++s){const c=t[s],u=n[c.id];u.needsUpdate!==!1&&c.setValue(e,u.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function dm(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const TP=37297;let EP=0;function AP(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=i;a<s;a++){const c=a+1;n.push(`${c===e?">":" "} ${c}: ${t[a]}`)}return n.join(`
`)}const fm=new ut;function wP(r){bt._getMatrix(fm,bt.workingColorSpace,r);const e=`mat3( ${fm.elements.map(t=>t.toFixed(4))} )`;switch(bt.getTransfer(r)){case Bc:return[e,"LinearTransferOETF"];case Dt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[e,"LinearTransferOETF"]}}function pm(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+AP(r.getShaderSource(e),a)}else return i}function PP(r,e){const t=wP(e);return[`vec4 ${r}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function RP(r,e){let t;switch(e){case PT:t="Linear";break;case RT:t="Reinhard";break;case CT:t="Cineon";break;case hg:t="ACESFilmic";break;case LT:t="AgX";break;case DT:t="Neutral";break;case IT:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const cc=new F;function CP(){bt.getLuminanceCoefficients(cc);const r=cc.x.toFixed(4),e=cc.y.toFixed(4),t=cc.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function IP(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(jo).join(`
`)}function LP(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function DP(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),a=s.name;let c=1;s.type===r.FLOAT_MAT2&&(c=2),s.type===r.FLOAT_MAT3&&(c=3),s.type===r.FLOAT_MAT4&&(c=4),t[a]={type:s.type,location:r.getAttribLocation(e,a),locationSize:c}}return t}function jo(r){return r!==""}function mm(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function gm(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const NP=/^[ \t]*#include +<([\w\d./]+)>/gm;function Qh(r){return r.replace(NP,UP)}const OP=new Map;function UP(r,e){let t=ft[e];if(t===void 0){const n=OP.get(e);if(n!==void 0)t=ft[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return Qh(t)}const FP=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function _m(r){return r.replace(FP,BP)}function BP(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function vm(r){let e=`precision ${r.precision} float;
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
#define LOW_PRECISION`),e}function kP(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===cg?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===lg?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===zi&&(e="SHADOWMAP_TYPE_VSM"),e}function zP(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case $s:case Js:e="ENVMAP_TYPE_CUBE";break;case Fc:e="ENVMAP_TYPE_CUBE_UV";break}return e}function HP(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Js:e="ENVMAP_MODE_REFRACTION";break}return e}function VP(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case ug:e="ENVMAP_BLENDING_MULTIPLY";break;case AT:e="ENVMAP_BLENDING_MIX";break;case wT:e="ENVMAP_BLENDING_ADD";break}return e}function GP(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function WP(r,e,t,n){const i=r.getContext(),s=t.defines;let a=t.vertexShader,c=t.fragmentShader;const u=kP(t),h=zP(t),f=HP(t),p=VP(t),m=GP(t),g=IP(t),x=LP(s),M=i.createProgram();let v,_,A=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(jo).join(`
`),v.length>0&&(v+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(jo).join(`
`),_.length>0&&(_+=`
`)):(v=[vm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(jo).join(`
`),_=[vm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.envMap?"#define "+f:"",t.envMap?"#define "+p:"",m?"#define CUBEUV_TEXEL_WIDTH "+m.texelWidth:"",m?"#define CUBEUV_TEXEL_HEIGHT "+m.texelHeight:"",m?"#define CUBEUV_MAX_MIP "+m.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==gr?"#define TONE_MAPPING":"",t.toneMapping!==gr?ft.tonemapping_pars_fragment:"",t.toneMapping!==gr?RP("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",ft.colorspace_pars_fragment,PP("linearToOutputTexel",t.outputColorSpace),CP(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(jo).join(`
`)),a=Qh(a),a=mm(a,t),a=gm(a,t),c=Qh(c),c=mm(c,t),c=gm(c,t),a=_m(a),c=_m(c),t.isRawShaderMaterial!==!0&&(A=`#version 300 es
`,v=[g,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,_=["#define varying in",t.glslVersion===Cp?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Cp?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const P=A+v+a,S=A+_+c,k=dm(i,i.VERTEX_SHADER,P),O=dm(i,i.FRAGMENT_SHADER,S);i.attachShader(M,k),i.attachShader(M,O),t.index0AttributeName!==void 0?i.bindAttribLocation(M,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(M,0,"position"),i.linkProgram(M);function U(H){if(r.debug.checkShaderErrors){const ee=i.getProgramInfoLog(M).trim(),J=i.getShaderInfoLog(k).trim(),oe=i.getShaderInfoLog(O).trim();let ce=!0,$=!0;if(i.getProgramParameter(M,i.LINK_STATUS)===!1)if(ce=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,M,k,O);else{const le=pm(i,k,"vertex"),ne=pm(i,O,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(M,i.VALIDATE_STATUS)+`

Material Name: `+H.name+`
Material Type: `+H.type+`

Program Info Log: `+ee+`
`+le+`
`+ne)}else ee!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ee):(J===""||oe==="")&&($=!1);$&&(H.diagnostics={runnable:ce,programLog:ee,vertexShader:{log:J,prefix:v},fragmentShader:{log:oe,prefix:_}})}i.deleteShader(k),i.deleteShader(O),z=new Pc(i,M),I=DP(i,M)}let z;this.getUniforms=function(){return z===void 0&&U(this),z};let I;this.getAttributes=function(){return I===void 0&&U(this),I};let w=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return w===!1&&(w=i.getProgramParameter(M,TP)),w},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(M),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=EP++,this.cacheKey=e,this.usedTimes=1,this.program=M,this.vertexShader=k,this.fragmentShader=O,this}let jP=0;class XP{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new qP(e),t.set(e,n)),n}}class qP{constructor(e){this.id=jP++,this.code=e,this.usedTimes=0}}function YP(r,e,t,n,i,s,a){const c=new gd,u=new XP,h=new Set,f=[],p=i.logarithmicDepthBuffer,m=i.vertexTextures;let g=i.precision;const x={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function M(I){return h.add(I),I===0?"uv":`uv${I}`}function v(I,w,H,ee,J){const oe=ee.fog,ce=J.geometry,$=I.isMeshStandardMaterial?ee.environment:null,le=(I.isMeshStandardMaterial?t:e).get(I.envMap||$),ne=le&&le.mapping===Fc?le.image.height:null,ge=x[I.type];I.precision!==null&&(g=i.getMaxPrecision(I.precision),g!==I.precision&&console.warn("THREE.WebGLProgram.getParameters:",I.precision,"not supported, using",g,"instead."));const Te=ce.morphAttributes.position||ce.morphAttributes.normal||ce.morphAttributes.color,Oe=Te!==void 0?Te.length:0;let Ye=0;ce.morphAttributes.position!==void 0&&(Ye=1),ce.morphAttributes.normal!==void 0&&(Ye=2),ce.morphAttributes.color!==void 0&&(Ye=3);let yt,he,me,Ne;if(ge){const pt=vi[ge];yt=pt.vertexShader,he=pt.fragmentShader}else yt=I.vertexShader,he=I.fragmentShader,u.update(I),me=u.getVertexShaderID(I),Ne=u.getFragmentShaderID(I);const Me=r.getRenderTarget(),Xe=r.state.buffers.depth.getReversed(),Ze=J.isInstancedMesh===!0,tt=J.isBatchedMesh===!0,St=!!I.map,rt=!!I.matcap,At=!!le,W=!!I.aoMap,cn=!!I.lightMap,ht=!!I.bumpMap,ct=!!I.normalMap,Fe=!!I.displacementMap,st=!!I.emissiveMap,ke=!!I.metalnessMap,D=!!I.roughnessMap,E=I.anisotropy>0,Z=I.clearcoat>0,ue=I.dispersion>0,pe=I.iridescence>0,fe=I.sheen>0,Ue=I.transmission>0,Pe=E&&!!I.anisotropyMap,De=Z&&!!I.clearcoatMap,dt=Z&&!!I.clearcoatNormalMap,N=Z&&!!I.clearcoatRoughnessMap,Y=pe&&!!I.iridescenceMap,ae=pe&&!!I.iridescenceThicknessMap,_e=fe&&!!I.sheenColorMap,xe=fe&&!!I.sheenRoughnessMap,Re=!!I.specularMap,qe=!!I.specularColorMap,lt=!!I.specularIntensityMap,G=Ue&&!!I.transmissionMap,be=Ue&&!!I.thicknessMap,ie=!!I.gradientMap,de=!!I.alphaMap,Ae=I.alphaTest>0,Ee=!!I.alphaHash,Ge=!!I.extensions;let ot=gr;I.toneMapped&&(Me===null||Me.isXRRenderTarget===!0)&&(ot=r.toneMapping);const Vt={shaderID:ge,shaderType:I.type,shaderName:I.name,vertexShader:yt,fragmentShader:he,defines:I.defines,customVertexShaderID:me,customFragmentShaderID:Ne,isRawShaderMaterial:I.isRawShaderMaterial===!0,glslVersion:I.glslVersion,precision:g,batching:tt,batchingColor:tt&&J._colorsTexture!==null,instancing:Ze,instancingColor:Ze&&J.instanceColor!==null,instancingMorph:Ze&&J.morphTexture!==null,supportsVertexTextures:m,outputColorSpace:Me===null?r.outputColorSpace:Me.isXRRenderTarget===!0?Me.texture.colorSpace:Ln,alphaToCoverage:!!I.alphaToCoverage,map:St,matcap:rt,envMap:At,envMapMode:At&&le.mapping,envMapCubeUVHeight:ne,aoMap:W,lightMap:cn,bumpMap:ht,normalMap:ct,displacementMap:m&&Fe,emissiveMap:st,normalMapObjectSpace:ct&&I.normalMapType===HT,normalMapTangentSpace:ct&&I.normalMapType===Eg,metalnessMap:ke,roughnessMap:D,anisotropy:E,anisotropyMap:Pe,clearcoat:Z,clearcoatMap:De,clearcoatNormalMap:dt,clearcoatRoughnessMap:N,dispersion:ue,iridescence:pe,iridescenceMap:Y,iridescenceThicknessMap:ae,sheen:fe,sheenColorMap:_e,sheenRoughnessMap:xe,specularMap:Re,specularColorMap:qe,specularIntensityMap:lt,transmission:Ue,transmissionMap:G,thicknessMap:be,gradientMap:ie,opaque:I.transparent===!1&&I.blending===Xs&&I.alphaToCoverage===!1,alphaMap:de,alphaTest:Ae,alphaHash:Ee,combine:I.combine,mapUv:St&&M(I.map.channel),aoMapUv:W&&M(I.aoMap.channel),lightMapUv:cn&&M(I.lightMap.channel),bumpMapUv:ht&&M(I.bumpMap.channel),normalMapUv:ct&&M(I.normalMap.channel),displacementMapUv:Fe&&M(I.displacementMap.channel),emissiveMapUv:st&&M(I.emissiveMap.channel),metalnessMapUv:ke&&M(I.metalnessMap.channel),roughnessMapUv:D&&M(I.roughnessMap.channel),anisotropyMapUv:Pe&&M(I.anisotropyMap.channel),clearcoatMapUv:De&&M(I.clearcoatMap.channel),clearcoatNormalMapUv:dt&&M(I.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:N&&M(I.clearcoatRoughnessMap.channel),iridescenceMapUv:Y&&M(I.iridescenceMap.channel),iridescenceThicknessMapUv:ae&&M(I.iridescenceThicknessMap.channel),sheenColorMapUv:_e&&M(I.sheenColorMap.channel),sheenRoughnessMapUv:xe&&M(I.sheenRoughnessMap.channel),specularMapUv:Re&&M(I.specularMap.channel),specularColorMapUv:qe&&M(I.specularColorMap.channel),specularIntensityMapUv:lt&&M(I.specularIntensityMap.channel),transmissionMapUv:G&&M(I.transmissionMap.channel),thicknessMapUv:be&&M(I.thicknessMap.channel),alphaMapUv:de&&M(I.alphaMap.channel),vertexTangents:!!ce.attributes.tangent&&(ct||E),vertexColors:I.vertexColors,vertexAlphas:I.vertexColors===!0&&!!ce.attributes.color&&ce.attributes.color.itemSize===4,pointsUvs:J.isPoints===!0&&!!ce.attributes.uv&&(St||de),fog:!!oe,useFog:I.fog===!0,fogExp2:!!oe&&oe.isFogExp2,flatShading:I.flatShading===!0,sizeAttenuation:I.sizeAttenuation===!0,logarithmicDepthBuffer:p,reverseDepthBuffer:Xe,skinning:J.isSkinnedMesh===!0,morphTargets:ce.morphAttributes.position!==void 0,morphNormals:ce.morphAttributes.normal!==void 0,morphColors:ce.morphAttributes.color!==void 0,morphTargetsCount:Oe,morphTextureStride:Ye,numDirLights:w.directional.length,numPointLights:w.point.length,numSpotLights:w.spot.length,numSpotLightMaps:w.spotLightMap.length,numRectAreaLights:w.rectArea.length,numHemiLights:w.hemi.length,numDirLightShadows:w.directionalShadowMap.length,numPointLightShadows:w.pointShadowMap.length,numSpotLightShadows:w.spotShadowMap.length,numSpotLightShadowsWithMaps:w.numSpotLightShadowsWithMaps,numLightProbes:w.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:I.dithering,shadowMapEnabled:r.shadowMap.enabled&&H.length>0,shadowMapType:r.shadowMap.type,toneMapping:ot,decodeVideoTexture:St&&I.map.isVideoTexture===!0&&bt.getTransfer(I.map.colorSpace)===Dt,decodeVideoTextureEmissive:st&&I.emissiveMap.isVideoTexture===!0&&bt.getTransfer(I.emissiveMap.colorSpace)===Dt,premultipliedAlpha:I.premultipliedAlpha,doubleSided:I.side===Fn,flipSided:I.side===Bn,useDepthPacking:I.depthPacking>=0,depthPacking:I.depthPacking||0,index0AttributeName:I.index0AttributeName,extensionClipCullDistance:Ge&&I.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Ge&&I.extensions.multiDraw===!0||tt)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:I.customProgramCacheKey()};return Vt.vertexUv1s=h.has(1),Vt.vertexUv2s=h.has(2),Vt.vertexUv3s=h.has(3),h.clear(),Vt}function _(I){const w=[];if(I.shaderID?w.push(I.shaderID):(w.push(I.customVertexShaderID),w.push(I.customFragmentShaderID)),I.defines!==void 0)for(const H in I.defines)w.push(H),w.push(I.defines[H]);return I.isRawShaderMaterial===!1&&(A(w,I),P(w,I),w.push(r.outputColorSpace)),w.push(I.customProgramCacheKey),w.join()}function A(I,w){I.push(w.precision),I.push(w.outputColorSpace),I.push(w.envMapMode),I.push(w.envMapCubeUVHeight),I.push(w.mapUv),I.push(w.alphaMapUv),I.push(w.lightMapUv),I.push(w.aoMapUv),I.push(w.bumpMapUv),I.push(w.normalMapUv),I.push(w.displacementMapUv),I.push(w.emissiveMapUv),I.push(w.metalnessMapUv),I.push(w.roughnessMapUv),I.push(w.anisotropyMapUv),I.push(w.clearcoatMapUv),I.push(w.clearcoatNormalMapUv),I.push(w.clearcoatRoughnessMapUv),I.push(w.iridescenceMapUv),I.push(w.iridescenceThicknessMapUv),I.push(w.sheenColorMapUv),I.push(w.sheenRoughnessMapUv),I.push(w.specularMapUv),I.push(w.specularColorMapUv),I.push(w.specularIntensityMapUv),I.push(w.transmissionMapUv),I.push(w.thicknessMapUv),I.push(w.combine),I.push(w.fogExp2),I.push(w.sizeAttenuation),I.push(w.morphTargetsCount),I.push(w.morphAttributeCount),I.push(w.numDirLights),I.push(w.numPointLights),I.push(w.numSpotLights),I.push(w.numSpotLightMaps),I.push(w.numHemiLights),I.push(w.numRectAreaLights),I.push(w.numDirLightShadows),I.push(w.numPointLightShadows),I.push(w.numSpotLightShadows),I.push(w.numSpotLightShadowsWithMaps),I.push(w.numLightProbes),I.push(w.shadowMapType),I.push(w.toneMapping),I.push(w.numClippingPlanes),I.push(w.numClipIntersection),I.push(w.depthPacking)}function P(I,w){c.disableAll(),w.supportsVertexTextures&&c.enable(0),w.instancing&&c.enable(1),w.instancingColor&&c.enable(2),w.instancingMorph&&c.enable(3),w.matcap&&c.enable(4),w.envMap&&c.enable(5),w.normalMapObjectSpace&&c.enable(6),w.normalMapTangentSpace&&c.enable(7),w.clearcoat&&c.enable(8),w.iridescence&&c.enable(9),w.alphaTest&&c.enable(10),w.vertexColors&&c.enable(11),w.vertexAlphas&&c.enable(12),w.vertexUv1s&&c.enable(13),w.vertexUv2s&&c.enable(14),w.vertexUv3s&&c.enable(15),w.vertexTangents&&c.enable(16),w.anisotropy&&c.enable(17),w.alphaHash&&c.enable(18),w.batching&&c.enable(19),w.dispersion&&c.enable(20),w.batchingColor&&c.enable(21),I.push(c.mask),c.disableAll(),w.fog&&c.enable(0),w.useFog&&c.enable(1),w.flatShading&&c.enable(2),w.logarithmicDepthBuffer&&c.enable(3),w.reverseDepthBuffer&&c.enable(4),w.skinning&&c.enable(5),w.morphTargets&&c.enable(6),w.morphNormals&&c.enable(7),w.morphColors&&c.enable(8),w.premultipliedAlpha&&c.enable(9),w.shadowMapEnabled&&c.enable(10),w.doubleSided&&c.enable(11),w.flipSided&&c.enable(12),w.useDepthPacking&&c.enable(13),w.dithering&&c.enable(14),w.transmission&&c.enable(15),w.sheen&&c.enable(16),w.opaque&&c.enable(17),w.pointsUvs&&c.enable(18),w.decodeVideoTexture&&c.enable(19),w.decodeVideoTextureEmissive&&c.enable(20),w.alphaToCoverage&&c.enable(21),I.push(c.mask)}function S(I){const w=x[I.type];let H;if(w){const ee=vi[w];H=IE.clone(ee.uniforms)}else H=I.uniforms;return H}function k(I,w){let H;for(let ee=0,J=f.length;ee<J;ee++){const oe=f[ee];if(oe.cacheKey===w){H=oe,++H.usedTimes;break}}return H===void 0&&(H=new WP(r,w,I,s),f.push(H)),H}function O(I){if(--I.usedTimes===0){const w=f.indexOf(I);f[w]=f[f.length-1],f.pop(),I.destroy()}}function U(I){u.remove(I)}function z(){u.dispose()}return{getParameters:v,getProgramCacheKey:_,getUniforms:S,acquireProgram:k,releaseProgram:O,releaseShaderCache:U,programs:f,dispose:z}}function KP(){let r=new WeakMap;function e(a){return r.has(a)}function t(a){let c=r.get(a);return c===void 0&&(c={},r.set(a,c)),c}function n(a){r.delete(a)}function i(a,c,u){r.get(a)[c]=u}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function ZP(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function ym(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function xm(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function a(p,m,g,x,M,v){let _=r[e];return _===void 0?(_={id:p.id,object:p,geometry:m,material:g,groupOrder:x,renderOrder:p.renderOrder,z:M,group:v},r[e]=_):(_.id=p.id,_.object=p,_.geometry=m,_.material=g,_.groupOrder=x,_.renderOrder=p.renderOrder,_.z=M,_.group=v),e++,_}function c(p,m,g,x,M,v){const _=a(p,m,g,x,M,v);g.transmission>0?n.push(_):g.transparent===!0?i.push(_):t.push(_)}function u(p,m,g,x,M,v){const _=a(p,m,g,x,M,v);g.transmission>0?n.unshift(_):g.transparent===!0?i.unshift(_):t.unshift(_)}function h(p,m){t.length>1&&t.sort(p||ZP),n.length>1&&n.sort(m||ym),i.length>1&&i.sort(m||ym)}function f(){for(let p=e,m=r.length;p<m;p++){const g=r[p];if(g.id===null)break;g.id=null,g.object=null,g.geometry=null,g.material=null,g.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:c,unshift:u,finish:f,sort:h}}function $P(){let r=new WeakMap;function e(n,i){const s=r.get(n);let a;return s===void 0?(a=new xm,r.set(n,[a])):i>=s.length?(a=new xm,s.push(a)):a=s[i],a}function t(){r=new WeakMap}return{get:e,dispose:t}}function JP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new F,color:new Ke};break;case"SpotLight":t={position:new F,direction:new F,color:new Ke,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new F,color:new Ke,distance:0,decay:0};break;case"HemisphereLight":t={direction:new F,skyColor:new Ke,groundColor:new Ke};break;case"RectAreaLight":t={color:new Ke,position:new F,halfWidth:new F,halfHeight:new F};break}return r[e.id]=t,t}}}function QP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qe,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let eR=0;function tR(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function nR(r){const e=new JP,t=QP(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)n.probe.push(new F);const i=new F,s=new nt,a=new nt;function c(h){let f=0,p=0,m=0;for(let I=0;I<9;I++)n.probe[I].set(0,0,0);let g=0,x=0,M=0,v=0,_=0,A=0,P=0,S=0,k=0,O=0,U=0;h.sort(tR);for(let I=0,w=h.length;I<w;I++){const H=h[I],ee=H.color,J=H.intensity,oe=H.distance,ce=H.shadow&&H.shadow.map?H.shadow.map.texture:null;if(H.isAmbientLight)f+=ee.r*J,p+=ee.g*J,m+=ee.b*J;else if(H.isLightProbe){for(let $=0;$<9;$++)n.probe[$].addScaledVector(H.sh.coefficients[$],J);U++}else if(H.isDirectionalLight){const $=e.get(H);if($.color.copy(H.color).multiplyScalar(H.intensity),H.castShadow){const le=H.shadow,ne=t.get(H);ne.shadowIntensity=le.intensity,ne.shadowBias=le.bias,ne.shadowNormalBias=le.normalBias,ne.shadowRadius=le.radius,ne.shadowMapSize=le.mapSize,n.directionalShadow[g]=ne,n.directionalShadowMap[g]=ce,n.directionalShadowMatrix[g]=H.shadow.matrix,A++}n.directional[g]=$,g++}else if(H.isSpotLight){const $=e.get(H);$.position.setFromMatrixPosition(H.matrixWorld),$.color.copy(ee).multiplyScalar(J),$.distance=oe,$.coneCos=Math.cos(H.angle),$.penumbraCos=Math.cos(H.angle*(1-H.penumbra)),$.decay=H.decay,n.spot[M]=$;const le=H.shadow;if(H.map&&(n.spotLightMap[k]=H.map,k++,le.updateMatrices(H),H.castShadow&&O++),n.spotLightMatrix[M]=le.matrix,H.castShadow){const ne=t.get(H);ne.shadowIntensity=le.intensity,ne.shadowBias=le.bias,ne.shadowNormalBias=le.normalBias,ne.shadowRadius=le.radius,ne.shadowMapSize=le.mapSize,n.spotShadow[M]=ne,n.spotShadowMap[M]=ce,S++}M++}else if(H.isRectAreaLight){const $=e.get(H);$.color.copy(ee).multiplyScalar(J),$.halfWidth.set(H.width*.5,0,0),$.halfHeight.set(0,H.height*.5,0),n.rectArea[v]=$,v++}else if(H.isPointLight){const $=e.get(H);if($.color.copy(H.color).multiplyScalar(H.intensity),$.distance=H.distance,$.decay=H.decay,H.castShadow){const le=H.shadow,ne=t.get(H);ne.shadowIntensity=le.intensity,ne.shadowBias=le.bias,ne.shadowNormalBias=le.normalBias,ne.shadowRadius=le.radius,ne.shadowMapSize=le.mapSize,ne.shadowCameraNear=le.camera.near,ne.shadowCameraFar=le.camera.far,n.pointShadow[x]=ne,n.pointShadowMap[x]=ce,n.pointShadowMatrix[x]=H.shadow.matrix,P++}n.point[x]=$,x++}else if(H.isHemisphereLight){const $=e.get(H);$.skyColor.copy(H.color).multiplyScalar(J),$.groundColor.copy(H.groundColor).multiplyScalar(J),n.hemi[_]=$,_++}}v>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ie.LTC_FLOAT_1,n.rectAreaLTC2=Ie.LTC_FLOAT_2):(n.rectAreaLTC1=Ie.LTC_HALF_1,n.rectAreaLTC2=Ie.LTC_HALF_2)),n.ambient[0]=f,n.ambient[1]=p,n.ambient[2]=m;const z=n.hash;(z.directionalLength!==g||z.pointLength!==x||z.spotLength!==M||z.rectAreaLength!==v||z.hemiLength!==_||z.numDirectionalShadows!==A||z.numPointShadows!==P||z.numSpotShadows!==S||z.numSpotMaps!==k||z.numLightProbes!==U)&&(n.directional.length=g,n.spot.length=M,n.rectArea.length=v,n.point.length=x,n.hemi.length=_,n.directionalShadow.length=A,n.directionalShadowMap.length=A,n.pointShadow.length=P,n.pointShadowMap.length=P,n.spotShadow.length=S,n.spotShadowMap.length=S,n.directionalShadowMatrix.length=A,n.pointShadowMatrix.length=P,n.spotLightMatrix.length=S+k-O,n.spotLightMap.length=k,n.numSpotLightShadowsWithMaps=O,n.numLightProbes=U,z.directionalLength=g,z.pointLength=x,z.spotLength=M,z.rectAreaLength=v,z.hemiLength=_,z.numDirectionalShadows=A,z.numPointShadows=P,z.numSpotShadows=S,z.numSpotMaps=k,z.numLightProbes=U,n.version=eR++)}function u(h,f){let p=0,m=0,g=0,x=0,M=0;const v=f.matrixWorldInverse;for(let _=0,A=h.length;_<A;_++){const P=h[_];if(P.isDirectionalLight){const S=n.directional[p];S.direction.setFromMatrixPosition(P.matrixWorld),i.setFromMatrixPosition(P.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(v),p++}else if(P.isSpotLight){const S=n.spot[g];S.position.setFromMatrixPosition(P.matrixWorld),S.position.applyMatrix4(v),S.direction.setFromMatrixPosition(P.matrixWorld),i.setFromMatrixPosition(P.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(v),g++}else if(P.isRectAreaLight){const S=n.rectArea[x];S.position.setFromMatrixPosition(P.matrixWorld),S.position.applyMatrix4(v),a.identity(),s.copy(P.matrixWorld),s.premultiply(v),a.extractRotation(s),S.halfWidth.set(P.width*.5,0,0),S.halfHeight.set(0,P.height*.5,0),S.halfWidth.applyMatrix4(a),S.halfHeight.applyMatrix4(a),x++}else if(P.isPointLight){const S=n.point[m];S.position.setFromMatrixPosition(P.matrixWorld),S.position.applyMatrix4(v),m++}else if(P.isHemisphereLight){const S=n.hemi[M];S.direction.setFromMatrixPosition(P.matrixWorld),S.direction.transformDirection(v),M++}}}return{setup:c,setupView:u,state:n}}function bm(r){const e=new nR(r),t=[],n=[];function i(f){h.camera=f,t.length=0,n.length=0}function s(f){t.push(f)}function a(f){n.push(f)}function c(){e.setup(t)}function u(f){e.setupView(t,f)}const h={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:h,setupLights:c,setupLightsView:u,pushLight:s,pushShadow:a}}function iR(r){let e=new WeakMap;function t(i,s=0){const a=e.get(i);let c;return a===void 0?(c=new bm(r),e.set(i,[c])):s>=a.length?(c=new bm(r),a.push(c)):c=a[s],c}function n(){e=new WeakMap}return{get:t,dispose:n}}class rR extends xi{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=kT,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class sR extends xi{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const oR=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,aR=`uniform sampler2D shadow_pass;
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
}`;function cR(r,e,t){let n=new _d;const i=new Qe,s=new Qe,a=new Et,c=new rR({depthPacking:zT}),u=new sR,h={},f=t.maxTextureSize,p={[Xi]:Bn,[Bn]:Xi,[Fn]:Fn},m=new _r({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Qe},radius:{value:4}},vertexShader:oR,fragmentShader:aR}),g=m.clone();g.defines.HORIZONTAL_PASS=1;const x=new sn;x.setAttribute("position",new Qt(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const M=new we(x,m),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=cg;let _=this.type;this.render=function(O,U,z){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||O.length===0)return;const I=r.getRenderTarget(),w=r.getActiveCubeFace(),H=r.getActiveMipmapLevel(),ee=r.state;ee.setBlending(mr),ee.buffers.color.setClear(1,1,1,1),ee.buffers.depth.setTest(!0),ee.setScissorTest(!1);const J=_!==zi&&this.type===zi,oe=_===zi&&this.type!==zi;for(let ce=0,$=O.length;ce<$;ce++){const le=O[ce],ne=le.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",le,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;i.copy(ne.mapSize);const ge=ne.getFrameExtents();if(i.multiply(ge),s.copy(ne.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(s.x=Math.floor(f/ge.x),i.x=s.x*ge.x,ne.mapSize.x=s.x),i.y>f&&(s.y=Math.floor(f/ge.y),i.y=s.y*ge.y,ne.mapSize.y=s.y)),ne.map===null||J===!0||oe===!0){const Oe=this.type!==zi?{minFilter:In,magFilter:In}:{};ne.map!==null&&ne.map.dispose(),ne.map=new ns(i.x,i.y,Oe),ne.map.texture.name=le.name+".shadowMap",ne.camera.updateProjectionMatrix()}r.setRenderTarget(ne.map),r.clear();const Te=ne.getViewportCount();for(let Oe=0;Oe<Te;Oe++){const Ye=ne.getViewport(Oe);a.set(s.x*Ye.x,s.y*Ye.y,s.x*Ye.z,s.y*Ye.w),ee.viewport(a),ne.updateMatrices(le,Oe),n=ne.getFrustum(),S(U,z,ne.camera,le,this.type)}ne.isPointLightShadow!==!0&&this.type===zi&&A(ne,z),ne.needsUpdate=!1}_=this.type,v.needsUpdate=!1,r.setRenderTarget(I,w,H)};function A(O,U){const z=e.update(M);m.defines.VSM_SAMPLES!==O.blurSamples&&(m.defines.VSM_SAMPLES=O.blurSamples,g.defines.VSM_SAMPLES=O.blurSamples,m.needsUpdate=!0,g.needsUpdate=!0),O.mapPass===null&&(O.mapPass=new ns(i.x,i.y)),m.uniforms.shadow_pass.value=O.map.texture,m.uniforms.resolution.value=O.mapSize,m.uniforms.radius.value=O.radius,r.setRenderTarget(O.mapPass),r.clear(),r.renderBufferDirect(U,null,z,m,M,null),g.uniforms.shadow_pass.value=O.mapPass.texture,g.uniforms.resolution.value=O.mapSize,g.uniforms.radius.value=O.radius,r.setRenderTarget(O.map),r.clear(),r.renderBufferDirect(U,null,z,g,M,null)}function P(O,U,z,I){let w=null;const H=z.isPointLight===!0?O.customDistanceMaterial:O.customDepthMaterial;if(H!==void 0)w=H;else if(w=z.isPointLight===!0?u:c,r.localClippingEnabled&&U.clipShadows===!0&&Array.isArray(U.clippingPlanes)&&U.clippingPlanes.length!==0||U.displacementMap&&U.displacementScale!==0||U.alphaMap&&U.alphaTest>0||U.map&&U.alphaTest>0){const ee=w.uuid,J=U.uuid;let oe=h[ee];oe===void 0&&(oe={},h[ee]=oe);let ce=oe[J];ce===void 0&&(ce=w.clone(),oe[J]=ce,U.addEventListener("dispose",k)),w=ce}if(w.visible=U.visible,w.wireframe=U.wireframe,I===zi?w.side=U.shadowSide!==null?U.shadowSide:U.side:w.side=U.shadowSide!==null?U.shadowSide:p[U.side],w.alphaMap=U.alphaMap,w.alphaTest=U.alphaTest,w.map=U.map,w.clipShadows=U.clipShadows,w.clippingPlanes=U.clippingPlanes,w.clipIntersection=U.clipIntersection,w.displacementMap=U.displacementMap,w.displacementScale=U.displacementScale,w.displacementBias=U.displacementBias,w.wireframeLinewidth=U.wireframeLinewidth,w.linewidth=U.linewidth,z.isPointLight===!0&&w.isMeshDistanceMaterial===!0){const ee=r.properties.get(w);ee.light=z}return w}function S(O,U,z,I,w){if(O.visible===!1)return;if(O.layers.test(U.layers)&&(O.isMesh||O.isLine||O.isPoints)&&(O.castShadow||O.receiveShadow&&w===zi)&&(!O.frustumCulled||n.intersectsObject(O))){O.modelViewMatrix.multiplyMatrices(z.matrixWorldInverse,O.matrixWorld);const J=e.update(O),oe=O.material;if(Array.isArray(oe)){const ce=J.groups;for(let $=0,le=ce.length;$<le;$++){const ne=ce[$],ge=oe[ne.materialIndex];if(ge&&ge.visible){const Te=P(O,ge,I,w);O.onBeforeShadow(r,O,U,z,J,Te,ne),r.renderBufferDirect(z,null,J,Te,O,ne),O.onAfterShadow(r,O,U,z,J,Te,ne)}}}else if(oe.visible){const ce=P(O,oe,I,w);O.onBeforeShadow(r,O,U,z,J,ce,null),r.renderBufferDirect(z,null,J,ce,O,null),O.onAfterShadow(r,O,U,z,J,ce,null)}}const ee=O.children;for(let J=0,oe=ee.length;J<oe;J++)S(ee[J],U,z,I,w)}function k(O){O.target.removeEventListener("dispose",k);for(const z in h){const I=h[z],w=O.target.uuid;w in I&&(I[w].dispose(),delete I[w])}}}const lR={[gh]:_h,[vh]:bh,[yh]:Sh,[Zs]:xh,[_h]:gh,[bh]:vh,[Sh]:yh,[xh]:Zs};function uR(r,e){function t(){let G=!1;const be=new Et;let ie=null;const de=new Et(0,0,0,0);return{setMask:function(Ae){ie!==Ae&&!G&&(r.colorMask(Ae,Ae,Ae,Ae),ie=Ae)},setLocked:function(Ae){G=Ae},setClear:function(Ae,Ee,Ge,ot,Vt){Vt===!0&&(Ae*=ot,Ee*=ot,Ge*=ot),be.set(Ae,Ee,Ge,ot),de.equals(be)===!1&&(r.clearColor(Ae,Ee,Ge,ot),de.copy(be))},reset:function(){G=!1,ie=null,de.set(-1,0,0,0)}}}function n(){let G=!1,be=!1,ie=null,de=null,Ae=null;return{setReversed:function(Ee){if(be!==Ee){const Ge=e.get("EXT_clip_control");be?Ge.clipControlEXT(Ge.LOWER_LEFT_EXT,Ge.ZERO_TO_ONE_EXT):Ge.clipControlEXT(Ge.LOWER_LEFT_EXT,Ge.NEGATIVE_ONE_TO_ONE_EXT);const ot=Ae;Ae=null,this.setClear(ot)}be=Ee},getReversed:function(){return be},setTest:function(Ee){Ee?Me(r.DEPTH_TEST):Xe(r.DEPTH_TEST)},setMask:function(Ee){ie!==Ee&&!G&&(r.depthMask(Ee),ie=Ee)},setFunc:function(Ee){if(be&&(Ee=lR[Ee]),de!==Ee){switch(Ee){case gh:r.depthFunc(r.NEVER);break;case _h:r.depthFunc(r.ALWAYS);break;case vh:r.depthFunc(r.LESS);break;case Zs:r.depthFunc(r.LEQUAL);break;case yh:r.depthFunc(r.EQUAL);break;case xh:r.depthFunc(r.GEQUAL);break;case bh:r.depthFunc(r.GREATER);break;case Sh:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}de=Ee}},setLocked:function(Ee){G=Ee},setClear:function(Ee){Ae!==Ee&&(be&&(Ee=1-Ee),r.clearDepth(Ee),Ae=Ee)},reset:function(){G=!1,ie=null,de=null,Ae=null,be=!1}}}function i(){let G=!1,be=null,ie=null,de=null,Ae=null,Ee=null,Ge=null,ot=null,Vt=null;return{setTest:function(pt){G||(pt?Me(r.STENCIL_TEST):Xe(r.STENCIL_TEST))},setMask:function(pt){be!==pt&&!G&&(r.stencilMask(pt),be=pt)},setFunc:function(pt,An,kn){(ie!==pt||de!==An||Ae!==kn)&&(r.stencilFunc(pt,An,kn),ie=pt,de=An,Ae=kn)},setOp:function(pt,An,kn){(Ee!==pt||Ge!==An||ot!==kn)&&(r.stencilOp(pt,An,kn),Ee=pt,Ge=An,ot=kn)},setLocked:function(pt){G=pt},setClear:function(pt){Vt!==pt&&(r.clearStencil(pt),Vt=pt)},reset:function(){G=!1,be=null,ie=null,de=null,Ae=null,Ee=null,Ge=null,ot=null,Vt=null}}}const s=new t,a=new n,c=new i,u=new WeakMap,h=new WeakMap;let f={},p={},m=new WeakMap,g=[],x=null,M=!1,v=null,_=null,A=null,P=null,S=null,k=null,O=null,U=new Ke(0,0,0),z=0,I=!1,w=null,H=null,ee=null,J=null,oe=null;const ce=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let $=!1,le=0;const ne=r.getParameter(r.VERSION);ne.indexOf("WebGL")!==-1?(le=parseFloat(/^WebGL (\d)/.exec(ne)[1]),$=le>=1):ne.indexOf("OpenGL ES")!==-1&&(le=parseFloat(/^OpenGL ES (\d)/.exec(ne)[1]),$=le>=2);let ge=null,Te={};const Oe=r.getParameter(r.SCISSOR_BOX),Ye=r.getParameter(r.VIEWPORT),yt=new Et().fromArray(Oe),he=new Et().fromArray(Ye);function me(G,be,ie,de){const Ae=new Uint8Array(4),Ee=r.createTexture();r.bindTexture(G,Ee),r.texParameteri(G,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(G,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let Ge=0;Ge<ie;Ge++)G===r.TEXTURE_3D||G===r.TEXTURE_2D_ARRAY?r.texImage3D(be,0,r.RGBA,1,1,de,0,r.RGBA,r.UNSIGNED_BYTE,Ae):r.texImage2D(be+Ge,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,Ae);return Ee}const Ne={};Ne[r.TEXTURE_2D]=me(r.TEXTURE_2D,r.TEXTURE_2D,1),Ne[r.TEXTURE_CUBE_MAP]=me(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Ne[r.TEXTURE_2D_ARRAY]=me(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Ne[r.TEXTURE_3D]=me(r.TEXTURE_3D,r.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),c.setClear(0),Me(r.DEPTH_TEST),a.setFunc(Zs),ht(!1),ct(Tp),Me(r.CULL_FACE),W(mr);function Me(G){f[G]!==!0&&(r.enable(G),f[G]=!0)}function Xe(G){f[G]!==!1&&(r.disable(G),f[G]=!1)}function Ze(G,be){return p[G]!==be?(r.bindFramebuffer(G,be),p[G]=be,G===r.DRAW_FRAMEBUFFER&&(p[r.FRAMEBUFFER]=be),G===r.FRAMEBUFFER&&(p[r.DRAW_FRAMEBUFFER]=be),!0):!1}function tt(G,be){let ie=g,de=!1;if(G){ie=m.get(be),ie===void 0&&(ie=[],m.set(be,ie));const Ae=G.textures;if(ie.length!==Ae.length||ie[0]!==r.COLOR_ATTACHMENT0){for(let Ee=0,Ge=Ae.length;Ee<Ge;Ee++)ie[Ee]=r.COLOR_ATTACHMENT0+Ee;ie.length=Ae.length,de=!0}}else ie[0]!==r.BACK&&(ie[0]=r.BACK,de=!0);de&&r.drawBuffers(ie)}function St(G){return x!==G?(r.useProgram(G),x=G,!0):!1}const rt={[Jr]:r.FUNC_ADD,[lT]:r.FUNC_SUBTRACT,[uT]:r.FUNC_REVERSE_SUBTRACT};rt[hT]=r.MIN,rt[dT]=r.MAX;const At={[fT]:r.ZERO,[pT]:r.ONE,[mT]:r.SRC_COLOR,[ph]:r.SRC_ALPHA,[bT]:r.SRC_ALPHA_SATURATE,[yT]:r.DST_COLOR,[_T]:r.DST_ALPHA,[gT]:r.ONE_MINUS_SRC_COLOR,[mh]:r.ONE_MINUS_SRC_ALPHA,[xT]:r.ONE_MINUS_DST_COLOR,[vT]:r.ONE_MINUS_DST_ALPHA,[ST]:r.CONSTANT_COLOR,[MT]:r.ONE_MINUS_CONSTANT_COLOR,[TT]:r.CONSTANT_ALPHA,[ET]:r.ONE_MINUS_CONSTANT_ALPHA};function W(G,be,ie,de,Ae,Ee,Ge,ot,Vt,pt){if(G===mr){M===!0&&(Xe(r.BLEND),M=!1);return}if(M===!1&&(Me(r.BLEND),M=!0),G!==cT){if(G!==v||pt!==I){if((_!==Jr||S!==Jr)&&(r.blendEquation(r.FUNC_ADD),_=Jr,S=Jr),pt)switch(G){case Xs:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Ep:r.blendFunc(r.ONE,r.ONE);break;case Ap:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case wp:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",G);break}else switch(G){case Xs:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Ep:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Ap:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case wp:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",G);break}A=null,P=null,k=null,O=null,U.set(0,0,0),z=0,v=G,I=pt}return}Ae=Ae||be,Ee=Ee||ie,Ge=Ge||de,(be!==_||Ae!==S)&&(r.blendEquationSeparate(rt[be],rt[Ae]),_=be,S=Ae),(ie!==A||de!==P||Ee!==k||Ge!==O)&&(r.blendFuncSeparate(At[ie],At[de],At[Ee],At[Ge]),A=ie,P=de,k=Ee,O=Ge),(ot.equals(U)===!1||Vt!==z)&&(r.blendColor(ot.r,ot.g,ot.b,Vt),U.copy(ot),z=Vt),v=G,I=!1}function cn(G,be){G.side===Fn?Xe(r.CULL_FACE):Me(r.CULL_FACE);let ie=G.side===Bn;be&&(ie=!ie),ht(ie),G.blending===Xs&&G.transparent===!1?W(mr):W(G.blending,G.blendEquation,G.blendSrc,G.blendDst,G.blendEquationAlpha,G.blendSrcAlpha,G.blendDstAlpha,G.blendColor,G.blendAlpha,G.premultipliedAlpha),a.setFunc(G.depthFunc),a.setTest(G.depthTest),a.setMask(G.depthWrite),s.setMask(G.colorWrite);const de=G.stencilWrite;c.setTest(de),de&&(c.setMask(G.stencilWriteMask),c.setFunc(G.stencilFunc,G.stencilRef,G.stencilFuncMask),c.setOp(G.stencilFail,G.stencilZFail,G.stencilZPass)),st(G.polygonOffset,G.polygonOffsetFactor,G.polygonOffsetUnits),G.alphaToCoverage===!0?Me(r.SAMPLE_ALPHA_TO_COVERAGE):Xe(r.SAMPLE_ALPHA_TO_COVERAGE)}function ht(G){w!==G&&(G?r.frontFace(r.CW):r.frontFace(r.CCW),w=G)}function ct(G){G!==oT?(Me(r.CULL_FACE),G!==H&&(G===Tp?r.cullFace(r.BACK):G===aT?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):Xe(r.CULL_FACE),H=G}function Fe(G){G!==ee&&($&&r.lineWidth(G),ee=G)}function st(G,be,ie){G?(Me(r.POLYGON_OFFSET_FILL),(J!==be||oe!==ie)&&(r.polygonOffset(be,ie),J=be,oe=ie)):Xe(r.POLYGON_OFFSET_FILL)}function ke(G){G?Me(r.SCISSOR_TEST):Xe(r.SCISSOR_TEST)}function D(G){G===void 0&&(G=r.TEXTURE0+ce-1),ge!==G&&(r.activeTexture(G),ge=G)}function E(G,be,ie){ie===void 0&&(ge===null?ie=r.TEXTURE0+ce-1:ie=ge);let de=Te[ie];de===void 0&&(de={type:void 0,texture:void 0},Te[ie]=de),(de.type!==G||de.texture!==be)&&(ge!==ie&&(r.activeTexture(ie),ge=ie),r.bindTexture(G,be||Ne[G]),de.type=G,de.texture=be)}function Z(){const G=Te[ge];G!==void 0&&G.type!==void 0&&(r.bindTexture(G.type,null),G.type=void 0,G.texture=void 0)}function ue(){try{r.compressedTexImage2D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function pe(){try{r.compressedTexImage3D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function fe(){try{r.texSubImage2D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function Ue(){try{r.texSubImage3D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function Pe(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function De(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function dt(){try{r.texStorage2D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function N(){try{r.texStorage3D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function Y(){try{r.texImage2D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function ae(){try{r.texImage3D.apply(r,arguments)}catch(G){console.error("THREE.WebGLState:",G)}}function _e(G){yt.equals(G)===!1&&(r.scissor(G.x,G.y,G.z,G.w),yt.copy(G))}function xe(G){he.equals(G)===!1&&(r.viewport(G.x,G.y,G.z,G.w),he.copy(G))}function Re(G,be){let ie=h.get(be);ie===void 0&&(ie=new WeakMap,h.set(be,ie));let de=ie.get(G);de===void 0&&(de=r.getUniformBlockIndex(be,G.name),ie.set(G,de))}function qe(G,be){const de=h.get(be).get(G);u.get(be)!==de&&(r.uniformBlockBinding(be,de,G.__bindingPointIndex),u.set(be,de))}function lt(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),a.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),f={},ge=null,Te={},p={},m=new WeakMap,g=[],x=null,M=!1,v=null,_=null,A=null,P=null,S=null,k=null,O=null,U=new Ke(0,0,0),z=0,I=!1,w=null,H=null,ee=null,J=null,oe=null,yt.set(0,0,r.canvas.width,r.canvas.height),he.set(0,0,r.canvas.width,r.canvas.height),s.reset(),a.reset(),c.reset()}return{buffers:{color:s,depth:a,stencil:c},enable:Me,disable:Xe,bindFramebuffer:Ze,drawBuffers:tt,useProgram:St,setBlending:W,setMaterial:cn,setFlipSided:ht,setCullFace:ct,setLineWidth:Fe,setPolygonOffset:st,setScissorTest:ke,activeTexture:D,bindTexture:E,unbindTexture:Z,compressedTexImage2D:ue,compressedTexImage3D:pe,texImage2D:Y,texImage3D:ae,updateUBOMapping:Re,uniformBlockBinding:qe,texStorage2D:dt,texStorage3D:N,texSubImage2D:fe,texSubImage3D:Ue,compressedTexSubImage2D:Pe,compressedTexSubImage3D:De,scissor:_e,viewport:xe,reset:lt}}function Sm(r,e,t,n){const i=hR(n);switch(t){case _g:return r*e;case yg:return r*e;case xg:return r*e*2;case ud:return r*e/i.components*i.byteLength;case hd:return r*e/i.components*i.byteLength;case bg:return r*e*2/i.components*i.byteLength;case dd:return r*e*2/i.components*i.byteLength;case vg:return r*e*3/i.components*i.byteLength;case ni:return r*e*4/i.components*i.byteLength;case fd:return r*e*4/i.components*i.byteLength;case Mc:case Tc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ec:case Ac:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Ah:case Ph:return Math.max(r,16)*Math.max(e,8)/4;case Eh:case wh:return Math.max(r,8)*Math.max(e,8)/2;case Rh:case Ch:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ih:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Lh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Dh:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case Nh:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case Oh:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case Uh:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case Fh:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case Bh:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case kh:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case zh:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case Hh:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case Vh:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case Gh:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case Wh:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case jh:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case wc:case Xh:case qh:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Sg:case Yh:return Math.ceil(r/4)*Math.ceil(e/4)*8;case Kh:case Zh:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function hR(r){switch(r){case qi:case pg:return{byteLength:1,components:1};case Jo:case mg:case na:return{byteLength:2,components:1};case cd:case ld:return{byteLength:2,components:4};case ts:case ad:case di:return{byteLength:4,components:1};case gg:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function dR(r,e,t,n,i,s,a){const c=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,u=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new Qe,f=new WeakMap;let p;const m=new WeakMap;let g=!1;try{g=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function x(D,E){return g?new OffscreenCanvas(D,E):ta("canvas")}function M(D,E,Z){let ue=1;const pe=ke(D);if((pe.width>Z||pe.height>Z)&&(ue=Z/Math.max(pe.width,pe.height)),ue<1)if(typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&D instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&D instanceof ImageBitmap||typeof VideoFrame<"u"&&D instanceof VideoFrame){const fe=Math.floor(ue*pe.width),Ue=Math.floor(ue*pe.height);p===void 0&&(p=x(fe,Ue));const Pe=E?x(fe,Ue):p;return Pe.width=fe,Pe.height=Ue,Pe.getContext("2d").drawImage(D,0,0,fe,Ue),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+pe.width+"x"+pe.height+") to ("+fe+"x"+Ue+")."),Pe}else return"data"in D&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+pe.width+"x"+pe.height+")."),D;return D}function v(D){return D.generateMipmaps}function _(D){r.generateMipmap(D)}function A(D){return D.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:D.isWebGL3DRenderTarget?r.TEXTURE_3D:D.isWebGLArrayRenderTarget||D.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function P(D,E,Z,ue,pe=!1){if(D!==null){if(r[D]!==void 0)return r[D];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+D+"'")}let fe=E;if(E===r.RED&&(Z===r.FLOAT&&(fe=r.R32F),Z===r.HALF_FLOAT&&(fe=r.R16F),Z===r.UNSIGNED_BYTE&&(fe=r.R8)),E===r.RED_INTEGER&&(Z===r.UNSIGNED_BYTE&&(fe=r.R8UI),Z===r.UNSIGNED_SHORT&&(fe=r.R16UI),Z===r.UNSIGNED_INT&&(fe=r.R32UI),Z===r.BYTE&&(fe=r.R8I),Z===r.SHORT&&(fe=r.R16I),Z===r.INT&&(fe=r.R32I)),E===r.RG&&(Z===r.FLOAT&&(fe=r.RG32F),Z===r.HALF_FLOAT&&(fe=r.RG16F),Z===r.UNSIGNED_BYTE&&(fe=r.RG8)),E===r.RG_INTEGER&&(Z===r.UNSIGNED_BYTE&&(fe=r.RG8UI),Z===r.UNSIGNED_SHORT&&(fe=r.RG16UI),Z===r.UNSIGNED_INT&&(fe=r.RG32UI),Z===r.BYTE&&(fe=r.RG8I),Z===r.SHORT&&(fe=r.RG16I),Z===r.INT&&(fe=r.RG32I)),E===r.RGB_INTEGER&&(Z===r.UNSIGNED_BYTE&&(fe=r.RGB8UI),Z===r.UNSIGNED_SHORT&&(fe=r.RGB16UI),Z===r.UNSIGNED_INT&&(fe=r.RGB32UI),Z===r.BYTE&&(fe=r.RGB8I),Z===r.SHORT&&(fe=r.RGB16I),Z===r.INT&&(fe=r.RGB32I)),E===r.RGBA_INTEGER&&(Z===r.UNSIGNED_BYTE&&(fe=r.RGBA8UI),Z===r.UNSIGNED_SHORT&&(fe=r.RGBA16UI),Z===r.UNSIGNED_INT&&(fe=r.RGBA32UI),Z===r.BYTE&&(fe=r.RGBA8I),Z===r.SHORT&&(fe=r.RGBA16I),Z===r.INT&&(fe=r.RGBA32I)),E===r.RGB&&Z===r.UNSIGNED_INT_5_9_9_9_REV&&(fe=r.RGB9_E5),E===r.RGBA){const Ue=pe?Bc:bt.getTransfer(ue);Z===r.FLOAT&&(fe=r.RGBA32F),Z===r.HALF_FLOAT&&(fe=r.RGBA16F),Z===r.UNSIGNED_BYTE&&(fe=Ue===Dt?r.SRGB8_ALPHA8:r.RGBA8),Z===r.UNSIGNED_SHORT_4_4_4_4&&(fe=r.RGBA4),Z===r.UNSIGNED_SHORT_5_5_5_1&&(fe=r.RGB5_A1)}return(fe===r.R16F||fe===r.R32F||fe===r.RG16F||fe===r.RG32F||fe===r.RGBA16F||fe===r.RGBA32F)&&e.get("EXT_color_buffer_float"),fe}function S(D,E){let Z;return D?E===null||E===ts||E===eo?Z=r.DEPTH24_STENCIL8:E===di?Z=r.DEPTH32F_STENCIL8:E===Jo&&(Z=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===ts||E===eo?Z=r.DEPTH_COMPONENT24:E===di?Z=r.DEPTH_COMPONENT32F:E===Jo&&(Z=r.DEPTH_COMPONENT16),Z}function k(D,E){return v(D)===!0||D.isFramebufferTexture&&D.minFilter!==In&&D.minFilter!==Zn?Math.log2(Math.max(E.width,E.height))+1:D.mipmaps!==void 0&&D.mipmaps.length>0?D.mipmaps.length:D.isCompressedTexture&&Array.isArray(D.image)?E.mipmaps.length:1}function O(D){const E=D.target;E.removeEventListener("dispose",O),z(E),E.isVideoTexture&&f.delete(E)}function U(D){const E=D.target;E.removeEventListener("dispose",U),w(E)}function z(D){const E=n.get(D);if(E.__webglInit===void 0)return;const Z=D.source,ue=m.get(Z);if(ue){const pe=ue[E.__cacheKey];pe.usedTimes--,pe.usedTimes===0&&I(D),Object.keys(ue).length===0&&m.delete(Z)}n.remove(D)}function I(D){const E=n.get(D);r.deleteTexture(E.__webglTexture);const Z=D.source,ue=m.get(Z);delete ue[E.__cacheKey],a.memory.textures--}function w(D){const E=n.get(D);if(D.depthTexture&&(D.depthTexture.dispose(),n.remove(D.depthTexture)),D.isWebGLCubeRenderTarget)for(let ue=0;ue<6;ue++){if(Array.isArray(E.__webglFramebuffer[ue]))for(let pe=0;pe<E.__webglFramebuffer[ue].length;pe++)r.deleteFramebuffer(E.__webglFramebuffer[ue][pe]);else r.deleteFramebuffer(E.__webglFramebuffer[ue]);E.__webglDepthbuffer&&r.deleteRenderbuffer(E.__webglDepthbuffer[ue])}else{if(Array.isArray(E.__webglFramebuffer))for(let ue=0;ue<E.__webglFramebuffer.length;ue++)r.deleteFramebuffer(E.__webglFramebuffer[ue]);else r.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&r.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&r.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let ue=0;ue<E.__webglColorRenderbuffer.length;ue++)E.__webglColorRenderbuffer[ue]&&r.deleteRenderbuffer(E.__webglColorRenderbuffer[ue]);E.__webglDepthRenderbuffer&&r.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const Z=D.textures;for(let ue=0,pe=Z.length;ue<pe;ue++){const fe=n.get(Z[ue]);fe.__webglTexture&&(r.deleteTexture(fe.__webglTexture),a.memory.textures--),n.remove(Z[ue])}n.remove(D)}let H=0;function ee(){H=0}function J(){const D=H;return D>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+D+" texture units while this GPU supports only "+i.maxTextures),H+=1,D}function oe(D){const E=[];return E.push(D.wrapS),E.push(D.wrapT),E.push(D.wrapR||0),E.push(D.magFilter),E.push(D.minFilter),E.push(D.anisotropy),E.push(D.internalFormat),E.push(D.format),E.push(D.type),E.push(D.generateMipmaps),E.push(D.premultiplyAlpha),E.push(D.flipY),E.push(D.unpackAlignment),E.push(D.colorSpace),E.join()}function ce(D,E){const Z=n.get(D);if(D.isVideoTexture&&Fe(D),D.isRenderTargetTexture===!1&&D.version>0&&Z.__version!==D.version){const ue=D.image;if(ue===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ue.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{he(Z,D,E);return}}t.bindTexture(r.TEXTURE_2D,Z.__webglTexture,r.TEXTURE0+E)}function $(D,E){const Z=n.get(D);if(D.version>0&&Z.__version!==D.version){he(Z,D,E);return}t.bindTexture(r.TEXTURE_2D_ARRAY,Z.__webglTexture,r.TEXTURE0+E)}function le(D,E){const Z=n.get(D);if(D.version>0&&Z.__version!==D.version){he(Z,D,E);return}t.bindTexture(r.TEXTURE_3D,Z.__webglTexture,r.TEXTURE0+E)}function ne(D,E){const Z=n.get(D);if(D.version>0&&Z.__version!==D.version){me(Z,D,E);return}t.bindTexture(r.TEXTURE_CUBE_MAP,Z.__webglTexture,r.TEXTURE0+E)}const ge={[Qs]:r.REPEAT,[fr]:r.CLAMP_TO_EDGE,[Ic]:r.MIRRORED_REPEAT},Te={[In]:r.NEAREST,[fg]:r.NEAREST_MIPMAP_NEAREST,[Go]:r.NEAREST_MIPMAP_LINEAR,[Zn]:r.LINEAR,[Sc]:r.LINEAR_MIPMAP_NEAREST,[Vi]:r.LINEAR_MIPMAP_LINEAR},Oe={[VT]:r.NEVER,[YT]:r.ALWAYS,[GT]:r.LESS,[Ag]:r.LEQUAL,[WT]:r.EQUAL,[qT]:r.GEQUAL,[jT]:r.GREATER,[XT]:r.NOTEQUAL};function Ye(D,E){if(E.type===di&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===Zn||E.magFilter===Sc||E.magFilter===Go||E.magFilter===Vi||E.minFilter===Zn||E.minFilter===Sc||E.minFilter===Go||E.minFilter===Vi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(D,r.TEXTURE_WRAP_S,ge[E.wrapS]),r.texParameteri(D,r.TEXTURE_WRAP_T,ge[E.wrapT]),(D===r.TEXTURE_3D||D===r.TEXTURE_2D_ARRAY)&&r.texParameteri(D,r.TEXTURE_WRAP_R,ge[E.wrapR]),r.texParameteri(D,r.TEXTURE_MAG_FILTER,Te[E.magFilter]),r.texParameteri(D,r.TEXTURE_MIN_FILTER,Te[E.minFilter]),E.compareFunction&&(r.texParameteri(D,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(D,r.TEXTURE_COMPARE_FUNC,Oe[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===In||E.minFilter!==Go&&E.minFilter!==Vi||E.type===di&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");r.texParameterf(D,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,i.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function yt(D,E){let Z=!1;D.__webglInit===void 0&&(D.__webglInit=!0,E.addEventListener("dispose",O));const ue=E.source;let pe=m.get(ue);pe===void 0&&(pe={},m.set(ue,pe));const fe=oe(E);if(fe!==D.__cacheKey){pe[fe]===void 0&&(pe[fe]={texture:r.createTexture(),usedTimes:0},a.memory.textures++,Z=!0),pe[fe].usedTimes++;const Ue=pe[D.__cacheKey];Ue!==void 0&&(pe[D.__cacheKey].usedTimes--,Ue.usedTimes===0&&I(E)),D.__cacheKey=fe,D.__webglTexture=pe[fe].texture}return Z}function he(D,E,Z){let ue=r.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(ue=r.TEXTURE_2D_ARRAY),E.isData3DTexture&&(ue=r.TEXTURE_3D);const pe=yt(D,E),fe=E.source;t.bindTexture(ue,D.__webglTexture,r.TEXTURE0+Z);const Ue=n.get(fe);if(fe.version!==Ue.__version||pe===!0){t.activeTexture(r.TEXTURE0+Z);const Pe=bt.getPrimaries(bt.workingColorSpace),De=E.colorSpace===dr?null:bt.getPrimaries(E.colorSpace),dt=E.colorSpace===dr||Pe===De?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,E.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,E.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,dt);let N=M(E.image,!1,i.maxTextureSize);N=st(E,N);const Y=s.convert(E.format,E.colorSpace),ae=s.convert(E.type);let _e=P(E.internalFormat,Y,ae,E.colorSpace,E.isVideoTexture);Ye(ue,E);let xe;const Re=E.mipmaps,qe=E.isVideoTexture!==!0,lt=Ue.__version===void 0||pe===!0,G=fe.dataReady,be=k(E,N);if(E.isDepthTexture)_e=S(E.format===to,E.type),lt&&(qe?t.texStorage2D(r.TEXTURE_2D,1,_e,N.width,N.height):t.texImage2D(r.TEXTURE_2D,0,_e,N.width,N.height,0,Y,ae,null));else if(E.isDataTexture)if(Re.length>0){qe&&lt&&t.texStorage2D(r.TEXTURE_2D,be,_e,Re[0].width,Re[0].height);for(let ie=0,de=Re.length;ie<de;ie++)xe=Re[ie],qe?G&&t.texSubImage2D(r.TEXTURE_2D,ie,0,0,xe.width,xe.height,Y,ae,xe.data):t.texImage2D(r.TEXTURE_2D,ie,_e,xe.width,xe.height,0,Y,ae,xe.data);E.generateMipmaps=!1}else qe?(lt&&t.texStorage2D(r.TEXTURE_2D,be,_e,N.width,N.height),G&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,N.width,N.height,Y,ae,N.data)):t.texImage2D(r.TEXTURE_2D,0,_e,N.width,N.height,0,Y,ae,N.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){qe&&lt&&t.texStorage3D(r.TEXTURE_2D_ARRAY,be,_e,Re[0].width,Re[0].height,N.depth);for(let ie=0,de=Re.length;ie<de;ie++)if(xe=Re[ie],E.format!==ni)if(Y!==null)if(qe){if(G)if(E.layerUpdates.size>0){const Ae=Sm(xe.width,xe.height,E.format,E.type);for(const Ee of E.layerUpdates){const Ge=xe.data.subarray(Ee*Ae/xe.data.BYTES_PER_ELEMENT,(Ee+1)*Ae/xe.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,ie,0,0,Ee,xe.width,xe.height,1,Y,Ge)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,ie,0,0,0,xe.width,xe.height,N.depth,Y,xe.data)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,ie,_e,xe.width,xe.height,N.depth,0,xe.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else qe?G&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,ie,0,0,0,xe.width,xe.height,N.depth,Y,ae,xe.data):t.texImage3D(r.TEXTURE_2D_ARRAY,ie,_e,xe.width,xe.height,N.depth,0,Y,ae,xe.data)}else{qe&&lt&&t.texStorage2D(r.TEXTURE_2D,be,_e,Re[0].width,Re[0].height);for(let ie=0,de=Re.length;ie<de;ie++)xe=Re[ie],E.format!==ni?Y!==null?qe?G&&t.compressedTexSubImage2D(r.TEXTURE_2D,ie,0,0,xe.width,xe.height,Y,xe.data):t.compressedTexImage2D(r.TEXTURE_2D,ie,_e,xe.width,xe.height,0,xe.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):qe?G&&t.texSubImage2D(r.TEXTURE_2D,ie,0,0,xe.width,xe.height,Y,ae,xe.data):t.texImage2D(r.TEXTURE_2D,ie,_e,xe.width,xe.height,0,Y,ae,xe.data)}else if(E.isDataArrayTexture)if(qe){if(lt&&t.texStorage3D(r.TEXTURE_2D_ARRAY,be,_e,N.width,N.height,N.depth),G)if(E.layerUpdates.size>0){const ie=Sm(N.width,N.height,E.format,E.type);for(const de of E.layerUpdates){const Ae=N.data.subarray(de*ie/N.data.BYTES_PER_ELEMENT,(de+1)*ie/N.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,de,N.width,N.height,1,Y,ae,Ae)}E.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,N.width,N.height,N.depth,Y,ae,N.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,_e,N.width,N.height,N.depth,0,Y,ae,N.data);else if(E.isData3DTexture)qe?(lt&&t.texStorage3D(r.TEXTURE_3D,be,_e,N.width,N.height,N.depth),G&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,N.width,N.height,N.depth,Y,ae,N.data)):t.texImage3D(r.TEXTURE_3D,0,_e,N.width,N.height,N.depth,0,Y,ae,N.data);else if(E.isFramebufferTexture){if(lt)if(qe)t.texStorage2D(r.TEXTURE_2D,be,_e,N.width,N.height);else{let ie=N.width,de=N.height;for(let Ae=0;Ae<be;Ae++)t.texImage2D(r.TEXTURE_2D,Ae,_e,ie,de,0,Y,ae,null),ie>>=1,de>>=1}}else if(Re.length>0){if(qe&&lt){const ie=ke(Re[0]);t.texStorage2D(r.TEXTURE_2D,be,_e,ie.width,ie.height)}for(let ie=0,de=Re.length;ie<de;ie++)xe=Re[ie],qe?G&&t.texSubImage2D(r.TEXTURE_2D,ie,0,0,Y,ae,xe):t.texImage2D(r.TEXTURE_2D,ie,_e,Y,ae,xe);E.generateMipmaps=!1}else if(qe){if(lt){const ie=ke(N);t.texStorage2D(r.TEXTURE_2D,be,_e,ie.width,ie.height)}G&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,Y,ae,N)}else t.texImage2D(r.TEXTURE_2D,0,_e,Y,ae,N);v(E)&&_(ue),Ue.__version=fe.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function me(D,E,Z){if(E.image.length!==6)return;const ue=yt(D,E),pe=E.source;t.bindTexture(r.TEXTURE_CUBE_MAP,D.__webglTexture,r.TEXTURE0+Z);const fe=n.get(pe);if(pe.version!==fe.__version||ue===!0){t.activeTexture(r.TEXTURE0+Z);const Ue=bt.getPrimaries(bt.workingColorSpace),Pe=E.colorSpace===dr?null:bt.getPrimaries(E.colorSpace),De=E.colorSpace===dr||Ue===Pe?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,E.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,E.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,De);const dt=E.isCompressedTexture||E.image[0].isCompressedTexture,N=E.image[0]&&E.image[0].isDataTexture,Y=[];for(let de=0;de<6;de++)!dt&&!N?Y[de]=M(E.image[de],!0,i.maxCubemapSize):Y[de]=N?E.image[de].image:E.image[de],Y[de]=st(E,Y[de]);const ae=Y[0],_e=s.convert(E.format,E.colorSpace),xe=s.convert(E.type),Re=P(E.internalFormat,_e,xe,E.colorSpace),qe=E.isVideoTexture!==!0,lt=fe.__version===void 0||ue===!0,G=pe.dataReady;let be=k(E,ae);Ye(r.TEXTURE_CUBE_MAP,E);let ie;if(dt){qe&&lt&&t.texStorage2D(r.TEXTURE_CUBE_MAP,be,Re,ae.width,ae.height);for(let de=0;de<6;de++){ie=Y[de].mipmaps;for(let Ae=0;Ae<ie.length;Ae++){const Ee=ie[Ae];E.format!==ni?_e!==null?qe?G&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae,0,0,Ee.width,Ee.height,_e,Ee.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae,Re,Ee.width,Ee.height,0,Ee.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):qe?G&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae,0,0,Ee.width,Ee.height,_e,xe,Ee.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae,Re,Ee.width,Ee.height,0,_e,xe,Ee.data)}}}else{if(ie=E.mipmaps,qe&&lt){ie.length>0&&be++;const de=ke(Y[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,be,Re,de.width,de.height)}for(let de=0;de<6;de++)if(N){qe?G&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,0,0,0,Y[de].width,Y[de].height,_e,xe,Y[de].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,0,Re,Y[de].width,Y[de].height,0,_e,xe,Y[de].data);for(let Ae=0;Ae<ie.length;Ae++){const Ge=ie[Ae].image[de].image;qe?G&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae+1,0,0,Ge.width,Ge.height,_e,xe,Ge.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae+1,Re,Ge.width,Ge.height,0,_e,xe,Ge.data)}}else{qe?G&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,0,0,0,_e,xe,Y[de]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,0,Re,_e,xe,Y[de]);for(let Ae=0;Ae<ie.length;Ae++){const Ee=ie[Ae];qe?G&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae+1,0,0,_e,xe,Ee.image[de]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+de,Ae+1,Re,_e,xe,Ee.image[de])}}}v(E)&&_(r.TEXTURE_CUBE_MAP),fe.__version=pe.version,E.onUpdate&&E.onUpdate(E)}D.__version=E.version}function Ne(D,E,Z,ue,pe,fe){const Ue=s.convert(Z.format,Z.colorSpace),Pe=s.convert(Z.type),De=P(Z.internalFormat,Ue,Pe,Z.colorSpace),dt=n.get(E),N=n.get(Z);if(N.__renderTarget=E,!dt.__hasExternalTextures){const Y=Math.max(1,E.width>>fe),ae=Math.max(1,E.height>>fe);pe===r.TEXTURE_3D||pe===r.TEXTURE_2D_ARRAY?t.texImage3D(pe,fe,De,Y,ae,E.depth,0,Ue,Pe,null):t.texImage2D(pe,fe,De,Y,ae,0,Ue,Pe,null)}t.bindFramebuffer(r.FRAMEBUFFER,D),ct(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,ue,pe,N.__webglTexture,0,ht(E)):(pe===r.TEXTURE_2D||pe>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&pe<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,ue,pe,N.__webglTexture,fe),t.bindFramebuffer(r.FRAMEBUFFER,null)}function Me(D,E,Z){if(r.bindRenderbuffer(r.RENDERBUFFER,D),E.depthBuffer){const ue=E.depthTexture,pe=ue&&ue.isDepthTexture?ue.type:null,fe=S(E.stencilBuffer,pe),Ue=E.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Pe=ht(E);ct(E)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Pe,fe,E.width,E.height):Z?r.renderbufferStorageMultisample(r.RENDERBUFFER,Pe,fe,E.width,E.height):r.renderbufferStorage(r.RENDERBUFFER,fe,E.width,E.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,Ue,r.RENDERBUFFER,D)}else{const ue=E.textures;for(let pe=0;pe<ue.length;pe++){const fe=ue[pe],Ue=s.convert(fe.format,fe.colorSpace),Pe=s.convert(fe.type),De=P(fe.internalFormat,Ue,Pe,fe.colorSpace),dt=ht(E);Z&&ct(E)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,dt,De,E.width,E.height):ct(E)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,dt,De,E.width,E.height):r.renderbufferStorage(r.RENDERBUFFER,De,E.width,E.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function Xe(D,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,D),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const ue=n.get(E.depthTexture);ue.__renderTarget=E,(!ue.__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),ce(E.depthTexture,0);const pe=ue.__webglTexture,fe=ht(E);if(E.depthTexture.format===qs)ct(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,pe,0,fe):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,pe,0);else if(E.depthTexture.format===to)ct(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,pe,0,fe):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,pe,0);else throw new Error("Unknown depthTexture format")}function Ze(D){const E=n.get(D),Z=D.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==D.depthTexture){const ue=D.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),ue){const pe=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,ue.removeEventListener("dispose",pe)};ue.addEventListener("dispose",pe),E.__depthDisposeCallback=pe}E.__boundDepthTexture=ue}if(D.depthTexture&&!E.__autoAllocateDepthBuffer){if(Z)throw new Error("target.depthTexture not supported in Cube render targets");Xe(E.__webglFramebuffer,D)}else if(Z){E.__webglDepthbuffer=[];for(let ue=0;ue<6;ue++)if(t.bindFramebuffer(r.FRAMEBUFFER,E.__webglFramebuffer[ue]),E.__webglDepthbuffer[ue]===void 0)E.__webglDepthbuffer[ue]=r.createRenderbuffer(),Me(E.__webglDepthbuffer[ue],D,!1);else{const pe=D.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,fe=E.__webglDepthbuffer[ue];r.bindRenderbuffer(r.RENDERBUFFER,fe),r.framebufferRenderbuffer(r.FRAMEBUFFER,pe,r.RENDERBUFFER,fe)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=r.createRenderbuffer(),Me(E.__webglDepthbuffer,D,!1);else{const ue=D.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,pe=E.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,pe),r.framebufferRenderbuffer(r.FRAMEBUFFER,ue,r.RENDERBUFFER,pe)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function tt(D,E,Z){const ue=n.get(D);E!==void 0&&Ne(ue.__webglFramebuffer,D,D.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),Z!==void 0&&Ze(D)}function St(D){const E=D.texture,Z=n.get(D),ue=n.get(E);D.addEventListener("dispose",U);const pe=D.textures,fe=D.isWebGLCubeRenderTarget===!0,Ue=pe.length>1;if(Ue||(ue.__webglTexture===void 0&&(ue.__webglTexture=r.createTexture()),ue.__version=E.version,a.memory.textures++),fe){Z.__webglFramebuffer=[];for(let Pe=0;Pe<6;Pe++)if(E.mipmaps&&E.mipmaps.length>0){Z.__webglFramebuffer[Pe]=[];for(let De=0;De<E.mipmaps.length;De++)Z.__webglFramebuffer[Pe][De]=r.createFramebuffer()}else Z.__webglFramebuffer[Pe]=r.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){Z.__webglFramebuffer=[];for(let Pe=0;Pe<E.mipmaps.length;Pe++)Z.__webglFramebuffer[Pe]=r.createFramebuffer()}else Z.__webglFramebuffer=r.createFramebuffer();if(Ue)for(let Pe=0,De=pe.length;Pe<De;Pe++){const dt=n.get(pe[Pe]);dt.__webglTexture===void 0&&(dt.__webglTexture=r.createTexture(),a.memory.textures++)}if(D.samples>0&&ct(D)===!1){Z.__webglMultisampledFramebuffer=r.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let Pe=0;Pe<pe.length;Pe++){const De=pe[Pe];Z.__webglColorRenderbuffer[Pe]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,Z.__webglColorRenderbuffer[Pe]);const dt=s.convert(De.format,De.colorSpace),N=s.convert(De.type),Y=P(De.internalFormat,dt,N,De.colorSpace,D.isXRRenderTarget===!0),ae=ht(D);r.renderbufferStorageMultisample(r.RENDERBUFFER,ae,Y,D.width,D.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Pe,r.RENDERBUFFER,Z.__webglColorRenderbuffer[Pe])}r.bindRenderbuffer(r.RENDERBUFFER,null),D.depthBuffer&&(Z.__webglDepthRenderbuffer=r.createRenderbuffer(),Me(Z.__webglDepthRenderbuffer,D,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(fe){t.bindTexture(r.TEXTURE_CUBE_MAP,ue.__webglTexture),Ye(r.TEXTURE_CUBE_MAP,E);for(let Pe=0;Pe<6;Pe++)if(E.mipmaps&&E.mipmaps.length>0)for(let De=0;De<E.mipmaps.length;De++)Ne(Z.__webglFramebuffer[Pe][De],D,E,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Pe,De);else Ne(Z.__webglFramebuffer[Pe],D,E,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Pe,0);v(E)&&_(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ue){for(let Pe=0,De=pe.length;Pe<De;Pe++){const dt=pe[Pe],N=n.get(dt);t.bindTexture(r.TEXTURE_2D,N.__webglTexture),Ye(r.TEXTURE_2D,dt),Ne(Z.__webglFramebuffer,D,dt,r.COLOR_ATTACHMENT0+Pe,r.TEXTURE_2D,0),v(dt)&&_(r.TEXTURE_2D)}t.unbindTexture()}else{let Pe=r.TEXTURE_2D;if((D.isWebGL3DRenderTarget||D.isWebGLArrayRenderTarget)&&(Pe=D.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(Pe,ue.__webglTexture),Ye(Pe,E),E.mipmaps&&E.mipmaps.length>0)for(let De=0;De<E.mipmaps.length;De++)Ne(Z.__webglFramebuffer[De],D,E,r.COLOR_ATTACHMENT0,Pe,De);else Ne(Z.__webglFramebuffer,D,E,r.COLOR_ATTACHMENT0,Pe,0);v(E)&&_(Pe),t.unbindTexture()}D.depthBuffer&&Ze(D)}function rt(D){const E=D.textures;for(let Z=0,ue=E.length;Z<ue;Z++){const pe=E[Z];if(v(pe)){const fe=A(D),Ue=n.get(pe).__webglTexture;t.bindTexture(fe,Ue),_(fe),t.unbindTexture()}}}const At=[],W=[];function cn(D){if(D.samples>0){if(ct(D)===!1){const E=D.textures,Z=D.width,ue=D.height;let pe=r.COLOR_BUFFER_BIT;const fe=D.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Ue=n.get(D),Pe=E.length>1;if(Pe)for(let De=0;De<E.length;De++)t.bindFramebuffer(r.FRAMEBUFFER,Ue.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+De,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,Ue.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+De,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,Ue.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Ue.__webglFramebuffer);for(let De=0;De<E.length;De++){if(D.resolveDepthBuffer&&(D.depthBuffer&&(pe|=r.DEPTH_BUFFER_BIT),D.stencilBuffer&&D.resolveStencilBuffer&&(pe|=r.STENCIL_BUFFER_BIT)),Pe){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,Ue.__webglColorRenderbuffer[De]);const dt=n.get(E[De]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,dt,0)}r.blitFramebuffer(0,0,Z,ue,0,0,Z,ue,pe,r.NEAREST),u===!0&&(At.length=0,W.length=0,At.push(r.COLOR_ATTACHMENT0+De),D.depthBuffer&&D.resolveDepthBuffer===!1&&(At.push(fe),W.push(fe),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,W)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,At))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),Pe)for(let De=0;De<E.length;De++){t.bindFramebuffer(r.FRAMEBUFFER,Ue.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+De,r.RENDERBUFFER,Ue.__webglColorRenderbuffer[De]);const dt=n.get(E[De]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,Ue.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+De,r.TEXTURE_2D,dt,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Ue.__webglMultisampledFramebuffer)}else if(D.depthBuffer&&D.resolveDepthBuffer===!1&&u){const E=D.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[E])}}}function ht(D){return Math.min(i.maxSamples,D.samples)}function ct(D){const E=n.get(D);return D.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function Fe(D){const E=a.render.frame;f.get(D)!==E&&(f.set(D,E),D.update())}function st(D,E){const Z=D.colorSpace,ue=D.format,pe=D.type;return D.isCompressedTexture===!0||D.isVideoTexture===!0||Z!==Ln&&Z!==dr&&(bt.getTransfer(Z)===Dt?(ue!==ni||pe!==qi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Z)),E}function ke(D){return typeof HTMLImageElement<"u"&&D instanceof HTMLImageElement?(h.width=D.naturalWidth||D.width,h.height=D.naturalHeight||D.height):typeof VideoFrame<"u"&&D instanceof VideoFrame?(h.width=D.displayWidth,h.height=D.displayHeight):(h.width=D.width,h.height=D.height),h}this.allocateTextureUnit=J,this.resetTextureUnits=ee,this.setTexture2D=ce,this.setTexture2DArray=$,this.setTexture3D=le,this.setTextureCube=ne,this.rebindTextures=tt,this.setupRenderTarget=St,this.updateRenderTargetMipmap=rt,this.updateMultisampleRenderTarget=cn,this.setupDepthRenderbuffer=Ze,this.setupFrameBufferTexture=Ne,this.useMultisampledRTT=ct}function fR(r,e){function t(n,i=dr){let s;const a=bt.getTransfer(i);if(n===qi)return r.UNSIGNED_BYTE;if(n===cd)return r.UNSIGNED_SHORT_4_4_4_4;if(n===ld)return r.UNSIGNED_SHORT_5_5_5_1;if(n===gg)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===pg)return r.BYTE;if(n===mg)return r.SHORT;if(n===Jo)return r.UNSIGNED_SHORT;if(n===ad)return r.INT;if(n===ts)return r.UNSIGNED_INT;if(n===di)return r.FLOAT;if(n===na)return r.HALF_FLOAT;if(n===_g)return r.ALPHA;if(n===vg)return r.RGB;if(n===ni)return r.RGBA;if(n===yg)return r.LUMINANCE;if(n===xg)return r.LUMINANCE_ALPHA;if(n===qs)return r.DEPTH_COMPONENT;if(n===to)return r.DEPTH_STENCIL;if(n===ud)return r.RED;if(n===hd)return r.RED_INTEGER;if(n===bg)return r.RG;if(n===dd)return r.RG_INTEGER;if(n===fd)return r.RGBA_INTEGER;if(n===Mc||n===Tc||n===Ec||n===Ac)if(a===Dt)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===Mc)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Tc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ec)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Ac)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===Mc)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Tc)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ec)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Ac)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Eh||n===Ah||n===wh||n===Ph)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===Eh)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ah)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===wh)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Ph)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Rh||n===Ch||n===Ih)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Rh||n===Ch)return a===Dt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Ih)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Lh||n===Dh||n===Nh||n===Oh||n===Uh||n===Fh||n===Bh||n===kh||n===zh||n===Hh||n===Vh||n===Gh||n===Wh||n===jh)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Lh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Dh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Nh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Oh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Uh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Fh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===Bh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===kh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===zh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Hh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Vh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Gh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Wh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===jh)return a===Dt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===wc||n===Xh||n===qh)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===wc)return a===Dt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Xh)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===qh)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Sg||n===Yh||n===Kh||n===Zh)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===wc)return s.COMPRESSED_RED_RGTC1_EXT;if(n===Yh)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Kh)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Zh)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===eo?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class pR extends Cn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Wi extends Ht{constructor(){super(),this.isGroup=!0,this.type="Group"}}const mR={type:"move"};class Yu{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Wi,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Wi,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new F,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new F),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Wi,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new F,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new F),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,a=null;const c=this._targetRay,u=this._grip,h=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(h&&e.hand){a=!0;for(const M of e.hand.values()){const v=t.getJointPose(M,n),_=this._getHandJoint(h,M);v!==null&&(_.matrix.fromArray(v.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=v.radius),_.visible=v!==null}const f=h.joints["index-finger-tip"],p=h.joints["thumb-tip"],m=f.position.distanceTo(p.position),g=.02,x=.005;h.inputState.pinching&&m>g+x?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!h.inputState.pinching&&m<=g-x&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else u!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(u.matrix.fromArray(s.transform.matrix),u.matrix.decompose(u.position,u.rotation,u.scale),u.matrixWorldNeedsUpdate=!0,s.linearVelocity?(u.hasLinearVelocity=!0,u.linearVelocity.copy(s.linearVelocity)):u.hasLinearVelocity=!1,s.angularVelocity?(u.hasAngularVelocity=!0,u.angularVelocity.copy(s.angularVelocity)):u.hasAngularVelocity=!1));c!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(c.matrix.fromArray(i.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,i.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(i.linearVelocity)):c.hasLinearVelocity=!1,i.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(i.angularVelocity)):c.hasAngularVelocity=!1,this.dispatchEvent(mR)))}return c!==null&&(c.visible=i!==null),u!==null&&(u.visible=s!==null),h!==null&&(h.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Wi;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const gR=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,_R=`
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

}`;class vR{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new fn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new _r({vertexShader:gR,fragmentShader:_R,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new we(new ao(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class yR extends vr{constructor(e,t){super();const n=this;let i=null,s=1,a=null,c="local-floor",u=1,h=null,f=null,p=null,m=null,g=null,x=null;const M=new vR,v=t.getContextAttributes();let _=null,A=null;const P=[],S=[],k=new Qe;let O=null;const U=new Cn;U.viewport=new Et;const z=new Cn;z.viewport=new Et;const I=[U,z],w=new pR;let H=null,ee=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(he){let me=P[he];return me===void 0&&(me=new Yu,P[he]=me),me.getTargetRaySpace()},this.getControllerGrip=function(he){let me=P[he];return me===void 0&&(me=new Yu,P[he]=me),me.getGripSpace()},this.getHand=function(he){let me=P[he];return me===void 0&&(me=new Yu,P[he]=me),me.getHandSpace()};function J(he){const me=S.indexOf(he.inputSource);if(me===-1)return;const Ne=P[me];Ne!==void 0&&(Ne.update(he.inputSource,he.frame,h||a),Ne.dispatchEvent({type:he.type,data:he.inputSource}))}function oe(){i.removeEventListener("select",J),i.removeEventListener("selectstart",J),i.removeEventListener("selectend",J),i.removeEventListener("squeeze",J),i.removeEventListener("squeezestart",J),i.removeEventListener("squeezeend",J),i.removeEventListener("end",oe),i.removeEventListener("inputsourceschange",ce);for(let he=0;he<P.length;he++){const me=S[he];me!==null&&(S[he]=null,P[he].disconnect(me))}H=null,ee=null,M.reset(),e.setRenderTarget(_),g=null,m=null,p=null,i=null,A=null,yt.stop(),n.isPresenting=!1,e.setPixelRatio(O),e.setSize(k.width,k.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(he){s=he,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(he){c=he,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||a},this.setReferenceSpace=function(he){h=he},this.getBaseLayer=function(){return m!==null?m:g},this.getBinding=function(){return p},this.getFrame=function(){return x},this.getSession=function(){return i},this.setSession=async function(he){if(i=he,i!==null){if(_=e.getRenderTarget(),i.addEventListener("select",J),i.addEventListener("selectstart",J),i.addEventListener("selectend",J),i.addEventListener("squeeze",J),i.addEventListener("squeezestart",J),i.addEventListener("squeezeend",J),i.addEventListener("end",oe),i.addEventListener("inputsourceschange",ce),v.xrCompatible!==!0&&await t.makeXRCompatible(),O=e.getPixelRatio(),e.getSize(k),i.renderState.layers===void 0){const me={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};g=new XRWebGLLayer(i,t,me),i.updateRenderState({baseLayer:g}),e.setPixelRatio(1),e.setSize(g.framebufferWidth,g.framebufferHeight,!1),A=new ns(g.framebufferWidth,g.framebufferHeight,{format:ni,type:qi,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil})}else{let me=null,Ne=null,Me=null;v.depth&&(Me=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,me=v.stencil?to:qs,Ne=v.stencil?eo:ts);const Xe={colorFormat:t.RGBA8,depthFormat:Me,scaleFactor:s};p=new XRWebGLBinding(i,t),m=p.createProjectionLayer(Xe),i.updateRenderState({layers:[m]}),e.setPixelRatio(1),e.setSize(m.textureWidth,m.textureHeight,!1),A=new ns(m.textureWidth,m.textureHeight,{format:ni,type:qi,depthTexture:new Bg(m.textureWidth,m.textureHeight,Ne,void 0,void 0,void 0,void 0,void 0,void 0,me),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:m.ignoreDepthValues===!1})}A.isXRRenderTarget=!0,this.setFoveation(u),h=null,a=await i.requestReferenceSpace(c),yt.setContext(i),yt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return M.getDepthTexture()};function ce(he){for(let me=0;me<he.removed.length;me++){const Ne=he.removed[me],Me=S.indexOf(Ne);Me>=0&&(S[Me]=null,P[Me].disconnect(Ne))}for(let me=0;me<he.added.length;me++){const Ne=he.added[me];let Me=S.indexOf(Ne);if(Me===-1){for(let Ze=0;Ze<P.length;Ze++)if(Ze>=S.length){S.push(Ne),Me=Ze;break}else if(S[Ze]===null){S[Ze]=Ne,Me=Ze;break}if(Me===-1)break}const Xe=P[Me];Xe&&Xe.connect(Ne)}}const $=new F,le=new F;function ne(he,me,Ne){$.setFromMatrixPosition(me.matrixWorld),le.setFromMatrixPosition(Ne.matrixWorld);const Me=$.distanceTo(le),Xe=me.projectionMatrix.elements,Ze=Ne.projectionMatrix.elements,tt=Xe[14]/(Xe[10]-1),St=Xe[14]/(Xe[10]+1),rt=(Xe[9]+1)/Xe[5],At=(Xe[9]-1)/Xe[5],W=(Xe[8]-1)/Xe[0],cn=(Ze[8]+1)/Ze[0],ht=tt*W,ct=tt*cn,Fe=Me/(-W+cn),st=Fe*-W;if(me.matrixWorld.decompose(he.position,he.quaternion,he.scale),he.translateX(st),he.translateZ(Fe),he.matrixWorld.compose(he.position,he.quaternion,he.scale),he.matrixWorldInverse.copy(he.matrixWorld).invert(),Xe[10]===-1)he.projectionMatrix.copy(me.projectionMatrix),he.projectionMatrixInverse.copy(me.projectionMatrixInverse);else{const ke=tt+Fe,D=St+Fe,E=ht-st,Z=ct+(Me-st),ue=rt*St/D*ke,pe=At*St/D*ke;he.projectionMatrix.makePerspective(E,Z,ue,pe,ke,D),he.projectionMatrixInverse.copy(he.projectionMatrix).invert()}}function ge(he,me){me===null?he.matrixWorld.copy(he.matrix):he.matrixWorld.multiplyMatrices(me.matrixWorld,he.matrix),he.matrixWorldInverse.copy(he.matrixWorld).invert()}this.updateCamera=function(he){if(i===null)return;let me=he.near,Ne=he.far;M.texture!==null&&(M.depthNear>0&&(me=M.depthNear),M.depthFar>0&&(Ne=M.depthFar)),w.near=z.near=U.near=me,w.far=z.far=U.far=Ne,(H!==w.near||ee!==w.far)&&(i.updateRenderState({depthNear:w.near,depthFar:w.far}),H=w.near,ee=w.far),U.layers.mask=he.layers.mask|2,z.layers.mask=he.layers.mask|4,w.layers.mask=U.layers.mask|z.layers.mask;const Me=he.parent,Xe=w.cameras;ge(w,Me);for(let Ze=0;Ze<Xe.length;Ze++)ge(Xe[Ze],Me);Xe.length===2?ne(w,U,z):w.projectionMatrix.copy(U.projectionMatrix),Te(he,w,Me)};function Te(he,me,Ne){Ne===null?he.matrix.copy(me.matrixWorld):(he.matrix.copy(Ne.matrixWorld),he.matrix.invert(),he.matrix.multiply(me.matrixWorld)),he.matrix.decompose(he.position,he.quaternion,he.scale),he.updateMatrixWorld(!0),he.projectionMatrix.copy(me.projectionMatrix),he.projectionMatrixInverse.copy(me.projectionMatrixInverse),he.isPerspectiveCamera&&(he.fov=no*2*Math.atan(1/he.projectionMatrix.elements[5]),he.zoom=1)}this.getCamera=function(){return w},this.getFoveation=function(){if(!(m===null&&g===null))return u},this.setFoveation=function(he){u=he,m!==null&&(m.fixedFoveation=he),g!==null&&g.fixedFoveation!==void 0&&(g.fixedFoveation=he)},this.hasDepthSensing=function(){return M.texture!==null},this.getDepthSensingMesh=function(){return M.getMesh(w)};let Oe=null;function Ye(he,me){if(f=me.getViewerPose(h||a),x=me,f!==null){const Ne=f.views;g!==null&&(e.setRenderTargetFramebuffer(A,g.framebuffer),e.setRenderTarget(A));let Me=!1;Ne.length!==w.cameras.length&&(w.cameras.length=0,Me=!0);for(let Ze=0;Ze<Ne.length;Ze++){const tt=Ne[Ze];let St=null;if(g!==null)St=g.getViewport(tt);else{const At=p.getViewSubImage(m,tt);St=At.viewport,Ze===0&&(e.setRenderTargetTextures(A,At.colorTexture,m.ignoreDepthValues?void 0:At.depthStencilTexture),e.setRenderTarget(A))}let rt=I[Ze];rt===void 0&&(rt=new Cn,rt.layers.enable(Ze),rt.viewport=new Et,I[Ze]=rt),rt.matrix.fromArray(tt.transform.matrix),rt.matrix.decompose(rt.position,rt.quaternion,rt.scale),rt.projectionMatrix.fromArray(tt.projectionMatrix),rt.projectionMatrixInverse.copy(rt.projectionMatrix).invert(),rt.viewport.set(St.x,St.y,St.width,St.height),Ze===0&&(w.matrix.copy(rt.matrix),w.matrix.decompose(w.position,w.quaternion,w.scale)),Me===!0&&w.cameras.push(rt)}const Xe=i.enabledFeatures;if(Xe&&Xe.includes("depth-sensing")){const Ze=p.getDepthInformation(Ne[0]);Ze&&Ze.isValid&&Ze.texture&&M.init(e,Ze,i.renderState)}}for(let Ne=0;Ne<P.length;Ne++){const Me=S[Ne],Xe=P[Ne];Me!==null&&Xe!==void 0&&Xe.update(Me,me,h||a)}Oe&&Oe(he,me),me.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:me}),x=null}const yt=new Fg;yt.setAnimationLoop(Ye),this.setAnimationLoop=function(he){Oe=he},this.dispose=function(){}}}const qr=new pi,xR=new nt;function bR(r,e){function t(v,_){v.matrixAutoUpdate===!0&&v.updateMatrix(),_.value.copy(v.matrix)}function n(v,_){_.color.getRGB(v.fogColor.value,Ng(r)),_.isFog?(v.fogNear.value=_.near,v.fogFar.value=_.far):_.isFogExp2&&(v.fogDensity.value=_.density)}function i(v,_,A,P,S){_.isMeshBasicMaterial||_.isMeshLambertMaterial?s(v,_):_.isMeshToonMaterial?(s(v,_),p(v,_)):_.isMeshPhongMaterial?(s(v,_),f(v,_)):_.isMeshStandardMaterial?(s(v,_),m(v,_),_.isMeshPhysicalMaterial&&g(v,_,S)):_.isMeshMatcapMaterial?(s(v,_),x(v,_)):_.isMeshDepthMaterial?s(v,_):_.isMeshDistanceMaterial?(s(v,_),M(v,_)):_.isMeshNormalMaterial?s(v,_):_.isLineBasicMaterial?(a(v,_),_.isLineDashedMaterial&&c(v,_)):_.isPointsMaterial?u(v,_,A,P):_.isSpriteMaterial?h(v,_):_.isShadowMaterial?(v.color.value.copy(_.color),v.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function s(v,_){v.opacity.value=_.opacity,_.color&&v.diffuse.value.copy(_.color),_.emissive&&v.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.bumpMap&&(v.bumpMap.value=_.bumpMap,t(_.bumpMap,v.bumpMapTransform),v.bumpScale.value=_.bumpScale,_.side===Bn&&(v.bumpScale.value*=-1)),_.normalMap&&(v.normalMap.value=_.normalMap,t(_.normalMap,v.normalMapTransform),v.normalScale.value.copy(_.normalScale),_.side===Bn&&v.normalScale.value.negate()),_.displacementMap&&(v.displacementMap.value=_.displacementMap,t(_.displacementMap,v.displacementMapTransform),v.displacementScale.value=_.displacementScale,v.displacementBias.value=_.displacementBias),_.emissiveMap&&(v.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,v.emissiveMapTransform)),_.specularMap&&(v.specularMap.value=_.specularMap,t(_.specularMap,v.specularMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest);const A=e.get(_),P=A.envMap,S=A.envMapRotation;P&&(v.envMap.value=P,qr.copy(S),qr.x*=-1,qr.y*=-1,qr.z*=-1,P.isCubeTexture&&P.isRenderTargetTexture===!1&&(qr.y*=-1,qr.z*=-1),v.envMapRotation.value.setFromMatrix4(xR.makeRotationFromEuler(qr)),v.flipEnvMap.value=P.isCubeTexture&&P.isRenderTargetTexture===!1?-1:1,v.reflectivity.value=_.reflectivity,v.ior.value=_.ior,v.refractionRatio.value=_.refractionRatio),_.lightMap&&(v.lightMap.value=_.lightMap,v.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,v.lightMapTransform)),_.aoMap&&(v.aoMap.value=_.aoMap,v.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,v.aoMapTransform))}function a(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform))}function c(v,_){v.dashSize.value=_.dashSize,v.totalSize.value=_.dashSize+_.gapSize,v.scale.value=_.scale}function u(v,_,A,P){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.size.value=_.size*A,v.scale.value=P*.5,_.map&&(v.map.value=_.map,t(_.map,v.uvTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function h(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.rotation.value=_.rotation,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function f(v,_){v.specular.value.copy(_.specular),v.shininess.value=Math.max(_.shininess,1e-4)}function p(v,_){_.gradientMap&&(v.gradientMap.value=_.gradientMap)}function m(v,_){v.metalness.value=_.metalness,_.metalnessMap&&(v.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,v.metalnessMapTransform)),v.roughness.value=_.roughness,_.roughnessMap&&(v.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,v.roughnessMapTransform)),_.envMap&&(v.envMapIntensity.value=_.envMapIntensity)}function g(v,_,A){v.ior.value=_.ior,_.sheen>0&&(v.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),v.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(v.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,v.sheenColorMapTransform)),_.sheenRoughnessMap&&(v.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,v.sheenRoughnessMapTransform))),_.clearcoat>0&&(v.clearcoat.value=_.clearcoat,v.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(v.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,v.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(v.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===Bn&&v.clearcoatNormalScale.value.negate())),_.dispersion>0&&(v.dispersion.value=_.dispersion),_.iridescence>0&&(v.iridescence.value=_.iridescence,v.iridescenceIOR.value=_.iridescenceIOR,v.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(v.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,v.iridescenceMapTransform)),_.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),_.transmission>0&&(v.transmission.value=_.transmission,v.transmissionSamplerMap.value=A.texture,v.transmissionSamplerSize.value.set(A.width,A.height),_.transmissionMap&&(v.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,v.transmissionMapTransform)),v.thickness.value=_.thickness,_.thicknessMap&&(v.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=_.attenuationDistance,v.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(v.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(v.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=_.specularIntensity,v.specularColor.value.copy(_.specularColor),_.specularColorMap&&(v.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,v.specularColorMapTransform)),_.specularIntensityMap&&(v.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,v.specularIntensityMapTransform))}function x(v,_){_.matcap&&(v.matcap.value=_.matcap)}function M(v,_){const A=e.get(_).light;v.referencePosition.value.setFromMatrixPosition(A.matrixWorld),v.nearDistance.value=A.shadow.camera.near,v.farDistance.value=A.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function SR(r,e,t,n){let i={},s={},a=[];const c=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function u(A,P){const S=P.program;n.uniformBlockBinding(A,S)}function h(A,P){let S=i[A.id];S===void 0&&(x(A),S=f(A),i[A.id]=S,A.addEventListener("dispose",v));const k=P.program;n.updateUBOMapping(A,k);const O=e.render.frame;s[A.id]!==O&&(m(A),s[A.id]=O)}function f(A){const P=p();A.__bindingPointIndex=P;const S=r.createBuffer(),k=A.__size,O=A.usage;return r.bindBuffer(r.UNIFORM_BUFFER,S),r.bufferData(r.UNIFORM_BUFFER,k,O),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,P,S),S}function p(){for(let A=0;A<c;A++)if(a.indexOf(A)===-1)return a.push(A),A;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function m(A){const P=i[A.id],S=A.uniforms,k=A.__cache;r.bindBuffer(r.UNIFORM_BUFFER,P);for(let O=0,U=S.length;O<U;O++){const z=Array.isArray(S[O])?S[O]:[S[O]];for(let I=0,w=z.length;I<w;I++){const H=z[I];if(g(H,O,I,k)===!0){const ee=H.__offset,J=Array.isArray(H.value)?H.value:[H.value];let oe=0;for(let ce=0;ce<J.length;ce++){const $=J[ce],le=M($);typeof $=="number"||typeof $=="boolean"?(H.__data[0]=$,r.bufferSubData(r.UNIFORM_BUFFER,ee+oe,H.__data)):$.isMatrix3?(H.__data[0]=$.elements[0],H.__data[1]=$.elements[1],H.__data[2]=$.elements[2],H.__data[3]=0,H.__data[4]=$.elements[3],H.__data[5]=$.elements[4],H.__data[6]=$.elements[5],H.__data[7]=0,H.__data[8]=$.elements[6],H.__data[9]=$.elements[7],H.__data[10]=$.elements[8],H.__data[11]=0):($.toArray(H.__data,oe),oe+=le.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,ee,H.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function g(A,P,S,k){const O=A.value,U=P+"_"+S;if(k[U]===void 0)return typeof O=="number"||typeof O=="boolean"?k[U]=O:k[U]=O.clone(),!0;{const z=k[U];if(typeof O=="number"||typeof O=="boolean"){if(z!==O)return k[U]=O,!0}else if(z.equals(O)===!1)return z.copy(O),!0}return!1}function x(A){const P=A.uniforms;let S=0;const k=16;for(let U=0,z=P.length;U<z;U++){const I=Array.isArray(P[U])?P[U]:[P[U]];for(let w=0,H=I.length;w<H;w++){const ee=I[w],J=Array.isArray(ee.value)?ee.value:[ee.value];for(let oe=0,ce=J.length;oe<ce;oe++){const $=J[oe],le=M($),ne=S%k,ge=ne%le.boundary,Te=ne+ge;S+=ge,Te!==0&&k-Te<le.storage&&(S+=k-Te),ee.__data=new Float32Array(le.storage/Float32Array.BYTES_PER_ELEMENT),ee.__offset=S,S+=le.storage}}}const O=S%k;return O>0&&(S+=k-O),A.__size=S,A.__cache={},this}function M(A){const P={boundary:0,storage:0};return typeof A=="number"||typeof A=="boolean"?(P.boundary=4,P.storage=4):A.isVector2?(P.boundary=8,P.storage=8):A.isVector3||A.isColor?(P.boundary=16,P.storage=12):A.isVector4?(P.boundary=16,P.storage=16):A.isMatrix3?(P.boundary=48,P.storage=48):A.isMatrix4?(P.boundary=64,P.storage=64):A.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",A),P}function v(A){const P=A.target;P.removeEventListener("dispose",v);const S=a.indexOf(P.__bindingPointIndex);a.splice(S,1),r.deleteBuffer(i[P.id]),delete i[P.id],delete s[P.id]}function _(){for(const A in i)r.deleteBuffer(i[A]);a=[],i={},s={}}return{bind:u,update:h,dispose:_}}class MR{constructor(e={}){const{canvas:t=hE(),context:n=null,depth:i=!0,stencil:s=!1,alpha:a=!1,antialias:c=!1,premultipliedAlpha:u=!0,preserveDrawingBuffer:h=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:p=!1,reverseDepthBuffer:m=!1}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");g=n.getContextAttributes().alpha}else g=a;const x=new Uint32Array(4),M=new Int32Array(4);let v=null,_=null;const A=[],P=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=dn,this.toneMapping=gr,this.toneMappingExposure=1;const S=this;let k=!1,O=0,U=0,z=null,I=-1,w=null;const H=new Et,ee=new Et;let J=null;const oe=new Ke(0);let ce=0,$=t.width,le=t.height,ne=1,ge=null,Te=null;const Oe=new Et(0,0,$,le),Ye=new Et(0,0,$,le);let yt=!1;const he=new _d;let me=!1,Ne=!1;const Me=new nt,Xe=new nt,Ze=new F,tt=new Et,St={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let rt=!1;function At(){return z===null?ne:1}let W=n;function cn(R,j){return t.getContext(R,j)}try{const R={alpha:!0,depth:i,stencil:s,antialias:c,premultipliedAlpha:u,preserveDrawingBuffer:h,powerPreference:f,failIfMajorPerformanceCaveat:p};if("setAttribute"in t&&t.setAttribute("data-engine","three.js r170"),t.addEventListener("webglcontextlost",de,!1),t.addEventListener("webglcontextrestored",Ae,!1),t.addEventListener("webglcontextcreationerror",Ee,!1),W===null){const j="webgl2";if(W=cn(j,R),W===null)throw cn(j)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(R){throw console.error("THREE.WebGLRenderer: "+R.message),R}let ht,ct,Fe,st,ke,D,E,Z,ue,pe,fe,Ue,Pe,De,dt,N,Y,ae,_e,xe,Re,qe,lt,G;function be(){ht=new P1(W),ht.init(),qe=new fR(W,ht),ct=new S1(W,ht,e,qe),Fe=new uR(W,ht),ct.reverseDepthBuffer&&m&&Fe.buffers.depth.setReversed(!0),st=new I1(W),ke=new KP,D=new dR(W,ht,Fe,ke,ct,qe,st),E=new T1(S),Z=new w1(S),ue=new BE(W),lt=new x1(W,ue),pe=new R1(W,ue,st,lt),fe=new D1(W,pe,ue,st),_e=new L1(W,ct,D),N=new M1(ke),Ue=new YP(S,E,Z,ht,ct,lt,N),Pe=new bR(S,ke),De=new $P,dt=new iR(ht),ae=new y1(S,E,Z,Fe,fe,g,u),Y=new cR(S,fe,ct),G=new SR(W,st,ct,Fe),xe=new b1(W,ht,st),Re=new C1(W,ht,st),st.programs=Ue.programs,S.capabilities=ct,S.extensions=ht,S.properties=ke,S.renderLists=De,S.shadowMap=Y,S.state=Fe,S.info=st}be();const ie=new yR(S,W);this.xr=ie,this.getContext=function(){return W},this.getContextAttributes=function(){return W.getContextAttributes()},this.forceContextLoss=function(){const R=ht.get("WEBGL_lose_context");R&&R.loseContext()},this.forceContextRestore=function(){const R=ht.get("WEBGL_lose_context");R&&R.restoreContext()},this.getPixelRatio=function(){return ne},this.setPixelRatio=function(R){R!==void 0&&(ne=R,this.setSize($,le,!1))},this.getSize=function(R){return R.set($,le)},this.setSize=function(R,j,Q=!0){if(ie.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}$=R,le=j,t.width=Math.floor(R*ne),t.height=Math.floor(j*ne),Q===!0&&(t.style.width=R+"px",t.style.height=j+"px"),this.setViewport(0,0,R,j)},this.getDrawingBufferSize=function(R){return R.set($*ne,le*ne).floor()},this.setDrawingBufferSize=function(R,j,Q){$=R,le=j,ne=Q,t.width=Math.floor(R*Q),t.height=Math.floor(j*Q),this.setViewport(0,0,R,j)},this.getCurrentViewport=function(R){return R.copy(H)},this.getViewport=function(R){return R.copy(Oe)},this.setViewport=function(R,j,Q,te){R.isVector4?Oe.set(R.x,R.y,R.z,R.w):Oe.set(R,j,Q,te),Fe.viewport(H.copy(Oe).multiplyScalar(ne).round())},this.getScissor=function(R){return R.copy(Ye)},this.setScissor=function(R,j,Q,te){R.isVector4?Ye.set(R.x,R.y,R.z,R.w):Ye.set(R,j,Q,te),Fe.scissor(ee.copy(Ye).multiplyScalar(ne).round())},this.getScissorTest=function(){return yt},this.setScissorTest=function(R){Fe.setScissorTest(yt=R)},this.setOpaqueSort=function(R){ge=R},this.setTransparentSort=function(R){Te=R},this.getClearColor=function(R){return R.copy(ae.getClearColor())},this.setClearColor=function(){ae.setClearColor.apply(ae,arguments)},this.getClearAlpha=function(){return ae.getClearAlpha()},this.setClearAlpha=function(){ae.setClearAlpha.apply(ae,arguments)},this.clear=function(R=!0,j=!0,Q=!0){let te=0;if(R){let X=!1;if(z!==null){const Se=z.texture.format;X=Se===fd||Se===dd||Se===hd}if(X){const Se=z.texture.type,Le=Se===qi||Se===ts||Se===Jo||Se===eo||Se===cd||Se===ld,ze=ae.getClearColor(),He=ae.getClearAlpha(),et=ze.r,$e=ze.g,Ve=ze.b;Le?(x[0]=et,x[1]=$e,x[2]=Ve,x[3]=He,W.clearBufferuiv(W.COLOR,0,x)):(M[0]=et,M[1]=$e,M[2]=Ve,M[3]=He,W.clearBufferiv(W.COLOR,0,M))}else te|=W.COLOR_BUFFER_BIT}j&&(te|=W.DEPTH_BUFFER_BIT),Q&&(te|=W.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),W.clear(te)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",de,!1),t.removeEventListener("webglcontextrestored",Ae,!1),t.removeEventListener("webglcontextcreationerror",Ee,!1),De.dispose(),dt.dispose(),ke.dispose(),E.dispose(),Z.dispose(),fe.dispose(),lt.dispose(),G.dispose(),Ue.dispose(),ie.dispose(),ie.removeEventListener("sessionstart",as),ie.removeEventListener("sessionend",cs),ri.stop()};function de(R){R.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),k=!0}function Ae(){console.log("THREE.WebGLRenderer: Context Restored."),k=!1;const R=st.autoReset,j=Y.enabled,Q=Y.autoUpdate,te=Y.needsUpdate,X=Y.type;be(),st.autoReset=R,Y.enabled=j,Y.autoUpdate=Q,Y.needsUpdate=te,Y.type=X}function Ee(R){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",R.statusMessage)}function Ge(R){const j=R.target;j.removeEventListener("dispose",Ge),ot(j)}function ot(R){Vt(R),ke.remove(R)}function Vt(R){const j=ke.get(R).programs;j!==void 0&&(j.forEach(function(Q){Ue.releaseProgram(Q)}),R.isShaderMaterial&&Ue.releaseShaderCache(R))}this.renderBufferDirect=function(R,j,Q,te,X,Se){j===null&&(j=St);const Le=X.isMesh&&X.matrixWorld.determinant()<0,ze=ho(R,j,Q,te,X);Fe.setMaterial(te,Le);let He=Q.index,et=1;if(te.wireframe===!0){if(He=pe.getWireframeAttribute(Q),He===void 0)return;et=2}const $e=Q.drawRange,Ve=Q.attributes.position;let vt=$e.start*et,wt=($e.start+$e.count)*et;Se!==null&&(vt=Math.max(vt,Se.start*et),wt=Math.min(wt,(Se.start+Se.count)*et)),He!==null?(vt=Math.max(vt,0),wt=Math.min(wt,He.count)):Ve!=null&&(vt=Math.max(vt,0),wt=Math.min(wt,Ve.count));const Rt=wt-vt;if(Rt<0||Rt===1/0)return;lt.setup(X,te,ze,Q,He);let qt,xt=xe;if(He!==null&&(qt=ue.get(He),xt=Re,xt.setIndex(qt)),X.isMesh)te.wireframe===!0?(Fe.setLineWidth(te.wireframeLinewidth*At()),xt.setMode(W.LINES)):xt.setMode(W.TRIANGLES);else if(X.isLine){let We=te.linewidth;We===void 0&&(We=1),Fe.setLineWidth(We*At()),X.isLineSegments?xt.setMode(W.LINES):X.isLineLoop?xt.setMode(W.LINE_LOOP):xt.setMode(W.LINE_STRIP)}else X.isPoints?xt.setMode(W.POINTS):X.isSprite&&xt.setMode(W.TRIANGLES);if(X.isBatchedMesh)if(X._multiDrawInstances!==null)xt.renderMultiDrawInstances(X._multiDrawStarts,X._multiDrawCounts,X._multiDrawCount,X._multiDrawInstances);else if(ht.get("WEBGL_multi_draw"))xt.renderMultiDraw(X._multiDrawStarts,X._multiDrawCounts,X._multiDrawCount);else{const We=X._multiDrawStarts,Hn=X._multiDrawCounts,gt=X._multiDrawCount,pn=He?ue.get(He).bytesPerElement:1,mi=ke.get(te).currentProgram.getUniforms();for(let Zt=0;Zt<gt;Zt++)mi.setValue(W,"_gl_DrawID",Zt),xt.render(We[Zt]/pn,Hn[Zt])}else if(X.isInstancedMesh)xt.renderInstances(vt,Rt,X.count);else if(Q.isInstancedBufferGeometry){const We=Q._maxInstanceCount!==void 0?Q._maxInstanceCount:1/0,Hn=Math.min(Q.instanceCount,We);xt.renderInstances(vt,Rt,Hn)}else xt.render(vt,Rt)};function pt(R,j,Q){R.transparent===!0&&R.side===Fn&&R.forceSinglePass===!1?(R.side=Bn,R.needsUpdate=!0,Ki(R,j,Q),R.side=Xi,R.needsUpdate=!0,Ki(R,j,Q),R.side=Fn):Ki(R,j,Q)}this.compile=function(R,j,Q=null){Q===null&&(Q=R),_=dt.get(Q),_.init(j),P.push(_),Q.traverseVisible(function(X){X.isLight&&X.layers.test(j.layers)&&(_.pushLight(X),X.castShadow&&_.pushShadow(X))}),R!==Q&&R.traverseVisible(function(X){X.isLight&&X.layers.test(j.layers)&&(_.pushLight(X),X.castShadow&&_.pushShadow(X))}),_.setupLights();const te=new Set;return R.traverse(function(X){if(!(X.isMesh||X.isPoints||X.isLine||X.isSprite))return;const Se=X.material;if(Se)if(Array.isArray(Se))for(let Le=0;Le<Se.length;Le++){const ze=Se[Le];pt(ze,Q,X),te.add(ze)}else pt(Se,Q,X),te.add(Se)}),P.pop(),_=null,te},this.compileAsync=function(R,j,Q=null){const te=this.compile(R,j,Q);return new Promise(X=>{function Se(){if(te.forEach(function(Le){ke.get(Le).currentProgram.isReady()&&te.delete(Le)}),te.size===0){X(R);return}setTimeout(Se,10)}ht.get("KHR_parallel_shader_compile")!==null?Se():setTimeout(Se,10)})};let An=null;function kn(R){An&&An(R)}function as(){ri.stop()}function cs(){ri.start()}const ri=new Fg;ri.setAnimationLoop(kn),typeof self<"u"&&ri.setContext(self),this.setAnimationLoop=function(R){An=R,ie.setAnimationLoop(R),R===null?ri.stop():ri.start()},ie.addEventListener("sessionstart",as),ie.addEventListener("sessionend",cs),this.render=function(R,j){if(j!==void 0&&j.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(k===!0)return;if(R.matrixWorldAutoUpdate===!0&&R.updateMatrixWorld(),j.parent===null&&j.matrixWorldAutoUpdate===!0&&j.updateMatrixWorld(),ie.enabled===!0&&ie.isPresenting===!0&&(ie.cameraAutoUpdate===!0&&ie.updateCamera(j),j=ie.getCamera()),R.isScene===!0&&R.onBeforeRender(S,R,j,z),_=dt.get(R,P.length),_.init(j),P.push(_),Xe.multiplyMatrices(j.projectionMatrix,j.matrixWorldInverse),he.setFromProjectionMatrix(Xe),Ne=this.localClippingEnabled,me=N.init(this.clippingPlanes,Ne),v=De.get(R,A.length),v.init(),A.push(v),ie.enabled===!0&&ie.isPresenting===!0){const Se=S.xr.getDepthSensingMesh();Se!==null&&yr(Se,j,-1/0,S.sortObjects)}yr(R,j,0,S.sortObjects),v.finish(),S.sortObjects===!0&&v.sort(ge,Te),rt=ie.enabled===!1||ie.isPresenting===!1||ie.hasDepthSensing()===!1,rt&&ae.addToRenderList(v,R),this.info.render.frame++,me===!0&&N.beginShadows();const Q=_.state.shadowsArray;Y.render(Q,R,j),me===!0&&N.endShadows(),this.info.autoReset===!0&&this.info.reset();const te=v.opaque,X=v.transmissive;if(_.setupLights(),j.isArrayCamera){const Se=j.cameras;if(X.length>0)for(let Le=0,ze=Se.length;Le<ze;Le++){const He=Se[Le];us(te,X,R,He)}rt&&ae.render(R);for(let Le=0,ze=Se.length;Le<ze;Le++){const He=Se[Le];ls(v,R,He,He.viewport)}}else X.length>0&&us(te,X,R,j),rt&&ae.render(R),ls(v,R,j);z!==null&&(D.updateMultisampleRenderTarget(z),D.updateRenderTargetMipmap(z)),R.isScene===!0&&R.onAfterRender(S,R,j),lt.resetDefaultState(),I=-1,w=null,P.pop(),P.length>0?(_=P[P.length-1],me===!0&&N.setGlobalState(S.clippingPlanes,_.state.camera)):_=null,A.pop(),A.length>0?v=A[A.length-1]:v=null};function yr(R,j,Q,te){if(R.visible===!1)return;if(R.layers.test(j.layers)){if(R.isGroup)Q=R.renderOrder;else if(R.isLOD)R.autoUpdate===!0&&R.update(j);else if(R.isLight)_.pushLight(R),R.castShadow&&_.pushShadow(R);else if(R.isSprite){if(!R.frustumCulled||he.intersectsSprite(R)){te&&tt.setFromMatrixPosition(R.matrixWorld).applyMatrix4(Xe);const Le=fe.update(R),ze=R.material;ze.visible&&v.push(R,Le,ze,Q,tt.z,null)}}else if((R.isMesh||R.isLine||R.isPoints)&&(!R.frustumCulled||he.intersectsObject(R))){const Le=fe.update(R),ze=R.material;if(te&&(R.boundingSphere!==void 0?(R.boundingSphere===null&&R.computeBoundingSphere(),tt.copy(R.boundingSphere.center)):(Le.boundingSphere===null&&Le.computeBoundingSphere(),tt.copy(Le.boundingSphere.center)),tt.applyMatrix4(R.matrixWorld).applyMatrix4(Xe)),Array.isArray(ze)){const He=Le.groups;for(let et=0,$e=He.length;et<$e;et++){const Ve=He[et],vt=ze[Ve.materialIndex];vt&&vt.visible&&v.push(R,Le,vt,Q,tt.z,Ve)}}else ze.visible&&v.push(R,Le,ze,Q,tt.z,null)}}const Se=R.children;for(let Le=0,ze=Se.length;Le<ze;Le++)yr(Se[Le],j,Q,te)}function ls(R,j,Q,te){const X=R.opaque,Se=R.transmissive,Le=R.transparent;_.setupLightsView(Q),me===!0&&N.setGlobalState(S.clippingPlanes,Q),te&&Fe.viewport(H.copy(te)),X.length>0&&zn(X,j,Q),Se.length>0&&zn(Se,j,Q),Le.length>0&&zn(Le,j,Q),Fe.buffers.depth.setTest(!0),Fe.buffers.depth.setMask(!0),Fe.buffers.color.setMask(!0),Fe.setPolygonOffset(!1)}function us(R,j,Q,te){if((Q.isScene===!0?Q.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[te.id]===void 0&&(_.state.transmissionRenderTarget[te.id]=new ns(1,1,{generateMipmaps:!0,type:ht.has("EXT_color_buffer_half_float")||ht.has("EXT_color_buffer_float")?na:qi,minFilter:Vi,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:bt.workingColorSpace}));const Se=_.state.transmissionRenderTarget[te.id],Le=te.viewport||H;Se.setSize(Le.z,Le.w);const ze=S.getRenderTarget();S.setRenderTarget(Se),S.getClearColor(oe),ce=S.getClearAlpha(),ce<1&&S.setClearColor(16777215,.5),S.clear(),rt&&ae.render(Q);const He=S.toneMapping;S.toneMapping=gr;const et=te.viewport;if(te.viewport!==void 0&&(te.viewport=void 0),_.setupLightsView(te),me===!0&&N.setGlobalState(S.clippingPlanes,te),zn(R,Q,te),D.updateMultisampleRenderTarget(Se),D.updateRenderTargetMipmap(Se),ht.has("WEBGL_multisampled_render_to_texture")===!1){let $e=!1;for(let Ve=0,vt=j.length;Ve<vt;Ve++){const wt=j[Ve],Rt=wt.object,qt=wt.geometry,xt=wt.material,We=wt.group;if(xt.side===Fn&&Rt.layers.test(te.layers)){const Hn=xt.side;xt.side=Bn,xt.needsUpdate=!0,xr(Rt,Q,te,qt,xt,We),xt.side=Hn,xt.needsUpdate=!0,$e=!0}}$e===!0&&(D.updateMultisampleRenderTarget(Se),D.updateRenderTargetMipmap(Se))}S.setRenderTarget(ze),S.setClearColor(oe,ce),et!==void 0&&(te.viewport=et),S.toneMapping=He}function zn(R,j,Q){const te=j.isScene===!0?j.overrideMaterial:null;for(let X=0,Se=R.length;X<Se;X++){const Le=R[X],ze=Le.object,He=Le.geometry,et=te===null?Le.material:te,$e=Le.group;ze.layers.test(Q.layers)&&xr(ze,j,Q,He,et,$e)}}function xr(R,j,Q,te,X,Se){R.onBeforeRender(S,j,Q,te,X,Se),R.modelViewMatrix.multiplyMatrices(Q.matrixWorldInverse,R.matrixWorld),R.normalMatrix.getNormalMatrix(R.modelViewMatrix),X.onBeforeRender(S,j,Q,te,R,Se),X.transparent===!0&&X.side===Fn&&X.forceSinglePass===!1?(X.side=Bn,X.needsUpdate=!0,S.renderBufferDirect(Q,j,te,X,R,Se),X.side=Xi,X.needsUpdate=!0,S.renderBufferDirect(Q,j,te,X,R,Se),X.side=Fn):S.renderBufferDirect(Q,j,te,X,R,Se),R.onAfterRender(S,j,Q,te,X,Se)}function Ki(R,j,Q){j.isScene!==!0&&(j=St);const te=ke.get(R),X=_.state.lights,Se=_.state.shadowsArray,Le=X.state.version,ze=Ue.getParameters(R,X.state,Se,j,Q),He=Ue.getProgramCacheKey(ze);let et=te.programs;te.environment=R.isMeshStandardMaterial?j.environment:null,te.fog=j.fog,te.envMap=(R.isMeshStandardMaterial?Z:E).get(R.envMap||te.environment),te.envMapRotation=te.environment!==null&&R.envMap===null?j.environmentRotation:R.envMapRotation,et===void 0&&(R.addEventListener("dispose",Ge),et=new Map,te.programs=et);let $e=et.get(He);if($e!==void 0){if(te.currentProgram===$e&&te.lightsStateVersion===Le)return $n(R,ze),$e}else ze.uniforms=Ue.getUniforms(R),R.onBeforeCompile(ze,S),$e=Ue.acquireProgram(ze,He),et.set(He,$e),te.uniforms=ze.uniforms;const Ve=te.uniforms;return(!R.isShaderMaterial&&!R.isRawShaderMaterial||R.clipping===!0)&&(Ve.clippingPlanes=N.uniform),$n(R,ze),te.needsLights=Zi(R),te.lightsStateVersion=Le,te.needsLights&&(Ve.ambientLightColor.value=X.state.ambient,Ve.lightProbe.value=X.state.probe,Ve.directionalLights.value=X.state.directional,Ve.directionalLightShadows.value=X.state.directionalShadow,Ve.spotLights.value=X.state.spot,Ve.spotLightShadows.value=X.state.spotShadow,Ve.rectAreaLights.value=X.state.rectArea,Ve.ltc_1.value=X.state.rectAreaLTC1,Ve.ltc_2.value=X.state.rectAreaLTC2,Ve.pointLights.value=X.state.point,Ve.pointLightShadows.value=X.state.pointShadow,Ve.hemisphereLights.value=X.state.hemi,Ve.directionalShadowMap.value=X.state.directionalShadowMap,Ve.directionalShadowMatrix.value=X.state.directionalShadowMatrix,Ve.spotShadowMap.value=X.state.spotShadowMap,Ve.spotLightMatrix.value=X.state.spotLightMatrix,Ve.spotLightMap.value=X.state.spotLightMap,Ve.pointShadowMap.value=X.state.pointShadowMap,Ve.pointShadowMatrix.value=X.state.pointShadowMatrix),te.currentProgram=$e,te.uniformsList=null,$e}function hs(R){if(R.uniformsList===null){const j=R.currentProgram.getUniforms();R.uniformsList=Pc.seqWithValue(j.seq,R.uniforms)}return R.uniformsList}function $n(R,j){const Q=ke.get(R);Q.outputColorSpace=j.outputColorSpace,Q.batching=j.batching,Q.batchingColor=j.batchingColor,Q.instancing=j.instancing,Q.instancingColor=j.instancingColor,Q.instancingMorph=j.instancingMorph,Q.skinning=j.skinning,Q.morphTargets=j.morphTargets,Q.morphNormals=j.morphNormals,Q.morphColors=j.morphColors,Q.morphTargetsCount=j.morphTargetsCount,Q.numClippingPlanes=j.numClippingPlanes,Q.numIntersection=j.numClipIntersection,Q.vertexAlphas=j.vertexAlphas,Q.vertexTangents=j.vertexTangents,Q.toneMapping=j.toneMapping}function ho(R,j,Q,te,X){j.isScene!==!0&&(j=St),D.resetTextureUnits();const Se=j.fog,Le=te.isMeshStandardMaterial?j.environment:null,ze=z===null?S.outputColorSpace:z.isXRRenderTarget===!0?z.texture.colorSpace:Ln,He=(te.isMeshStandardMaterial?Z:E).get(te.envMap||Le),et=te.vertexColors===!0&&!!Q.attributes.color&&Q.attributes.color.itemSize===4,$e=!!Q.attributes.tangent&&(!!te.normalMap||te.anisotropy>0),Ve=!!Q.morphAttributes.position,vt=!!Q.morphAttributes.normal,wt=!!Q.morphAttributes.color;let Rt=gr;te.toneMapped&&(z===null||z.isXRRenderTarget===!0)&&(Rt=S.toneMapping);const qt=Q.morphAttributes.position||Q.morphAttributes.normal||Q.morphAttributes.color,xt=qt!==void 0?qt.length:0,We=ke.get(te),Hn=_.state.lights;if(me===!0&&(Ne===!0||R!==w)){const yn=R===w&&te.id===I;N.setState(te,R,yn)}let gt=!1;te.version===We.__version?(We.needsLights&&We.lightsStateVersion!==Hn.state.version||We.outputColorSpace!==ze||X.isBatchedMesh&&We.batching===!1||!X.isBatchedMesh&&We.batching===!0||X.isBatchedMesh&&We.batchingColor===!0&&X.colorTexture===null||X.isBatchedMesh&&We.batchingColor===!1&&X.colorTexture!==null||X.isInstancedMesh&&We.instancing===!1||!X.isInstancedMesh&&We.instancing===!0||X.isSkinnedMesh&&We.skinning===!1||!X.isSkinnedMesh&&We.skinning===!0||X.isInstancedMesh&&We.instancingColor===!0&&X.instanceColor===null||X.isInstancedMesh&&We.instancingColor===!1&&X.instanceColor!==null||X.isInstancedMesh&&We.instancingMorph===!0&&X.morphTexture===null||X.isInstancedMesh&&We.instancingMorph===!1&&X.morphTexture!==null||We.envMap!==He||te.fog===!0&&We.fog!==Se||We.numClippingPlanes!==void 0&&(We.numClippingPlanes!==N.numPlanes||We.numIntersection!==N.numIntersection)||We.vertexAlphas!==et||We.vertexTangents!==$e||We.morphTargets!==Ve||We.morphNormals!==vt||We.morphColors!==wt||We.toneMapping!==Rt||We.morphTargetsCount!==xt)&&(gt=!0):(gt=!0,We.__version=te.version);let pn=We.currentProgram;gt===!0&&(pn=Ki(te,j,X));let mi=!1,Zt=!1,Ei=!1;const Ct=pn.getUniforms(),Dn=We.uniforms;if(Fe.useProgram(pn.program)&&(mi=!0,Zt=!0,Ei=!0),te.id!==I&&(I=te.id,Zt=!0),mi||w!==R){Fe.buffers.depth.getReversed()?(Me.copy(R.projectionMatrix),fE(Me),pE(Me),Ct.setValue(W,"projectionMatrix",Me)):Ct.setValue(W,"projectionMatrix",R.projectionMatrix),Ct.setValue(W,"viewMatrix",R.matrixWorldInverse);const mn=Ct.map.cameraPosition;mn!==void 0&&mn.setValue(W,Ze.setFromMatrixPosition(R.matrixWorld)),ct.logarithmicDepthBuffer&&Ct.setValue(W,"logDepthBufFC",2/(Math.log(R.far+1)/Math.LN2)),(te.isMeshPhongMaterial||te.isMeshToonMaterial||te.isMeshLambertMaterial||te.isMeshBasicMaterial||te.isMeshStandardMaterial||te.isShaderMaterial)&&Ct.setValue(W,"isOrthographic",R.isOrthographicCamera===!0),w!==R&&(w=R,Zt=!0,Ei=!0)}if(X.isSkinnedMesh){Ct.setOptional(W,X,"bindMatrix"),Ct.setOptional(W,X,"bindMatrixInverse");const yn=X.skeleton;yn&&(yn.boneTexture===null&&yn.computeBoneTexture(),Ct.setValue(W,"boneTexture",yn.boneTexture,D))}X.isBatchedMesh&&(Ct.setOptional(W,X,"batchingTexture"),Ct.setValue(W,"batchingTexture",X._matricesTexture,D),Ct.setOptional(W,X,"batchingIdTexture"),Ct.setValue(W,"batchingIdTexture",X._indirectTexture,D),Ct.setOptional(W,X,"batchingColorTexture"),X._colorsTexture!==null&&Ct.setValue(W,"batchingColorTexture",X._colorsTexture,D));const Ai=Q.morphAttributes;if((Ai.position!==void 0||Ai.normal!==void 0||Ai.color!==void 0)&&_e.update(X,Q,pn),(Zt||We.receiveShadow!==X.receiveShadow)&&(We.receiveShadow=X.receiveShadow,Ct.setValue(W,"receiveShadow",X.receiveShadow)),te.isMeshGouraudMaterial&&te.envMap!==null&&(Dn.envMap.value=He,Dn.flipEnvMap.value=He.isCubeTexture&&He.isRenderTargetTexture===!1?-1:1),te.isMeshStandardMaterial&&te.envMap===null&&j.environment!==null&&(Dn.envMapIntensity.value=j.environmentIntensity),Zt&&(Ct.setValue(W,"toneMappingExposure",S.toneMappingExposure),We.needsLights&&Ti(Dn,Ei),Se&&te.fog===!0&&Pe.refreshFogUniforms(Dn,Se),Pe.refreshMaterialUniforms(Dn,te,ne,le,_.state.transmissionRenderTarget[R.id]),Pc.upload(W,hs(We),Dn,D)),te.isShaderMaterial&&te.uniformsNeedUpdate===!0&&(Pc.upload(W,hs(We),Dn,D),te.uniformsNeedUpdate=!1),te.isSpriteMaterial&&Ct.setValue(W,"center",X.center),Ct.setValue(W,"modelViewMatrix",X.modelViewMatrix),Ct.setValue(W,"normalMatrix",X.normalMatrix),Ct.setValue(W,"modelMatrix",X.matrixWorld),te.isShaderMaterial||te.isRawShaderMaterial){const yn=te.uniformsGroups;for(let mn=0,Vn=yn.length;mn<Vn;mn++){const ds=yn[mn];G.update(ds,pn),G.bind(ds,pn)}}return pn}function Ti(R,j){R.ambientLightColor.needsUpdate=j,R.lightProbe.needsUpdate=j,R.directionalLights.needsUpdate=j,R.directionalLightShadows.needsUpdate=j,R.pointLights.needsUpdate=j,R.pointLightShadows.needsUpdate=j,R.spotLights.needsUpdate=j,R.spotLightShadows.needsUpdate=j,R.rectAreaLights.needsUpdate=j,R.hemisphereLights.needsUpdate=j}function Zi(R){return R.isMeshLambertMaterial||R.isMeshToonMaterial||R.isMeshPhongMaterial||R.isMeshStandardMaterial||R.isShadowMaterial||R.isShaderMaterial&&R.lights===!0}this.getActiveCubeFace=function(){return O},this.getActiveMipmapLevel=function(){return U},this.getRenderTarget=function(){return z},this.setRenderTargetTextures=function(R,j,Q){ke.get(R.texture).__webglTexture=j,ke.get(R.depthTexture).__webglTexture=Q;const te=ke.get(R);te.__hasExternalTextures=!0,te.__autoAllocateDepthBuffer=Q===void 0,te.__autoAllocateDepthBuffer||ht.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),te.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(R,j){const Q=ke.get(R);Q.__webglFramebuffer=j,Q.__useDefaultFramebuffer=j===void 0},this.setRenderTarget=function(R,j=0,Q=0){z=R,O=j,U=Q;let te=!0,X=null,Se=!1,Le=!1;if(R){const He=ke.get(R);if(He.__useDefaultFramebuffer!==void 0)Fe.bindFramebuffer(W.FRAMEBUFFER,null),te=!1;else if(He.__webglFramebuffer===void 0)D.setupRenderTarget(R);else if(He.__hasExternalTextures)D.rebindTextures(R,ke.get(R.texture).__webglTexture,ke.get(R.depthTexture).__webglTexture);else if(R.depthBuffer){const Ve=R.depthTexture;if(He.__boundDepthTexture!==Ve){if(Ve!==null&&ke.has(Ve)&&(R.width!==Ve.image.width||R.height!==Ve.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");D.setupDepthRenderbuffer(R)}}const et=R.texture;(et.isData3DTexture||et.isDataArrayTexture||et.isCompressedArrayTexture)&&(Le=!0);const $e=ke.get(R).__webglFramebuffer;R.isWebGLCubeRenderTarget?(Array.isArray($e[j])?X=$e[j][Q]:X=$e[j],Se=!0):R.samples>0&&D.useMultisampledRTT(R)===!1?X=ke.get(R).__webglMultisampledFramebuffer:Array.isArray($e)?X=$e[Q]:X=$e,H.copy(R.viewport),ee.copy(R.scissor),J=R.scissorTest}else H.copy(Oe).multiplyScalar(ne).floor(),ee.copy(Ye).multiplyScalar(ne).floor(),J=yt;if(Fe.bindFramebuffer(W.FRAMEBUFFER,X)&&te&&Fe.drawBuffers(R,X),Fe.viewport(H),Fe.scissor(ee),Fe.setScissorTest(J),Se){const He=ke.get(R.texture);W.framebufferTexture2D(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_CUBE_MAP_POSITIVE_X+j,He.__webglTexture,Q)}else if(Le){const He=ke.get(R.texture),et=j||0;W.framebufferTextureLayer(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0,He.__webglTexture,Q||0,et)}I=-1},this.readRenderTargetPixels=function(R,j,Q,te,X,Se,Le){if(!(R&&R.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let ze=ke.get(R).__webglFramebuffer;if(R.isWebGLCubeRenderTarget&&Le!==void 0&&(ze=ze[Le]),ze){Fe.bindFramebuffer(W.FRAMEBUFFER,ze);try{const He=R.texture,et=He.format,$e=He.type;if(!ct.textureFormatReadable(et)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ct.textureTypeReadable($e)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}j>=0&&j<=R.width-te&&Q>=0&&Q<=R.height-X&&W.readPixels(j,Q,te,X,qe.convert(et),qe.convert($e),Se)}finally{const He=z!==null?ke.get(z).__webglFramebuffer:null;Fe.bindFramebuffer(W.FRAMEBUFFER,He)}}},this.readRenderTargetPixelsAsync=async function(R,j,Q,te,X,Se,Le){if(!(R&&R.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let ze=ke.get(R).__webglFramebuffer;if(R.isWebGLCubeRenderTarget&&Le!==void 0&&(ze=ze[Le]),ze){const He=R.texture,et=He.format,$e=He.type;if(!ct.textureFormatReadable(et))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ct.textureTypeReadable($e))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(j>=0&&j<=R.width-te&&Q>=0&&Q<=R.height-X){Fe.bindFramebuffer(W.FRAMEBUFFER,ze);const Ve=W.createBuffer();W.bindBuffer(W.PIXEL_PACK_BUFFER,Ve),W.bufferData(W.PIXEL_PACK_BUFFER,Se.byteLength,W.STREAM_READ),W.readPixels(j,Q,te,X,qe.convert(et),qe.convert($e),0);const vt=z!==null?ke.get(z).__webglFramebuffer:null;Fe.bindFramebuffer(W.FRAMEBUFFER,vt);const wt=W.fenceSync(W.SYNC_GPU_COMMANDS_COMPLETE,0);return W.flush(),await dE(W,wt,4),W.bindBuffer(W.PIXEL_PACK_BUFFER,Ve),W.getBufferSubData(W.PIXEL_PACK_BUFFER,0,Se),W.deleteBuffer(Ve),W.deleteSync(wt),Se}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(R,j=null,Q=0){R.isTexture!==!0&&(Wo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),j=arguments[0]||null,R=arguments[1]);const te=Math.pow(2,-Q),X=Math.floor(R.image.width*te),Se=Math.floor(R.image.height*te),Le=j!==null?j.x:0,ze=j!==null?j.y:0;D.setTexture2D(R,0),W.copyTexSubImage2D(W.TEXTURE_2D,Q,0,0,Le,ze,X,Se),Fe.unbindTexture()},this.copyTextureToTexture=function(R,j,Q=null,te=null,X=0){R.isTexture!==!0&&(Wo("WebGLRenderer: copyTextureToTexture function signature has changed."),te=arguments[0]||null,R=arguments[1],j=arguments[2],X=arguments[3]||0,Q=null);let Se,Le,ze,He,et,$e,Ve,vt,wt;const Rt=R.isCompressedTexture?R.mipmaps[X]:R.image;Q!==null?(Se=Q.max.x-Q.min.x,Le=Q.max.y-Q.min.y,ze=Q.isBox3?Q.max.z-Q.min.z:1,He=Q.min.x,et=Q.min.y,$e=Q.isBox3?Q.min.z:0):(Se=Rt.width,Le=Rt.height,ze=Rt.depth||1,He=0,et=0,$e=0),te!==null?(Ve=te.x,vt=te.y,wt=te.z):(Ve=0,vt=0,wt=0);const qt=qe.convert(j.format),xt=qe.convert(j.type);let We;j.isData3DTexture?(D.setTexture3D(j,0),We=W.TEXTURE_3D):j.isDataArrayTexture||j.isCompressedArrayTexture?(D.setTexture2DArray(j,0),We=W.TEXTURE_2D_ARRAY):(D.setTexture2D(j,0),We=W.TEXTURE_2D),W.pixelStorei(W.UNPACK_FLIP_Y_WEBGL,j.flipY),W.pixelStorei(W.UNPACK_PREMULTIPLY_ALPHA_WEBGL,j.premultiplyAlpha),W.pixelStorei(W.UNPACK_ALIGNMENT,j.unpackAlignment);const Hn=W.getParameter(W.UNPACK_ROW_LENGTH),gt=W.getParameter(W.UNPACK_IMAGE_HEIGHT),pn=W.getParameter(W.UNPACK_SKIP_PIXELS),mi=W.getParameter(W.UNPACK_SKIP_ROWS),Zt=W.getParameter(W.UNPACK_SKIP_IMAGES);W.pixelStorei(W.UNPACK_ROW_LENGTH,Rt.width),W.pixelStorei(W.UNPACK_IMAGE_HEIGHT,Rt.height),W.pixelStorei(W.UNPACK_SKIP_PIXELS,He),W.pixelStorei(W.UNPACK_SKIP_ROWS,et),W.pixelStorei(W.UNPACK_SKIP_IMAGES,$e);const Ei=R.isDataArrayTexture||R.isData3DTexture,Ct=j.isDataArrayTexture||j.isData3DTexture;if(R.isRenderTargetTexture||R.isDepthTexture){const Dn=ke.get(R),Ai=ke.get(j),yn=ke.get(Dn.__renderTarget),mn=ke.get(Ai.__renderTarget);Fe.bindFramebuffer(W.READ_FRAMEBUFFER,yn.__webglFramebuffer),Fe.bindFramebuffer(W.DRAW_FRAMEBUFFER,mn.__webglFramebuffer);for(let Vn=0;Vn<ze;Vn++)Ei&&W.framebufferTextureLayer(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,ke.get(R).__webglTexture,X,$e+Vn),R.isDepthTexture?(Ct&&W.framebufferTextureLayer(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,ke.get(j).__webglTexture,X,wt+Vn),W.blitFramebuffer(He,et,Se,Le,Ve,vt,Se,Le,W.DEPTH_BUFFER_BIT,W.NEAREST)):Ct?W.copyTexSubImage3D(We,X,Ve,vt,wt+Vn,He,et,Se,Le):W.copyTexSubImage2D(We,X,Ve,vt,wt+Vn,He,et,Se,Le);Fe.bindFramebuffer(W.READ_FRAMEBUFFER,null),Fe.bindFramebuffer(W.DRAW_FRAMEBUFFER,null)}else Ct?R.isDataTexture||R.isData3DTexture?W.texSubImage3D(We,X,Ve,vt,wt,Se,Le,ze,qt,xt,Rt.data):j.isCompressedArrayTexture?W.compressedTexSubImage3D(We,X,Ve,vt,wt,Se,Le,ze,qt,Rt.data):W.texSubImage3D(We,X,Ve,vt,wt,Se,Le,ze,qt,xt,Rt):R.isDataTexture?W.texSubImage2D(W.TEXTURE_2D,X,Ve,vt,Se,Le,qt,xt,Rt.data):R.isCompressedTexture?W.compressedTexSubImage2D(W.TEXTURE_2D,X,Ve,vt,Rt.width,Rt.height,qt,Rt.data):W.texSubImage2D(W.TEXTURE_2D,X,Ve,vt,Se,Le,qt,xt,Rt);W.pixelStorei(W.UNPACK_ROW_LENGTH,Hn),W.pixelStorei(W.UNPACK_IMAGE_HEIGHT,gt),W.pixelStorei(W.UNPACK_SKIP_PIXELS,pn),W.pixelStorei(W.UNPACK_SKIP_ROWS,mi),W.pixelStorei(W.UNPACK_SKIP_IMAGES,Zt),X===0&&j.generateMipmaps&&W.generateMipmap(We),Fe.unbindTexture()},this.copyTextureToTexture3D=function(R,j,Q=null,te=null,X=0){return R.isTexture!==!0&&(Wo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),Q=arguments[0]||null,te=arguments[1]||null,R=arguments[2],j=arguments[3],X=arguments[4]||0),Wo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(R,j,Q,te,X)},this.initRenderTarget=function(R){ke.get(R).__webglFramebuffer===void 0&&D.setupRenderTarget(R)},this.initTexture=function(R){R.isCubeTexture?D.setTextureCube(R,0):R.isData3DTexture?D.setTexture3D(R,0):R.isDataArrayTexture||R.isCompressedArrayTexture?D.setTexture2DArray(R,0):D.setTexture2D(R,0),Fe.unbindTexture()},this.resetState=function(){O=0,U=0,z=null,Fe.reset(),lt.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Gi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=bt._getDrawingBufferColorSpace(e),t.unpackColorSpace=bt._getUnpackColorSpace()}}class xd{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new Ke(e),this.density=t}clone(){return new xd(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class TR extends Ht{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new pi,this.environmentIntensity=1,this.environmentRotation=new pi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class ER{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Jh,this.updateRanges=[],this.version=0,this.uuid=fi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=fi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=fi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Pn=new F;class bd{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Pn.fromBufferAttribute(this,t),Pn.applyMatrix4(e),this.setXYZ(t,Pn.x,Pn.y,Pn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Pn.fromBufferAttribute(this,t),Pn.applyNormalMatrix(e),this.setXYZ(t,Pn.x,Pn.y,Pn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Pn.fromBufferAttribute(this,t),Pn.transformDirection(e),this.setXYZ(t,Pn.x,Pn.y,Pn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=ui(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Lt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Lt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Lt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Lt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Lt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=ui(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=ui(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=ui(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=ui(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Lt(t,this.array),n=Lt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=Lt(t,this.array),n=Lt(n,this.array),i=Lt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Lt(t,this.array),n=Lt(n,this.array),i=Lt(i,this.array),s=Lt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new Qt(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new bd(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Mm=new F,Tm=new Et,Em=new Et,AR=new F,Am=new nt,lc=new F,Ku=new bi,wm=new nt,Zu=new oo;class wR extends we{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Pp,this.bindMatrix=new nt,this.bindMatrixInverse=new nt,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new Yi),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,lc),this.boundingBox.expandByPoint(lc)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new bi),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,lc),this.boundingSphere.expandByPoint(lc)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,i=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Ku.copy(this.boundingSphere),Ku.applyMatrix4(i),e.ray.intersectsSphere(Ku)!==!1&&(wm.copy(i).invert(),Zu.copy(e.ray).applyMatrix4(wm),!(this.boundingBox!==null&&Zu.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Zu)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new Et,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);const s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Pp?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===NT?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,i=this.geometry;Tm.fromBufferAttribute(i.attributes.skinIndex,e),Em.fromBufferAttribute(i.attributes.skinWeight,e),Mm.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){const a=Em.getComponent(s);if(a!==0){const c=Tm.getComponent(s);Am.multiplyMatrices(n.bones[c].matrixWorld,n.boneInverses[c]),t.addScaledVector(AR.copy(Mm).applyMatrix4(Am),a)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Sd extends Ht{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Gg extends fn{constructor(e=null,t=1,n=1,i,s,a,c,u,h=In,f=In,p,m){super(null,a,c,u,h,f,i,s,p,m),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Pm=new nt,PR=new nt;class zc{constructor(e=[],t=[]){this.uuid=fi(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new nt)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new nt;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,a=e.length;s<a;s++){const c=e[s]?e[s].matrixWorld:PR;Pm.multiplyMatrices(c,t[s]),Pm.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new zc(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Gg(t,e,e,ni,di);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){const s=e.bones[n];let a=t[s];a===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),a=new Sd),this.bones.push(a),this.boneInverses.push(new nt().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){const a=t[i];e.bones.push(a.uuid);const c=n[i];e.boneInverses.push(c.toArray())}return e}}class ed extends Qt{constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const ks=new nt,Rm=new nt,uc=[],Cm=new Yi,RR=new nt,Uo=new we,Fo=new bi;class CR extends we{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new ed(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let i=0;i<n;i++)this.setMatrixAt(i,RR)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new Yi),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,ks),Cm.copy(e.boundingBox).applyMatrix4(ks),this.boundingBox.union(Cm)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new bi),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,ks),Fo.copy(e.boundingSphere).applyMatrix4(ks),this.boundingSphere.union(Fo)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,i=this.morphTexture.source.data.data,s=n.length+1,a=e*s+1;for(let c=0;c<n.length;c++)n[c]=i[a+c]}raycast(e,t){const n=this.matrixWorld,i=this.count;if(Uo.geometry=this.geometry,Uo.material=this.material,Uo.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Fo.copy(this.boundingSphere),Fo.applyMatrix4(n),e.ray.intersectsSphere(Fo)!==!1))for(let s=0;s<i;s++){this.getMatrixAt(s,ks),Rm.multiplyMatrices(n,ks),Uo.matrixWorld=Rm,Uo.raycast(e,uc);for(let a=0,c=uc.length;a<c;a++){const u=uc[a];u.instanceId=s,u.object=this,t.push(u)}uc.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new ed(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,i=n.length+1;this.morphTexture===null&&(this.morphTexture=new Gg(new Float32Array(i*this.count),i,this.count,ud,di));const s=this.morphTexture.source.data.data;let a=0;for(let h=0;h<n.length;h++)a+=n[h];const c=this.geometry.morphTargetsRelative?1:1-a,u=i*e;s[u]=c,s.set(n,u+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Hc extends xi{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new Ke(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Nc=new F,Oc=new F,Im=new nt,Bo=new oo,hc=new bi,$u=new F,Lm=new F;class li extends Ht{constructor(e=new sn,t=new Hc){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)Nc.fromBufferAttribute(t,i-1),Oc.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=Nc.distanceTo(Oc);e.setAttribute("lineDistance",new jt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),hc.copy(n.boundingSphere),hc.applyMatrix4(i),hc.radius+=s,e.ray.intersectsSphere(hc)===!1)return;Im.copy(i).invert(),Bo.copy(e.ray).applyMatrix4(Im);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=this.isLineSegments?2:1,f=n.index,m=n.attributes.position;if(f!==null){const g=Math.max(0,a.start),x=Math.min(f.count,a.start+a.count);for(let M=g,v=x-1;M<v;M+=h){const _=f.getX(M),A=f.getX(M+1),P=dc(this,e,Bo,u,_,A);P&&t.push(P)}if(this.isLineLoop){const M=f.getX(x-1),v=f.getX(g),_=dc(this,e,Bo,u,M,v);_&&t.push(_)}}else{const g=Math.max(0,a.start),x=Math.min(m.count,a.start+a.count);for(let M=g,v=x-1;M<v;M+=h){const _=dc(this,e,Bo,u,M,M+1);_&&t.push(_)}if(this.isLineLoop){const M=dc(this,e,Bo,u,x-1,g);M&&t.push(M)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function dc(r,e,t,n,i,s){const a=r.geometry.attributes.position;if(Nc.fromBufferAttribute(a,i),Oc.fromBufferAttribute(a,s),t.distanceSqToSegment(Nc,Oc,$u,Lm)>n)return;$u.applyMatrix4(r.matrixWorld);const u=e.ray.origin.distanceTo($u);if(!(u<e.near||u>e.far))return{distance:u,point:Lm.clone().applyMatrix4(r.matrixWorld),index:i,face:null,faceIndex:null,barycoord:null,object:r}}const Dm=new F,Nm=new F;class Wg extends li{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)Dm.fromBufferAttribute(t,i),Nm.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Dm.distanceTo(Nm);e.setAttribute("lineDistance",new jt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class IR extends li{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class jg extends xi{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new Ke(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Om=new nt,td=new oo,fc=new bi,pc=new F;class LR extends Ht{constructor(e=new sn,t=new jg){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),fc.copy(n.boundingSphere),fc.applyMatrix4(i),fc.radius+=s,e.ray.intersectsSphere(fc)===!1)return;Om.copy(i).invert(),td.copy(e.ray).applyMatrix4(Om);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=n.index,p=n.attributes.position;if(h!==null){const m=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=m,M=g;x<M;x++){const v=h.getX(x);pc.fromBufferAttribute(p,v),Um(pc,v,u,i,e,t,this)}}else{const m=Math.max(0,a.start),g=Math.min(p.count,a.start+a.count);for(let x=m,M=g;x<M;x++)pc.fromBufferAttribute(p,x),Um(pc,x,u,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function Um(r,e,t,n,i,s,a){const c=td.distanceSqToPoint(r);if(c<t){const u=new F;td.closestPointToPoint(r,u),u.applyMatrix4(n);const h=i.ray.origin.distanceTo(u);if(h<i.near||h>i.far)return;s.push({distance:h,distanceToRay:Math.sqrt(c),point:u,index:e,face:null,faceIndex:null,barycoord:null,object:a})}}class _n extends sn{constructor(e=1,t=1,n=1,i=32,s=1,a=!1,c=0,u=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:i,heightSegments:s,openEnded:a,thetaStart:c,thetaLength:u};const h=this;i=Math.floor(i),s=Math.floor(s);const f=[],p=[],m=[],g=[];let x=0;const M=[],v=n/2;let _=0;A(),a===!1&&(e>0&&P(!0),t>0&&P(!1)),this.setIndex(f),this.setAttribute("position",new jt(p,3)),this.setAttribute("normal",new jt(m,3)),this.setAttribute("uv",new jt(g,2));function A(){const S=new F,k=new F;let O=0;const U=(t-e)/n;for(let z=0;z<=s;z++){const I=[],w=z/s,H=w*(t-e)+e;for(let ee=0;ee<=i;ee++){const J=ee/i,oe=J*u+c,ce=Math.sin(oe),$=Math.cos(oe);k.x=H*ce,k.y=-w*n+v,k.z=H*$,p.push(k.x,k.y,k.z),S.set(ce,U,$).normalize(),m.push(S.x,S.y,S.z),g.push(J,1-w),I.push(x++)}M.push(I)}for(let z=0;z<i;z++)for(let I=0;I<s;I++){const w=M[I][z],H=M[I+1][z],ee=M[I+1][z+1],J=M[I][z+1];(e>0||I!==0)&&(f.push(w,H,J),O+=3),(t>0||I!==s-1)&&(f.push(H,ee,J),O+=3)}h.addGroup(_,O,0),_+=O}function P(S){const k=x,O=new Qe,U=new F;let z=0;const I=S===!0?e:t,w=S===!0?1:-1;for(let ee=1;ee<=i;ee++)p.push(0,v*w,0),m.push(0,w,0),g.push(.5,.5),x++;const H=x;for(let ee=0;ee<=i;ee++){const oe=ee/i*u+c,ce=Math.cos(oe),$=Math.sin(oe);U.x=I*$,U.y=v*w,U.z=I*ce,p.push(U.x,U.y,U.z),m.push(0,w,0),O.x=ce*.5+.5,O.y=$*.5*w+.5,g.push(O.x,O.y),x++}for(let ee=0;ee<i;ee++){const J=k+ee,oe=H+ee;S===!0?f.push(oe,oe+1,J):f.push(oe+1,oe,J),z+=3}h.addGroup(_,z,S===!0?1:2),_+=z}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new _n(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Md extends _n{constructor(e=1,t=1,n=32,i=1,s=!1,a=0,c=Math.PI*2){super(0,e,t,n,i,s,a,c),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:i,openEnded:s,thetaStart:a,thetaLength:c}}static fromJSON(e){return new Md(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Td extends sn{constructor(e=[],t=[],n=1,i=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:i};const s=[],a=[];c(i),h(n),f(),this.setAttribute("position",new jt(s,3)),this.setAttribute("normal",new jt(s.slice(),3)),this.setAttribute("uv",new jt(a,2)),i===0?this.computeVertexNormals():this.normalizeNormals();function c(A){const P=new F,S=new F,k=new F;for(let O=0;O<t.length;O+=3)g(t[O+0],P),g(t[O+1],S),g(t[O+2],k),u(P,S,k,A)}function u(A,P,S,k){const O=k+1,U=[];for(let z=0;z<=O;z++){U[z]=[];const I=A.clone().lerp(S,z/O),w=P.clone().lerp(S,z/O),H=O-z;for(let ee=0;ee<=H;ee++)ee===0&&z===O?U[z][ee]=I:U[z][ee]=I.clone().lerp(w,ee/H)}for(let z=0;z<O;z++)for(let I=0;I<2*(O-z)-1;I++){const w=Math.floor(I/2);I%2===0?(m(U[z][w+1]),m(U[z+1][w]),m(U[z][w])):(m(U[z][w+1]),m(U[z+1][w+1]),m(U[z+1][w]))}}function h(A){const P=new F;for(let S=0;S<s.length;S+=3)P.x=s[S+0],P.y=s[S+1],P.z=s[S+2],P.normalize().multiplyScalar(A),s[S+0]=P.x,s[S+1]=P.y,s[S+2]=P.z}function f(){const A=new F;for(let P=0;P<s.length;P+=3){A.x=s[P+0],A.y=s[P+1],A.z=s[P+2];const S=v(A)/2/Math.PI+.5,k=_(A)/Math.PI+.5;a.push(S,1-k)}x(),p()}function p(){for(let A=0;A<a.length;A+=6){const P=a[A+0],S=a[A+2],k=a[A+4],O=Math.max(P,S,k),U=Math.min(P,S,k);O>.9&&U<.1&&(P<.2&&(a[A+0]+=1),S<.2&&(a[A+2]+=1),k<.2&&(a[A+4]+=1))}}function m(A){s.push(A.x,A.y,A.z)}function g(A,P){const S=A*3;P.x=e[S+0],P.y=e[S+1],P.z=e[S+2]}function x(){const A=new F,P=new F,S=new F,k=new F,O=new Qe,U=new Qe,z=new Qe;for(let I=0,w=0;I<s.length;I+=9,w+=6){A.set(s[I+0],s[I+1],s[I+2]),P.set(s[I+3],s[I+4],s[I+5]),S.set(s[I+6],s[I+7],s[I+8]),O.set(a[w+0],a[w+1]),U.set(a[w+2],a[w+3]),z.set(a[w+4],a[w+5]),k.copy(A).add(P).add(S).divideScalar(3);const H=v(k);M(O,w+0,A,H),M(U,w+2,P,H),M(z,w+4,S,H)}}function M(A,P,S,k){k<0&&A.x===1&&(a[P]=A.x-1),S.x===0&&S.z===0&&(a[P]=k/2/Math.PI+.5)}function v(A){return Math.atan2(A.z,-A.x)}function _(A){return Math.atan2(-A.y,Math.sqrt(A.x*A.x+A.z*A.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Td(e.vertices,e.indices,e.radius,e.details)}}class Ws extends Td{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],i=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,i,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Ws(e.radius,e.detail)}}class ia extends sn{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,a=0,c=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:a,thetaLength:c},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const u=Math.min(a+c,Math.PI);let h=0;const f=[],p=new F,m=new F,g=[],x=[],M=[],v=[];for(let _=0;_<=n;_++){const A=[],P=_/n;let S=0;_===0&&a===0?S=.5/t:_===n&&u===Math.PI&&(S=-.5/t);for(let k=0;k<=t;k++){const O=k/t;p.x=-e*Math.cos(i+O*s)*Math.sin(a+P*c),p.y=e*Math.cos(a+P*c),p.z=e*Math.sin(i+O*s)*Math.sin(a+P*c),x.push(p.x,p.y,p.z),m.copy(p).normalize(),M.push(m.x,m.y,m.z),v.push(O+S,1-P),A.push(h++)}f.push(A)}for(let _=0;_<n;_++)for(let A=0;A<t;A++){const P=f[_][A+1],S=f[_][A],k=f[_+1][A],O=f[_+1][A+1];(_!==0||a>0)&&g.push(P,S,O),(_!==n-1||u<Math.PI)&&g.push(S,k,O)}this.setIndex(g),this.setAttribute("position",new jt(x,3)),this.setAttribute("normal",new jt(M,3)),this.setAttribute("uv",new jt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ia(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class es extends sn{constructor(e=1,t=.4,n=12,i=48,s=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:i,arc:s},n=Math.floor(n),i=Math.floor(i);const a=[],c=[],u=[],h=[],f=new F,p=new F,m=new F;for(let g=0;g<=n;g++)for(let x=0;x<=i;x++){const M=x/i*s,v=g/n*Math.PI*2;p.x=(e+t*Math.cos(v))*Math.cos(M),p.y=(e+t*Math.cos(v))*Math.sin(M),p.z=t*Math.sin(v),c.push(p.x,p.y,p.z),f.x=e*Math.cos(M),f.y=e*Math.sin(M),m.subVectors(p,f).normalize(),u.push(m.x,m.y,m.z),h.push(x/i),h.push(g/n)}for(let g=1;g<=n;g++)for(let x=1;x<=i;x++){const M=(i+1)*g+x-1,v=(i+1)*(g-1)+x-1,_=(i+1)*(g-1)+x,A=(i+1)*g+x;a.push(M,v,A),a.push(v,_,A)}this.setIndex(a),this.setAttribute("position",new jt(c,3)),this.setAttribute("normal",new jt(u,3)),this.setAttribute("uv",new jt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new es(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class is extends xi{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new Ke(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new Ke(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Eg,this.normalScale=new Qe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new pi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Si extends is{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new Qe(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return vn(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new Ke(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new Ke(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new Ke(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function mc(r,e,t){return!r||!t&&r.constructor===e?r:typeof e.BYTES_PER_ELEMENT=="number"?new e(r):Array.prototype.slice.call(r)}function DR(r){return ArrayBuffer.isView(r)&&!(r instanceof DataView)}function NR(r){function e(i,s){return r[i]-r[s]}const t=r.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}function Fm(r,e,t){const n=r.length,i=new r.constructor(n);for(let s=0,a=0;a!==n;++s){const c=t[s]*e;for(let u=0;u!==e;++u)i[a++]=r[c+u]}return i}function Xg(r,e,t,n){let i=1,s=r[0];for(;s!==void 0&&s[n]===void 0;)s=r[i++];if(s===void 0)return;let a=s[n];if(a!==void 0)if(Array.isArray(a))do a=s[n],a!==void 0&&(e.push(s.time),t.push.apply(t,a)),s=r[i++];while(s!==void 0);else if(a.toArray!==void 0)do a=s[n],a!==void 0&&(e.push(s.time),a.toArray(t,t.length)),s=r[i++];while(s!==void 0);else do a=s[n],a!==void 0&&(e.push(s.time),t.push(a)),s=r[i++];while(s!==void 0)}class ra{constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let a;n:{i:if(!(e<i)){for(let c=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===c)break;if(s=i,i=t[++n],e<i)break t}a=t.length;break n}if(!(e>=s)){const c=t[1];e<c&&(n=2,s=c);for(let u=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===u)break;if(i=s,s=t[--n-1],e>=s)break t}a=n,n=0;break n}break e}for(;n<a;){const c=n+a>>>1;e<t[c]?a=c:n=c+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let a=0;a!==i;++a)t[a]=n[s+a];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class OR extends ra{constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Hs,endingEnd:Hs}}intervalChanged_(e,t,n){const i=this.parameterPositions;let s=e-2,a=e+1,c=i[s],u=i[a];if(c===void 0)switch(this.getSettings_().endingStart){case Vs:s=e,c=2*t-n;break;case Lc:s=i.length-2,c=t+i[s]-i[s+1];break;default:s=e,c=n}if(u===void 0)switch(this.getSettings_().endingEnd){case Vs:a=e,u=2*n-t;break;case Lc:a=1,u=n+i[1]-i[0];break;default:a=e-1,u=t}const h=(n-t)*.5,f=this.valueSize;this._weightPrev=h/(t-c),this._weightNext=h/(u-n),this._offsetPrev=s*f,this._offsetNext=a*f}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=this._offsetPrev,p=this._offsetNext,m=this._weightPrev,g=this._weightNext,x=(n-t)/(i-t),M=x*x,v=M*x,_=-m*v+2*m*M-m*x,A=(1+m)*v+(-1.5-2*m)*M+(-.5+m)*x+1,P=(-1-g)*v+(1.5+g)*M+.5*x,S=g*v-g*M;for(let k=0;k!==c;++k)s[k]=_*a[f+k]+A*a[h+k]+P*a[u+k]+S*a[p+k];return s}}class qg extends ra{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=(n-t)/(i-t),p=1-f;for(let m=0;m!==c;++m)s[m]=a[h+m]*p+a[u+m]*f;return s}}class UR extends ra{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}}class Mi{constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=mc(t,this.TimeBufferType),this.values=mc(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:mc(e.times,Array),values:mc(e.values,Array)};const i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new UR(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new qg(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new OR(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case Qo:t=this.InterpolantFactoryMethodDiscrete;break;case ea:t=this.InterpolantFactoryMethodLinear;break;case bu:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return Qo;case this.InterpolantFactoryMethodLinear:return ea;case this.InterpolantFactoryMethodSmooth:return bu}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){const n=this.times,i=n.length;let s=0,a=i-1;for(;s!==i&&n[s]<e;)++s;for(;a!==-1&&n[a]>t;)--a;if(++a,s!==0||a!==i){s>=a&&(a=Math.max(a,1),s=a-1);const c=this.getValueSize();this.times=n.slice(s,a),this.values=this.values.slice(s*c,a*c)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let a=null;for(let c=0;c!==s;c++){const u=n[c];if(typeof u=="number"&&isNaN(u)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,c,u),e=!1;break}if(a!==null&&a>u){console.error("THREE.KeyframeTrack: Out of order keys.",this,c,u,a),e=!1;break}a=u}if(i!==void 0&&DR(i))for(let c=0,u=i.length;c!==u;++c){const h=i[c];if(isNaN(h)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,c,h),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),i=this.getInterpolation()===bu,s=e.length-1;let a=1;for(let c=1;c<s;++c){let u=!1;const h=e[c],f=e[c+1];if(h!==f&&(c!==1||h!==e[0]))if(i)u=!0;else{const p=c*n,m=p-n,g=p+n;for(let x=0;x!==n;++x){const M=t[p+x];if(M!==t[m+x]||M!==t[g+x]){u=!0;break}}}if(u){if(c!==a){e[a]=e[c];const p=c*n,m=a*n;for(let g=0;g!==n;++g)t[m+g]=t[p+g]}++a}}if(s>0){e[a]=e[s];for(let c=s*n,u=a*n,h=0;h!==n;++h)t[u+h]=t[c+h];++a}return a!==e.length?(this.times=e.slice(0,a),this.values=t.slice(0,a*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}}Mi.prototype.TimeBufferType=Float32Array;Mi.prototype.ValueBufferType=Float32Array;Mi.prototype.DefaultInterpolation=ea;class lo extends Mi{constructor(e,t,n){super(e,t,n)}}lo.prototype.ValueTypeName="bool";lo.prototype.ValueBufferType=Array;lo.prototype.DefaultInterpolation=Qo;lo.prototype.InterpolantFactoryMethodLinear=void 0;lo.prototype.InterpolantFactoryMethodSmooth=void 0;class Yg extends Mi{}Yg.prototype.ValueTypeName="color";class ro extends Mi{}ro.prototype.ValueTypeName="number";class FR extends ra{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=(n-t)/(i-t);let h=e*c;for(let f=h+c;h!==f;h+=4)Wt.slerpFlat(s,0,a,h-c,a,h,u);return s}}class rs extends Mi{InterpolantFactoryMethodLinear(e){return new FR(this.times,this.values,this.getValueSize(),e)}}rs.prototype.ValueTypeName="quaternion";rs.prototype.InterpolantFactoryMethodSmooth=void 0;class uo extends Mi{constructor(e,t,n){super(e,t,n)}}uo.prototype.ValueTypeName="string";uo.prototype.ValueBufferType=Array;uo.prototype.DefaultInterpolation=Qo;uo.prototype.InterpolantFactoryMethodLinear=void 0;uo.prototype.InterpolantFactoryMethodSmooth=void 0;class ss extends Mi{}ss.prototype.ValueTypeName="vector";class Uc{constructor(e="",t=-1,n=[],i=pd){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=fi(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,i=1/(e.fps||1);for(let a=0,c=n.length;a!==c;++a)t.push(kR(n[a]).scale(i));const s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){const t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,a=n.length;s!==a;++s)t.push(Mi.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){const s=t.length,a=[];for(let c=0;c<s;c++){let u=[],h=[];u.push((c+s-1)%s,c,(c+1)%s),h.push(0,1,0);const f=NR(u);u=Fm(u,1,f),h=Fm(h,1,f),!i&&u[0]===0&&(u.push(s),h.push(h[0])),a.push(new ro(".morphTargetInfluences["+t[c].name+"]",u,h).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const i={},s=/^([\w-]*?)([\d]+)$/;for(let c=0,u=e.length;c<u;c++){const h=e[c],f=h.name.match(s);if(f&&f.length>1){const p=f[1];let m=i[p];m||(i[p]=m=[]),m.push(h)}}const a=[];for(const c in i)a.push(this.CreateFromMorphTargetSequence(c,i[c],t,n));return a}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(p,m,g,x,M){if(g.length!==0){const v=[],_=[];Xg(g,v,_,x),v.length!==0&&M.push(new p(m,v,_))}},i=[],s=e.name||"default",a=e.fps||30,c=e.blendMode;let u=e.length||-1;const h=e.hierarchy||[];for(let p=0;p<h.length;p++){const m=h[p].keys;if(!(!m||m.length===0))if(m[0].morphTargets){const g={};let x;for(x=0;x<m.length;x++)if(m[x].morphTargets)for(let M=0;M<m[x].morphTargets.length;M++)g[m[x].morphTargets[M]]=-1;for(const M in g){const v=[],_=[];for(let A=0;A!==m[x].morphTargets.length;++A){const P=m[x];v.push(P.time),_.push(P.morphTarget===M?1:0)}i.push(new ro(".morphTargetInfluence["+M+"]",v,_))}u=g.length*a}else{const g=".bones["+t[p].name+"]";n(ss,g+".position",m,"pos",i),n(rs,g+".quaternion",m,"rot",i),n(ss,g+".scale",m,"scl",i)}}return i.length===0?null:new this(s,u,i,c)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,i=e.length;n!==i;++n){const s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function BR(r){switch(r.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return ro;case"vector":case"vector2":case"vector3":case"vector4":return ss;case"color":return Yg;case"quaternion":return rs;case"bool":case"boolean":return lo;case"string":return uo}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+r)}function kR(r){if(r.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=BR(r.type);if(r.times===void 0){const t=[],n=[];Xg(r.keys,t,n,"value"),r.times=t,r.values=n}return e.parse!==void 0?e.parse(r):new e(r.name,r.times,r.values,r.interpolation)}const pr={enabled:!1,files:{},add:function(r,e){this.enabled!==!1&&(this.files[r]=e)},get:function(r){if(this.enabled!==!1)return this.files[r]},remove:function(r){delete this.files[r]},clear:function(){this.files={}}};class zR{constructor(e,t,n){const i=this;let s=!1,a=0,c=0,u;const h=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(f){c++,s===!1&&i.onStart!==void 0&&i.onStart(f,a,c),s=!0},this.itemEnd=function(f){a++,i.onProgress!==void 0&&i.onProgress(f,a,c),a===c&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(f){i.onError!==void 0&&i.onError(f)},this.resolveURL=function(f){return u?u(f):f},this.setURLModifier=function(f){return u=f,this},this.addHandler=function(f,p){return h.push(f,p),this},this.removeHandler=function(f){const p=h.indexOf(f);return p!==-1&&h.splice(p,2),this},this.getHandler=function(f){for(let p=0,m=h.length;p<m;p+=2){const g=h[p],x=h[p+1];if(g.global&&(g.lastIndex=0),g.test(f))return x}return null}}}const HR=new zR;class os{constructor(e){this.manager=e!==void 0?e:HR,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}os.DEFAULT_MATERIAL_NAME="__DEFAULT";const ki={};class VR extends Error{constructor(e,t){super(e),this.response=t}}class Ed extends os{constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=pr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(ki[e]!==void 0){ki[e].push({onLoad:t,onProgress:n,onError:i});return}ki[e]=[],ki[e].push({onLoad:t,onProgress:n,onError:i});const a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),c=this.mimeType,u=this.responseType;fetch(a).then(h=>{if(h.status===200||h.status===0){if(h.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||h.body===void 0||h.body.getReader===void 0)return h;const f=ki[e],p=h.body.getReader(),m=h.headers.get("X-File-Size")||h.headers.get("Content-Length"),g=m?parseInt(m):0,x=g!==0;let M=0;const v=new ReadableStream({start(_){A();function A(){p.read().then(({done:P,value:S})=>{if(P)_.close();else{M+=S.byteLength;const k=new ProgressEvent("progress",{lengthComputable:x,loaded:M,total:g});for(let O=0,U=f.length;O<U;O++){const z=f[O];z.onProgress&&z.onProgress(k)}_.enqueue(S),A()}},P=>{_.error(P)})}}});return new Response(v)}else throw new VR(`fetch for "${h.url}" responded with ${h.status}: ${h.statusText}`,h)}).then(h=>{switch(u){case"arraybuffer":return h.arrayBuffer();case"blob":return h.blob();case"document":return h.text().then(f=>new DOMParser().parseFromString(f,c));case"json":return h.json();default:if(c===void 0)return h.text();{const p=/charset="?([^;"\s]*)"?/i.exec(c),m=p&&p[1]?p[1].toLowerCase():void 0,g=new TextDecoder(m);return h.arrayBuffer().then(x=>g.decode(x))}}}).then(h=>{pr.add(e,h);const f=ki[e];delete ki[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onLoad&&g.onLoad(h)}}).catch(h=>{const f=ki[e];if(f===void 0)throw this.manager.itemError(e),h;delete ki[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onError&&g.onError(h)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class GR extends os{constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=pr.get(e);if(a!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a;const c=ta("img");function u(){f(),pr.add(e,this),t&&t(this),s.manager.itemEnd(e)}function h(p){f(),i&&i(p),s.manager.itemError(e),s.manager.itemEnd(e)}function f(){c.removeEventListener("load",u,!1),c.removeEventListener("error",h,!1)}return c.addEventListener("load",u,!1),c.addEventListener("error",h,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(c.crossOrigin=this.crossOrigin),s.manager.itemStart(e),c.src=e,c}}class WR extends os{constructor(e){super(e)}load(e,t,n,i){const s=new fn,a=new GR(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(c){s.image=c,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}}class Vc extends Ht{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new Ke(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const Ju=new nt,Bm=new F,km=new F;class Ad{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Qe(512,512),this.map=null,this.mapPass=null,this.matrix=new nt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new _d,this._frameExtents=new Qe(1,1),this._viewportCount=1,this._viewports=[new Et(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Bm.setFromMatrixPosition(e.matrixWorld),t.position.copy(Bm),km.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(km),t.updateMatrixWorld(),Ju.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Ju),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Ju)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class jR extends Ad{constructor(){super(new Cn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=no*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class Rc extends Vc{constructor(e,t,n=0,i=Math.PI/3,s=0,a=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(Ht.DEFAULT_UP),this.updateMatrix(),this.target=new Ht,this.distance=n,this.angle=i,this.penumbra=s,this.decay=a,this.map=null,this.shadow=new jR}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const zm=new nt,ko=new F,Qu=new F;class XR extends Ad{constructor(){super(new Cn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Qe(4,2),this._viewportCount=6,this._viewports=[new Et(2,1,1,1),new Et(0,1,1,1),new Et(3,1,1,1),new Et(1,1,1,1),new Et(3,0,1,1),new Et(1,0,1,1)],this._cubeDirections=[new F(1,0,0),new F(-1,0,0),new F(0,0,1),new F(0,0,-1),new F(0,1,0),new F(0,-1,0)],this._cubeUps=[new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,0,1),new F(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),ko.setFromMatrixPosition(e.matrixWorld),n.position.copy(ko),Qu.copy(n.position),Qu.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(Qu),n.updateMatrixWorld(),i.makeTranslation(-ko.x,-ko.y,-ko.z),zm.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(zm)}}class Kg extends Vc{constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new XR}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class qR extends Ad{constructor(){super(new vd(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class YR extends Vc{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Ht.DEFAULT_UP),this.updateMatrix(),this.target=new Ht,this.shadow=new qR}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class KR extends Vc{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class $o{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class ZR extends os{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=pr.get(e);if(a!==void 0){if(s.manager.itemStart(e),a.then){a.then(h=>{t&&t(h),s.manager.itemEnd(e)}).catch(h=>{i&&i(h)});return}return setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a}const c={};c.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",c.headers=this.requestHeader;const u=fetch(e,c).then(function(h){return h.blob()}).then(function(h){return createImageBitmap(h,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(h){return pr.add(e,h),t&&t(h),s.manager.itemEnd(e),h}).catch(function(h){i&&i(h),pr.remove(e),s.manager.itemError(e),s.manager.itemEnd(e)});pr.add(e,u),s.manager.itemStart(e)}}class $R{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Hm(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Hm();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Hm(){return performance.now()}class JR{constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,a;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,a=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,a=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,a=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=a,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){const n=this.buffer,i=this.valueSize,s=e*i+i;let a=this.cumulativeWeight;if(a===0){for(let c=0;c!==i;++c)n[s+c]=n[c];a=t}else{a+=t;const c=t/a;this._mixBufferRegion(n,s,0,c,i)}this.cumulativeWeight=a}accumulateAdditive(e){const t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){const t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,a=this.cumulativeWeightAdditive,c=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){const u=t*this._origIndex;this._mixBufferRegion(n,i,u,1-s,t)}a>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let u=t,h=t+t;u!==h;++u)if(n[u]!==n[u+t]){c.setValue(n,i);break}}saveOriginalState(){const e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,a=i;s!==a;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){const e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){const e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){const e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let a=0;a!==s;++a)e[t+a]=e[n+a]}_slerp(e,t,n,i){Wt.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){const a=this._workIndex*s;Wt.multiplyQuaternionsFlat(e,a,e,t,e,n),Wt.slerpFlat(e,t,e,t,e,a,i)}_lerp(e,t,n,i,s){const a=1-i;for(let c=0;c!==s;++c){const u=t+c;e[u]=e[u]*a+e[n+c]*i}}_lerpAdditive(e,t,n,i,s){for(let a=0;a!==s;++a){const c=t+a;e[c]=e[c]+e[n+a]*i}}}const wd="\\[\\]\\.:\\/",QR=new RegExp("["+wd+"]","g"),Pd="[^"+wd+"]",eC="[^"+wd.replace("\\.","")+"]",tC=/((?:WC+[\/:])*)/.source.replace("WC",Pd),nC=/(WCOD+)?/.source.replace("WCOD",eC),iC=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Pd),rC=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Pd),sC=new RegExp("^"+tC+nC+iC+rC+"$"),oC=["material","materials","bones","map"];class aC{constructor(e,t,n){const i=n||Pt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class Pt{constructor(e,t,n){this.path=t,this.parsedPath=n||Pt.parseTrackName(t),this.node=Pt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new Pt.Composite(e,t,n):new Pt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(QR,"")}static parseTrackName(e){const t=sC.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){const s=n.nodeName.substring(i+1);oC.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(s){for(let a=0;a<s.length;a++){const c=s[a];if(c.name===t||c.uuid===t)return c;const u=n(c.children);if(u)return u}return null},i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,i=t.propertyName;let s=t.propertyIndex;if(e||(e=Pt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let h=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let f=0;f<e.length;f++)if(e[f].name===h){h=f;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(h!==void 0){if(e[h]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[h]}}const a=e[i];if(a===void 0){const h=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+h+"."+i+" but it wasn't found.",e);return}let c=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?c=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(c=this.Versioning.MatrixWorldNeedsUpdate);let u=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}u=this.BindingType.ArrayElement,this.resolvedProperty=a,this.propertyIndex=s}else a.fromArray!==void 0&&a.toArray!==void 0?(u=this.BindingType.HasFromToArray,this.resolvedProperty=a):Array.isArray(a)?(u=this.BindingType.EntireArray,this.resolvedProperty=a):this.propertyName=i;this.getValue=this.GetterByBindingType[u],this.setValue=this.SetterByBindingTypeAndVersioning[u][c]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}Pt.Composite=aC;Pt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};Pt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};Pt.prototype.GetterByBindingType=[Pt.prototype._getValue_direct,Pt.prototype._getValue_array,Pt.prototype._getValue_arrayElement,Pt.prototype._getValue_toArray];Pt.prototype.SetterByBindingTypeAndVersioning=[[Pt.prototype._setValue_direct,Pt.prototype._setValue_direct_setNeedsUpdate,Pt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[Pt.prototype._setValue_array,Pt.prototype._setValue_array_setNeedsUpdate,Pt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[Pt.prototype._setValue_arrayElement,Pt.prototype._setValue_arrayElement_setNeedsUpdate,Pt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[Pt.prototype._setValue_fromArray,Pt.prototype._setValue_fromArray_setNeedsUpdate,Pt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];class cC{constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;const s=t.tracks,a=s.length,c=new Array(a),u={endingStart:Hs,endingEnd:Hs};for(let h=0;h!==a;++h){const f=s[h].createInterpolant(null);c[h]=f,f.settings=u}this._interpolantSettings=u,this._interpolants=c,this._propertyBindings=new Array(a),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=Mg,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){const i=this._clip.duration,s=e._clip.duration,a=s/i,c=i/s;e.warp(1,a,t),this.warp(c,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){const e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){const i=this._mixer,s=i.time,a=this.timeScale;let c=this._timeScaleInterpolant;c===null&&(c=i._lendControlInterpolant(),this._timeScaleInterpolant=c);const u=c.parameterPositions,h=c.sampleValues;return u[0]=s,u[1]=s+n,h[0]=e/a,h[1]=t/a,this}stopWarping(){const e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}const s=this._startTime;if(s!==null){const u=(e-s)*n;u<0||n===0?t=0:(this._startTime=null,t=n*u)}t*=this._updateTimeScale(e);const a=this._updateTime(t),c=this._updateWeight(e);if(c>0){const u=this._interpolants,h=this._propertyBindings;switch(this.blendMode){case FT:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulateAdditive(c);break;case pd:default:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulate(i,c)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;const n=this._weightInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;const n=this._timeScaleInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){const t=this._clip.duration,n=this.loop;let i=this.time+e,s=this._loopCount;const a=n===UT;if(e===0)return s===-1?i:a&&(s&1)===1?t-i:i;if(n===OT){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,a)):this._setEndings(this.repetitions===0,!0,a)),i>=t||i<0){const c=Math.floor(i/t);i-=t*c,s+=Math.abs(c);const u=this.repetitions-s;if(u<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(u===1){const h=e<0;this._setEndings(h,!h,a)}else this._setEndings(!1,!1,a);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:c})}}else this.time=i;if(a&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){const i=this._interpolantSettings;n?(i.endingStart=Vs,i.endingEnd=Vs):(e?i.endingStart=this.zeroSlopeAtStart?Vs:Hs:i.endingStart=Lc,t?i.endingEnd=this.zeroSlopeAtEnd?Vs:Hs:i.endingEnd=Lc)}_scheduleFading(e,t,n){const i=this._mixer,s=i.time;let a=this._weightInterpolant;a===null&&(a=i._lendControlInterpolant(),this._weightInterpolant=a);const c=a.parameterPositions,u=a.sampleValues;return c[0]=s,u[0]=t,c[1]=s+e,u[1]=n,this}}const lC=new Float32Array(1);class uC extends vr{constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){const n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,a=e._propertyBindings,c=e._interpolants,u=n.uuid,h=this._bindingsByRootAndName;let f=h[u];f===void 0&&(f={},h[u]=f);for(let p=0;p!==s;++p){const m=i[p],g=m.name;let x=f[g];if(x!==void 0)++x.referenceCount,a[p]=x;else{if(x=a[p],x!==void 0){x._cacheIndex===null&&(++x.referenceCount,this._addInactiveBinding(x,u,g));continue}const M=t&&t._propertyBindings[p].binding.parsedPath;x=new JR(Pt.create(n,g,M),m.ValueTypeName,m.getValueSize()),++x.referenceCount,this._addInactiveBinding(x,u,g),a[p]=x}c[p].resultBuffer=x.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){const n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;const e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){const t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){const i=this._actions,s=this._actionsByClip;let a=s[t];if(a===void 0)a={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=a;else{const c=a.knownActions;e._byClipCacheIndex=c.length,c.push(e)}e._cacheIndex=i.length,i.push(e),a.actionByRoot[n]=e}_removeInactiveAction(e){const t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;const s=e._clip.uuid,a=this._actionsByClip,c=a[s],u=c.knownActions,h=u[u.length-1],f=e._byClipCacheIndex;h._byClipCacheIndex=f,u[f]=h,u.pop(),e._byClipCacheIndex=null;const p=c.actionByRoot,m=(e._localRoot||this._root).uuid;delete p[m],u.length===0&&delete a[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){const t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){const t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){const i=this._bindingsByRootAndName,s=this._bindings;let a=i[t];a===void 0&&(a={},i[t]=a),a[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){const t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,a=this._bindingsByRootAndName,c=a[i],u=t[t.length-1],h=e._cacheIndex;u._cacheIndex=h,t[h]=u,t.pop(),delete c[s],Object.keys(c).length===0&&delete a[i]}_lendBinding(e){const t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){const t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){const e=this._controlInterpolants,t=this._nActiveControlInterpolants++;let n=e[t];return n===void 0&&(n=new qg(new Float32Array(2),new Float32Array(2),1,lC),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){const t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){const i=t||this._root,s=i.uuid;let a=typeof e=="string"?Uc.findByName(i,e):e;const c=a!==null?a.uuid:e,u=this._actionsByClip[c];let h=null;if(n===void 0&&(a!==null?n=a.blendMode:n=pd),u!==void 0){const p=u.actionByRoot[s];if(p!==void 0&&p.blendMode===n)return p;h=u.knownActions[0],a===null&&(a=h._clip)}if(a===null)return null;const f=new cC(this,a,t,n);return this._bindAction(f,h),this._addInactiveAction(f,c,s),f}existingAction(e,t){const n=t||this._root,i=n.uuid,s=typeof e=="string"?Uc.findByName(n,e):e,a=s?s.uuid:e,c=this._actionsByClip[a];return c!==void 0&&c.actionByRoot[i]||null}stopAllAction(){const e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;const t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),a=this._accuIndex^=1;for(let h=0;h!==n;++h)t[h]._update(i,e,s,a);const c=this._bindings,u=this._nActiveBindings;for(let h=0;h!==u;++h)c[h].apply(a);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){const t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){const a=s.knownActions;for(let c=0,u=a.length;c!==u;++c){const h=a[c];this._deactivateAction(h);const f=h._cacheIndex,p=t[t.length-1];h._cacheIndex=null,h._byClipCacheIndex=null,p._cacheIndex=f,t[f]=p,t.pop(),this._removeInactiveBindingsForAction(h)}delete i[n]}}uncacheRoot(e){const t=e.uuid,n=this._actionsByClip;for(const a in n){const c=n[a].actionByRoot,u=c[t];u!==void 0&&(this._deactivateAction(u),this._removeInactiveAction(u))}const i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(const a in s){const c=s[a];c.restoreOriginalState(),this._removeInactiveBinding(c)}}uncacheAction(e,t){const n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}}const Vm=new nt;class Zg{constructor(e,t,n=0,i=1/0){this.ray=new oo(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new gd,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Vm.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Vm),this}intersectObject(e,t=!0,n=[]){return nd(e,this,n,t),n.sort(Gm),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)nd(e[i],this,n,t);return n.sort(Gm),n}}function Gm(r,e){return r.distance-e.distance}function nd(r,e,t,n){let i=!0;if(r.layers.test(e.layers)&&r.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const s=r.children;for(let a=0,c=s.length;a<c;a++)nd(s[a],e,t,!0)}}class Wm{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(vn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const cr=new F,gc=new nt,eh=new nt;class hC extends Wg{constructor(e){const t=$g(e),n=new sn,i=[],s=[],a=new Ke(0,0,1),c=new Ke(0,1,0);for(let h=0;h<t.length;h++){const f=t[h];f.parent&&f.parent.isBone&&(i.push(0,0,0),i.push(0,0,0),s.push(a.r,a.g,a.b),s.push(c.r,c.g,c.b))}n.setAttribute("position",new jt(i,3)),n.setAttribute("color",new jt(s,3));const u=new Hc({vertexColors:!0,depthTest:!1,depthWrite:!1,toneMapped:!1,transparent:!0});super(n,u),this.isSkeletonHelper=!0,this.type="SkeletonHelper",this.root=e,this.bones=t,this.matrix=e.matrixWorld,this.matrixAutoUpdate=!1}updateMatrixWorld(e){const t=this.bones,n=this.geometry,i=n.getAttribute("position");eh.copy(this.root.matrixWorld).invert();for(let s=0,a=0;s<t.length;s++){const c=t[s];c.parent&&c.parent.isBone&&(gc.multiplyMatrices(eh,c.matrixWorld),cr.setFromMatrixPosition(gc),i.setXYZ(a,cr.x,cr.y,cr.z),gc.multiplyMatrices(eh,c.parent.matrixWorld),cr.setFromMatrixPosition(gc),i.setXYZ(a+1,cr.x,cr.y,cr.z),a+=2)}n.getAttribute("position").needsUpdate=!0,super.updateMatrixWorld(e)}dispose(){this.geometry.dispose(),this.material.dispose()}}function $g(r){const e=[];r.isBone===!0&&e.push(r);for(let t=0;t<r.children.length;t++)e.push.apply(e,$g(r.children[t]));return e}class Jg extends vr{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(){}disconnect(){}dispose(){}update(){}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:"170"}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__="170");var yi=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},th={},jm;function nn(){return jm||(jm=1,(function(r){var e=Object.defineProperty,t=Object.defineProperties,n=Object.getOwnPropertyDescriptors,i=Object.getOwnPropertySymbols,s=Object.prototype.hasOwnProperty,a=Object.prototype.propertyIsEnumerable,c=(b,L,V)=>L in b?e(b,L,{enumerable:!0,configurable:!0,writable:!0,value:V}):b[L]=V,u=(b,L)=>{for(var V in L||(L={}))s.call(L,V)&&c(b,V,L[V]);if(i)for(var V of i(L))a.call(L,V)&&c(b,V,L[V]);return b},h=(b,L)=>t(b,n(L)),f=b=>e(b,"__esModule",{value:!0}),p=(b,L)=>{f(b);for(var V in L)e(b,V,{get:L[V],enumerable:!0})};p(r,{Atom:()=>Sa,PointerProxy:()=>Cl,Ticker:()=>Ta,getPointerParts:()=>Tr,isPointer:()=>wi,isPrism:()=>_s,iterateAndCountTicks:()=>wl,iterateOver:()=>Rl,pointer:()=>mo,pointerToPrism:()=>ys,prism:()=>Pr,val:()=>bo});var m=Array.isArray,g=m,x=typeof yi=="object"&&yi&&yi.Object===Object&&yi,M=x,v=typeof self=="object"&&self&&self.Object===Object&&self,_=M||v||Function("return this")(),A=_,P=A.Symbol,S=P,k=Object.prototype,O=k.hasOwnProperty,U=k.toString,z=S?S.toStringTag:void 0;function I(b){var L=O.call(b,z),V=b[z];try{b[z]=void 0;var re=!0}catch{}var Je=U.call(b);return re&&(L?b[z]=V:delete b[z]),Je}var w=I,H=Object.prototype,ee=H.toString;function J(b){return ee.call(b)}var oe=J,ce="[object Null]",$="[object Undefined]",le=S?S.toStringTag:void 0;function ne(b){return b==null?b===void 0?$:ce:le&&le in Object(b)?w(b):oe(b)}var ge=ne;function Te(b){return b!=null&&typeof b=="object"}var Oe=Te,Ye="[object Symbol]";function yt(b){return typeof b=="symbol"||Oe(b)&&ge(b)==Ye}var he=yt,me=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Ne=/^\w*$/;function Me(b,L){if(g(b))return!1;var V=typeof b;return V=="number"||V=="symbol"||V=="boolean"||b==null||he(b)?!0:Ne.test(b)||!me.test(b)||L!=null&&b in Object(L)}var Xe=Me;function Ze(b){var L=typeof b;return b!=null&&(L=="object"||L=="function")}var tt=Ze,St="[object AsyncFunction]",rt="[object Function]",At="[object GeneratorFunction]",W="[object Proxy]";function cn(b){if(!tt(b))return!1;var L=ge(b);return L==rt||L==At||L==St||L==W}var ht=cn,ct=A["__core-js_shared__"],Fe=ct,st=(function(){var b=/[^.]+$/.exec(Fe&&Fe.keys&&Fe.keys.IE_PROTO||"");return b?"Symbol(src)_1."+b:""})();function ke(b){return!!st&&st in b}var D=ke,E=Function.prototype,Z=E.toString;function ue(b){if(b!=null){try{return Z.call(b)}catch{}try{return b+""}catch{}}return""}var pe=ue,fe=/[\\^$.*+?()[\]{}|]/g,Ue=/^\[object .+?Constructor\]$/,Pe=Function.prototype,De=Object.prototype,dt=Pe.toString,N=De.hasOwnProperty,Y=RegExp("^"+dt.call(N).replace(fe,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function ae(b){if(!tt(b)||D(b))return!1;var L=ht(b)?Y:Ue;return L.test(pe(b))}var _e=ae;function xe(b,L){return b==null?void 0:b[L]}var Re=xe;function qe(b,L){var V=Re(b,L);return _e(V)?V:void 0}var lt=qe,G=lt(Object,"create"),be=G;function ie(){this.__data__=be?be(null):{},this.size=0}var de=ie;function Ae(b){var L=this.has(b)&&delete this.__data__[b];return this.size-=L?1:0,L}var Ee=Ae,Ge="__lodash_hash_undefined__",ot=Object.prototype,Vt=ot.hasOwnProperty;function pt(b){var L=this.__data__;if(be){var V=L[b];return V===Ge?void 0:V}return Vt.call(L,b)?L[b]:void 0}var An=pt,kn=Object.prototype,as=kn.hasOwnProperty;function cs(b){var L=this.__data__;return be?L[b]!==void 0:as.call(L,b)}var ri=cs,yr="__lodash_hash_undefined__";function ls(b,L){var V=this.__data__;return this.size+=this.has(b)?0:1,V[b]=be&&L===void 0?yr:L,this}var us=ls;function zn(b){var L=-1,V=b==null?0:b.length;for(this.clear();++L<V;){var re=b[L];this.set(re[0],re[1])}}zn.prototype.clear=de,zn.prototype.delete=Ee,zn.prototype.get=An,zn.prototype.has=ri,zn.prototype.set=us;var xr=zn;function Ki(){this.__data__=[],this.size=0}var hs=Ki;function $n(b,L){return b===L||b!==b&&L!==L}var ho=$n;function Ti(b,L){for(var V=b.length;V--;)if(ho(b[V][0],L))return V;return-1}var Zi=Ti,R=Array.prototype,j=R.splice;function Q(b){var L=this.__data__,V=Zi(L,b);if(V<0)return!1;var re=L.length-1;return V==re?L.pop():j.call(L,V,1),--this.size,!0}var te=Q;function X(b){var L=this.__data__,V=Zi(L,b);return V<0?void 0:L[V][1]}var Se=X;function Le(b){return Zi(this.__data__,b)>-1}var ze=Le;function He(b,L){var V=this.__data__,re=Zi(V,b);return re<0?(++this.size,V.push([b,L])):V[re][1]=L,this}var et=He;function $e(b){var L=-1,V=b==null?0:b.length;for(this.clear();++L<V;){var re=b[L];this.set(re[0],re[1])}}$e.prototype.clear=hs,$e.prototype.delete=te,$e.prototype.get=Se,$e.prototype.has=ze,$e.prototype.set=et;var Ve=$e,vt=lt(A,"Map"),wt=vt;function Rt(){this.size=0,this.__data__={hash:new xr,map:new(wt||Ve),string:new xr}}var qt=Rt;function xt(b){var L=typeof b;return L=="string"||L=="number"||L=="symbol"||L=="boolean"?b!=="__proto__":b===null}var We=xt;function Hn(b,L){var V=b.__data__;return We(L)?V[typeof L=="string"?"string":"hash"]:V.map}var gt=Hn;function pn(b){var L=gt(this,b).delete(b);return this.size-=L?1:0,L}var mi=pn;function Zt(b){return gt(this,b).get(b)}var Ei=Zt;function Ct(b){return gt(this,b).has(b)}var Dn=Ct;function Ai(b,L){var V=gt(this,b),re=V.size;return V.set(b,L),this.size+=V.size==re?0:1,this}var yn=Ai;function mn(b){var L=-1,V=b==null?0:b.length;for(this.clear();++L<V;){var re=b[L];this.set(re[0],re[1])}}mn.prototype.clear=qt,mn.prototype.delete=mi,mn.prototype.get=Ei,mn.prototype.has=Dn,mn.prototype.set=yn;var Vn=mn,ds="Expected a function";function fo(b,L){if(typeof b!="function"||L!=null&&typeof L!="function")throw new TypeError(ds);var V=function(){var re=arguments,Je=L?L.apply(this,re):re[0],Mt=V.cache;if(Mt.has(Je))return Mt.get(Je);var gn=b.apply(this,re);return V.cache=Mt.set(Je,gn)||Mt,gn};return V.cache=new(fo.Cache||Vn),V}fo.Cache=Vn;var Gc=fo,$i=500;function fs(b){var L=Gc(b,function(re){return V.size===$i&&V.clear(),re}),V=L.cache;return L}var Wc=fs,br=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,jc=/\\(\\)?/g,Xc=Wc(function(b){var L=[];return b.charCodeAt(0)===46&&L.push(""),b.replace(br,function(V,re,Je,Mt){L.push(Je?Mt.replace(jc,"$1"):re||V)}),L}),qc=Xc;function Yc(b,L){for(var V=-1,re=b==null?0:b.length,Je=Array(re);++V<re;)Je[V]=L(b[V],V,b);return Je}var Kc=Yc,Sr=S?S.prototype:void 0,sa=Sr?Sr.toString:void 0;function oa(b){if(typeof b=="string")return b;if(g(b))return Kc(b,oa)+"";if(he(b))return sa?sa.call(b):"";var L=b+"";return L=="0"&&1/b==-1/0?"-0":L}var Zc=oa;function $c(b){return b==null?"":Zc(b)}var Jc=$c;function Qc(b,L){return g(b)?b:Xe(b,L)?[b]:qc(Jc(b))}var el=Qc;function tl(b){if(typeof b=="string"||he(b))return b;var L=b+"";return L=="0"&&1/b==-1/0?"-0":L}var Ji=tl;function ps(b,L){L=el(L,b);for(var V=0,re=L.length;b!=null&&V<re;)b=b[Ji(L[V++])];return V&&V==re?b:void 0}var nl=ps;function po(b,L,V){var re=b==null?void 0:nl(b,L);return re===void 0?V:re}var il=po;function rl(b,L){return function(V){return b(L(V))}}var sl=rl,ol=sl(Object.getPrototypeOf,Object),al=ol,cl="[object Object]",ll=Function.prototype,ul=Object.prototype,aa=ll.toString,hl=ul.hasOwnProperty,ca=aa.call(Object);function la(b){if(!Oe(b)||ge(b)!=cl)return!1;var L=al(b);if(L===null)return!0;var V=hl.call(L,"constructor")&&L.constructor;return typeof V=="function"&&V instanceof V&&aa.call(V)==ca}var ua=la;function ha(b){var L=b==null?0:b.length;return L?b[L-1]:void 0}var dl=ha,ms=new WeakMap,da=new WeakMap,Mr=Symbol("pointerMeta"),fl={get(b,L){if(L===Mr)return ms.get(b);let V=da.get(b);V||(V=new Map,da.set(b,V));const re=V.get(L);if(re!==void 0)return re;const Je=ms.get(b),Mt=gs({root:Je.root,path:[...Je.path,L]});return V.set(L,Mt),Mt}},si=b=>b[Mr],Tr=b=>{const{root:L,path:V}=si(b);return{root:L,path:V}};function gs(b){var L;const V={root:b.root,path:(L=b.path)!=null?L:[]},re={};return ms.set(re,V),new Proxy(re,fl)}var mo=gs,wi=b=>b&&!!si(b);function fa(b,L,V){return L.length===0?V(b):Qi(b,L,V)}var Qi=(b,L,V)=>{if(L.length===0)return V(b);if(Array.isArray(b)){let[re,...Je]=L;re=parseInt(String(re),10),isNaN(re)&&(re=0);const Mt=b[re],gn=Qi(Mt,Je,V);if(Mt===gn)return b;const Jn=[...b];return Jn.splice(re,1,gn),Jn}else if(typeof b=="object"&&b!==null){const[re,...Je]=L,Mt=b[re],gn=Qi(Mt,Je,V);return Mt===gn?b:h(u({},b),{[re]:gn})}else{const[re,...Je]=L;return{[re]:Qi(void 0,Je,V)}}},en=class{constructor(){this._head=void 0}peek(){return this._head&&this._head.data}pop(){const b=this._head;if(b)return this._head=b.next,b.data}push(b){const L={next:this._head,data:b};this._head=L}};function _s(b){return!!(b&&b.isPrism&&b.isPrism===!0)}function go(){const b=()=>{},L=new en,V=b;return{type:"Dataverse_discoveryMechanism",startIgnoringDependencies:()=>{L.push(V)},stopIgnoringDependencies:()=>{L.peek()!==V||L.pop()},reportResolutionStart:er=>{const Rr=L.peek();Rr&&Rr(er),L.push(V)},reportResolutionEnd:er=>{L.pop()},pushCollector:er=>{L.push(er)},popCollector:er=>{if(L.peek()!==er)throw new Error("Popped collector is not on top of the stack");L.pop()}}}function pl(){const b="__dataverse_discoveryMechanism_sharedStack",L=typeof window<"u"?window:typeof yi<"u"?yi:{};if(L){const V=L[b];if(V&&typeof V=="object"&&V.type==="Dataverse_discoveryMechanism")return V;{const re=go();return L[b]=re,re}}else return go()}var{startIgnoringDependencies:Pi,stopIgnoringDependencies:Er,reportResolutionEnd:ml,reportResolutionStart:gl,pushCollector:_o,popCollector:_l}=pl(),pa=()=>{},vl=class{constructor(b,L){this._fn=b,this._prismInstance=L,this._didMarkDependentsAsStale=!1,this._isFresh=!1,this._cacheOfDendencyValues=new Map,this._dependents=new Set,this._dependencies=new Set,this._possiblyStaleDeps=new Set,this._scope=new ma(this),this._lastValue=void 0,this._forciblySetToStale=!1,this._reactToDependencyGoingStale=V=>{this._possiblyStaleDeps.add(V),this._markAsStale()};for(const V of this._dependencies)V._addDependent(this._reactToDependencyGoingStale);Pi(),this.getValue(),Er()}get hasDependents(){return this._dependents.size>0}removeDependent(b){this._dependents.delete(b)}addDependent(b){this._dependents.add(b)}destroy(){for(const b of this._dependencies)b._removeDependent(this._reactToDependencyGoingStale);ga(this._scope)}getValue(){if(!this._isFresh){const b=this._recalculate();this._lastValue=b,this._isFresh=!0,this._didMarkDependentsAsStale=!1,this._forciblySetToStale=!1}return this._lastValue}_recalculate(){let b;if(!this._forciblySetToStale&&this._possiblyStaleDeps.size>0){let re=!1;Pi();for(const Je of this._possiblyStaleDeps)if(this._cacheOfDendencyValues.get(Je)!==Je.getValue()){re=!0;break}if(Er(),this._possiblyStaleDeps.clear(),!re)return this._lastValue}const L=new Set;this._cacheOfDendencyValues.clear();const V=re=>{L.add(re),this._addDependency(re)};_o(V),ln.push(this._scope);try{b=this._fn()}catch(re){console.error(re)}finally{ln.pop()!==this._scope&&console.warn("The Prism hook stack has slipped. This is a bug.")}_l(V);for(const re of this._dependencies)L.has(re)||this._removeDependency(re);this._dependencies=L,Pi();for(const re of L)this._cacheOfDendencyValues.set(re,re.getValue());return Er(),b}forceStale(){this._forciblySetToStale=!0,this._markAsStale()}_markAsStale(){if(!this._didMarkDependentsAsStale){this._didMarkDependentsAsStale=!0,this._isFresh=!1;for(const b of this._dependents)b(this._prismInstance)}}_addDependency(b){this._dependencies.has(b)||(this._dependencies.add(b),b._addDependent(this._reactToDependencyGoingStale))}_removeDependency(b){this._dependencies.has(b)&&(this._dependencies.delete(b),b._removeDependent(this._reactToDependencyGoingStale))}},vo={},yl=class{constructor(b){this._fn=b,this.isPrism=!0,this._state={hot:!1,handle:void 0}}get isHot(){return this._state.hot}onChange(b,L,V=!1){const re=()=>{b.onThisOrNextTick(Mt)};let Je=vo;const Mt=()=>{const Jn=this.getValue();Jn!==Je&&(Je=Jn,L(Jn))};return this._addDependent(re),V&&(Je=this.getValue(),L(Je)),()=>{this._removeDependent(re),b.offThisOrNextTick(Mt),b.offNextTick(Mt)}}onStale(b){const L=()=>{this._removeDependent(V)},V=()=>b();return this._addDependent(V),L}keepHot(){return this.onStale(()=>{})}_addDependent(b){this._state.hot||this._goHot(),this._state.handle.addDependent(b)}_goHot(){const b=new vl(this._fn,this);this._state={hot:!0,handle:b}}_removeDependent(b){const L=this._state;if(!L.hot)return;const V=L.handle;V.removeDependent(b),V.hasDependents||(this._state={hot:!1,handle:void 0},V.destroy())}getValue(){gl(this);const b=this._state;let L;return b.hot?L=b.handle.getValue():L=wr(this._fn),ml(this),L}},ma=class{constructor(b){this._hotHandle=b,this._refs=new Map,this.isPrismScope=!0,this.subs={},this.effects=new Map,this.memos=new Map}ref(b,L){let V=this._refs.get(b);if(V!==void 0)return V;{const re={current:L};return this._refs.set(b,re),re}}effect(b,L,V){let re=this.effects.get(b);re===void 0&&(re={cleanup:pa,deps:void 0},this.effects.set(b,re)),_a(re.deps,V)&&(re.cleanup(),Pi(),re.cleanup=vs(L,pa).value,Er(),re.deps=V)}memo(b,L,V){let re=this.memos.get(b);return re===void 0&&(re={cachedValue:null,deps:void 0},this.memos.set(b,re)),_a(re.deps,V)&&(Pi(),re.cachedValue=vs(L,void 0).value,Er(),re.deps=V),re.cachedValue}state(b,L){const{value:V,setValue:re}=this.memo("state/"+b,()=>{const Je={current:L};return{value:Je,setValue:gn=>{Je.current=gn,this._hotHandle.forceStale()}}},[]);return[V.current,re]}sub(b){return this.subs[b]||(this.subs[b]=new ma(this._hotHandle)),this.subs[b]}cleanupEffects(){for(const b of this.effects.values())vs(b.cleanup,void 0);this.effects.clear()}source(b,L){return this.effect("$$source/blah",()=>b(()=>{this._hotHandle.forceStale()}),[b]),L()}};function ga(b){for(const L of Object.values(b.subs))ga(L);b.cleanupEffects()}function vs(b,L){try{return{value:b(),ok:!0}}catch(V){return setTimeout(function(){throw V}),{value:L,ok:!1}}}var ln=new en;function xl(b,L){const V=ln.peek();if(!V)throw new Error("prism.ref() is called outside of a prism() call.");return V.ref(b,L)}function yo(b,L,V){const re=ln.peek();if(!re)throw new Error("prism.effect() is called outside of a prism() call.");return re.effect(b,L,V)}function _a(b,L){if(b===void 0||L===void 0)return!0;const V=b.length;if(V!==L.length)return!0;for(let re=0;re<V;re++)if(b[re]!==L[re])return!0;return!1}function va(b,L,V){const re=ln.peek();if(!re)throw new Error("prism.memo() is called outside of a prism() call.");return re.memo(b,L,V)}function wn(b,L){const V=ln.peek();if(!V)throw new Error("prism.state() is called outside of a prism() call.");return V.state(b,L)}function bl(){if(!ln.peek())throw new Error("The parent function is called outside of a prism() call.")}function Sl(b,L){const V=ln.peek();if(!V)throw new Error("prism.scope() is called outside of a prism() call.");const re=V.sub(b);ln.push(re);const Je=vs(L,void 0).value;return ln.pop(),Je}function Ml(b,L,V){return va(b,()=>tn(L),V).getValue()}function ya(){return!!ln.peek()}function Tl(b,L){const V=ln.peek();if(!V)throw new Error("prism.source() is called outside of a prism() call.");return V.source(b,L)}var tn=b=>new yl(b),Ar=class{effect(b,L,V){console.warn("prism.effect() does not run in cold prisms")}memo(b,L,V){return L()}state(b,L){return[L,()=>{}]}ref(b,L){return{current:L}}sub(b){return new Ar}source(b,L){return L()}};function wr(b){const L=new Ar;ln.push(L);let V;try{V=b()}catch(re){console.error(re)}finally{ln.pop()!==L&&console.warn("The Prism hook stack has slipped. This is a bug.")}return V}tn.ref=xl,tn.effect=yo,tn.memo=va,tn.ensurePrism=bl,tn.state=wn,tn.scope=Sl,tn.sub=Ml,tn.inPrism=ya,tn.source=Tl;var Pr=tn,xa;(function(b){b[b.Dict=0]="Dict",b[b.Array=1]="Array",b[b.Other=2]="Other"})(xa||(xa={}));var It=b=>Array.isArray(b)?1:ua(b)?0:2,xo=(b,L,V=It(b))=>V===0&&typeof L=="string"||V===1&&El(L)?b[L]:void 0,El=b=>{const L=typeof b=="number"?b:parseInt(b,10);return!isNaN(L)&&L>=0&&L<1/0&&(L|0)===L},ba=class{constructor(b,L){this._parent=b,this._path=L,this.children=new Map,this.identityChangeListeners=new Set}addIdentityChangeListener(b){this.identityChangeListeners.add(b)}removeIdentityChangeListener(b){this.identityChangeListeners.delete(b),this._checkForGC()}removeChild(b){this.children.delete(b),this._checkForGC()}getChild(b){return this.children.get(b)}getOrCreateChild(b){let L=this.children.get(b);return L||(L=L=new ba(this,this._path.concat([b])),this.children.set(b,L)),L}_checkForGC(){this.identityChangeListeners.size>0||this.children.size>0||this._parent&&this._parent.removeChild(dl(this._path))}},Sa=class{constructor(b){this.$$isPointerToPrismProvider=!0,this.pointer=mo({root:this,path:[]}),this.prism=this.pointerToPrism(this.pointer),this._onPointerValueChange=(L,V)=>{const{path:re}=Tr(L),Je=this._getOrCreateScopeForPath(re);return Je.identityChangeListeners.add(V),()=>{Je.identityChangeListeners.delete(V)}},this._currentState=b,this._rootScope=new ba(void 0,[])}set(b){const L=this._currentState;this._currentState=b,this._checkUpdates(this._rootScope,L,b)}get(){return this._currentState}getByPointer(b){const L=wi(b)?b:b(this.pointer),V=Tr(L).path;return this._getIn(V)}_getIn(b){return b.length===0?this.get():il(this.get(),b)}reduce(b){this.set(b(this.get()))}reduceByPointer(b,L){const V=wi(b)?b:b(this.pointer),re=Tr(V).path,Je=fa(this.get(),re,L);this.set(Je)}setByPointer(b,L){this.reduceByPointer(b,()=>L)}_checkUpdates(b,L,V){if(L===V)return;for(const Mt of b.identityChangeListeners)Mt(V);if(b.children.size===0)return;const re=It(L),Je=It(V);if(!(re===2&&re===Je))for(const[Mt,gn]of b.children){const Jn=xo(L,Mt,re),Ea=xo(V,Mt,Je);this._checkUpdates(gn,Jn,Ea)}}_getOrCreateScopeForPath(b){let L=this._rootScope;for(const V of b)L=L.getOrCreateChild(V);return L}pointerToPrism(b){const{path:L}=Tr(b),V=Je=>this._onPointerValueChange(b,Je),re=()=>this._getIn(L);return Pr(()=>Pr.source(V,re))}},Ma=new WeakMap;function Al(b){return typeof b=="object"&&b!==null&&b.$$isPointerToPrismProvider===!0}var ys=b=>{const L=si(b);let V=Ma.get(L);if(!V){const re=L.root;if(!Al(re))throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");V=re.pointerToPrism(b),Ma.set(L,V)}return V},bo=b=>wi(b)?ys(b).getValue():_s(b)?b.getValue():b;function*wl(b){let L;if(wi(b))L=ys(b);else if(_s(b))L=b;else throw new Error("Only pointers and prisms are supported");let V=0;const re=L.onStale(()=>{V++});try{for(;;){const Je=V;V=0,yield{value:L.getValue(),ticks:Je}}}finally{re()}}var Pl=180,Ta=class{constructor(b){this._conf=b,this._ticking=!1,this._dormant=!0,this._numberOfDormantTicks=0,this.__ticks=0,this._scheduledForThisOrNextTick=new Set,this._scheduledForNextTick=new Set,this._timeAtCurrentTick=0}get dormant(){return this._dormant}onThisOrNextTick(b){this._scheduledForThisOrNextTick.add(b),this._dormant&&this._goActive()}onNextTick(b){this._scheduledForNextTick.add(b),this._dormant&&this._goActive()}offThisOrNextTick(b){this._scheduledForThisOrNextTick.delete(b)}offNextTick(b){this._scheduledForNextTick.delete(b)}get time(){return this._ticking?this._timeAtCurrentTick:performance.now()}_goActive(){var b,L;this._dormant&&(this._dormant=!1,(L=(b=this._conf)==null?void 0:b.onActive)==null||L.call(b))}_goDormant(){var b,L;this._dormant||(this._dormant=!0,this._numberOfDormantTicks=0,(L=(b=this._conf)==null?void 0:b.onDormant)==null||L.call(b))}tick(b=performance.now()){if(this.__ticks++,!this._dormant&&this._scheduledForNextTick.size===0&&this._scheduledForThisOrNextTick.size===0&&(this._numberOfDormantTicks++,this._numberOfDormantTicks>=Pl)){this._goDormant();return}this._ticking=!0,this._timeAtCurrentTick=b;for(const L of this._scheduledForNextTick)this._scheduledForThisOrNextTick.add(L);this._scheduledForNextTick.clear(),this._tick(0),this._ticking=!1}_tick(b){const L=this.time;if(b>10&&console.warn("_tick() recursing for 10 times"),b>100)throw new Error("Maximum recursion limit for _tick()");const V=this._scheduledForThisOrNextTick;this._scheduledForThisOrNextTick=new Set;for(const re of V)re(L);if(this._scheduledForThisOrNextTick.size>0)return this._tick(b+1)}};function*Rl(b){let L;if(wi(b))L=ys(b);else if(_s(b))L=b;else throw new Error("Only pointers and prisms are supported");const V=new Ta,re=L.onChange(V,Je=>{});try{for(;;)V.tick(),yield L.getValue()}finally{re()}}var Cl=class{constructor(b){this.$$isPointerToPrismProvider=!0,this._currentPointerBox=new Sa(b),this.pointer=mo({root:this,path:[]})}setPointer(b){this._currentPointerBox.set(b)}pointerToPrism(b){const{path:L}=si(b);return Pr(()=>{const V=this._currentPointerBox.prism.getValue(),re=L.reduce((Je,Mt)=>Je[Mt],V);return bo(re)})}}})(th)),th}const Xm={type:"change"},Rd={type:"start"},Qg={type:"end"},_c=new oo,qm=new hr,dC=Math.cos(70*wg.DEG2RAD),rn=new F,Un=2*Math.PI,Nt={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},nh=1e-6;class fC extends Jg{constructor(e,t=null){super(e,t),this.state=Nt.NONE,this.enabled=!0,this.target=new F,this.cursor=new F,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:js.ROTATE,MIDDLE:js.DOLLY,RIGHT:js.PAN},this.touches={ONE:zs.ROTATE,TWO:zs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new F,this._lastQuaternion=new Wt,this._lastTargetPosition=new F,this._quat=new Wt().setFromUnitVectors(e.up,new F(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new Wm,this._sphericalDelta=new Wm,this._scale=1,this._panOffset=new F,this._rotateStart=new Qe,this._rotateEnd=new Qe,this._rotateDelta=new Qe,this._panStart=new Qe,this._panEnd=new Qe,this._panDelta=new Qe,this._dollyStart=new Qe,this._dollyEnd=new Qe,this._dollyDelta=new Qe,this._dollyDirection=new F,this._mouse=new Qe,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=mC.bind(this),this._onPointerDown=pC.bind(this),this._onPointerUp=gC.bind(this),this._onContextMenu=MC.bind(this),this._onMouseWheel=yC.bind(this),this._onKeyDown=xC.bind(this),this._onTouchStart=bC.bind(this),this._onTouchMove=SC.bind(this),this._onMouseDown=_C.bind(this),this._onMouseMove=vC.bind(this),this._interceptControlDown=TC.bind(this),this._interceptControlUp=EC.bind(this),this.domElement!==null&&this.connect(),this.update()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Xm),this.update(),this.state=Nt.NONE}update(e=null){const t=this.object.position;rn.copy(t).sub(this.target),rn.applyQuaternion(this._quat),this._spherical.setFromVector3(rn),this.autoRotate&&this.state===Nt.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,i=this.maxAzimuthAngle;isFinite(n)&&isFinite(i)&&(n<-Math.PI?n+=Un:n>Math.PI&&(n-=Un),i<-Math.PI?i+=Un:i>Math.PI&&(i-=Un),n<=i?this._spherical.theta=Math.max(n,Math.min(i,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+i)/2?Math.max(n,this._spherical.theta):Math.min(i,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const a=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=a!=this._spherical.radius}if(rn.setFromSpherical(this._spherical),rn.applyQuaternion(this._quatInverse),t.copy(this.target).add(rn),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let a=null;if(this.object.isPerspectiveCamera){const c=rn.length();a=this._clampDistance(c*this._scale);const u=c-a;this.object.position.addScaledVector(this._dollyDirection,u),this.object.updateMatrixWorld(),s=!!u}else if(this.object.isOrthographicCamera){const c=new F(this._mouse.x,this._mouse.y,0);c.unproject(this.object);const u=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=u!==this.object.zoom;const h=new F(this._mouse.x,this._mouse.y,0);h.unproject(this.object),this.object.position.sub(h).add(c),this.object.updateMatrixWorld(),a=rn.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;a!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(a).add(this.object.position):(_c.origin.copy(this.object.position),_c.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(_c.direction))<dC?this.object.lookAt(this.target):(qm.setFromNormalAndCoplanarPoint(this.object.up,this.target),_c.intersectPlane(qm,this.target))))}else if(this.object.isOrthographicCamera){const a=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),a!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>nh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>nh||this._lastTargetPosition.distanceToSquared(this.target)>nh?(this.dispatchEvent(Xm),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?Un/60*this.autoRotateSpeed*e:Un/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){rn.setFromMatrixColumn(t,0),rn.multiplyScalar(-e),this._panOffset.add(rn)}_panUp(e,t){this.screenSpacePanning===!0?rn.setFromMatrixColumn(t,1):(rn.setFromMatrixColumn(t,0),rn.crossVectors(this.object.up,rn)),rn.multiplyScalar(e),this._panOffset.add(rn)}_pan(e,t){const n=this.domElement;if(this.object.isPerspectiveCamera){const i=this.object.position;rn.copy(i).sub(this.target);let s=rn.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/n.clientHeight,this.object.matrix),this._panUp(2*t*s/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const n=this.domElement.getBoundingClientRect(),i=e-n.left,s=t-n.top,a=n.width,c=n.height;this._mouse.x=i/a*2-1,this._mouse.y=-(s/c)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Un*this._rotateDelta.x/t.clientHeight),this._rotateUp(Un*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(Un*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(-Un*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(Un*this.rotateSpeed/this.domElement.clientHeight):this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(-Un*this.rotateSpeed/this.domElement.clientHeight):this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._rotateStart.set(n,i)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panStart.set(n,i)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const n=this._getSecondPointerPosition(e),i=.5*(e.pageX+n.x),s=.5*(e.pageY+n.y);this._rotateEnd.set(i,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Un*this._rotateDelta.x/t.clientHeight),this._rotateUp(Un*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panEnd.set(n,i)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const a=(e.pageX+t.x)*.5,c=(e.pageY+t.y)*.5;this._updateZoomParameters(a,c)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new Qe,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}}function pC(r){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(r)&&(this._addPointer(r),r.pointerType==="touch"?this._onTouchStart(r):this._onMouseDown(r)))}function mC(r){this.enabled!==!1&&(r.pointerType==="touch"?this._onTouchMove(r):this._onMouseMove(r))}function gC(r){switch(this._removePointer(r),this._pointers.length){case 0:this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(Qg),this.state=Nt.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function _C(r){let e;switch(r.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case js.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(r),this.state=Nt.DOLLY;break;case js.ROTATE:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Nt.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Nt.ROTATE}break;case js.PAN:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Nt.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Nt.PAN}break;default:this.state=Nt.NONE}this.state!==Nt.NONE&&this.dispatchEvent(Rd)}function vC(r){switch(this.state){case Nt.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(r);break;case Nt.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(r);break;case Nt.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(r);break}}function yC(r){this.enabled===!1||this.enableZoom===!1||this.state!==Nt.NONE||(r.preventDefault(),this.dispatchEvent(Rd),this._handleMouseWheel(this._customWheelEvent(r)),this.dispatchEvent(Qg))}function xC(r){this.enabled===!1||this.enablePan===!1||this._handleKeyDown(r)}function bC(r){switch(this._trackPointer(r),this._pointers.length){case 1:switch(this.touches.ONE){case zs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(r),this.state=Nt.TOUCH_ROTATE;break;case zs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(r),this.state=Nt.TOUCH_PAN;break;default:this.state=Nt.NONE}break;case 2:switch(this.touches.TWO){case zs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(r),this.state=Nt.TOUCH_DOLLY_PAN;break;case zs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(r),this.state=Nt.TOUCH_DOLLY_ROTATE;break;default:this.state=Nt.NONE}break;default:this.state=Nt.NONE}this.state!==Nt.NONE&&this.dispatchEvent(Rd)}function SC(r){switch(this._trackPointer(r),this.state){case Nt.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(r),this.update();break;case Nt.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(r),this.update();break;case Nt.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(r),this.update();break;case Nt.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(r),this.update();break;default:this.state=Nt.NONE}}function MC(r){this.enabled!==!1&&r.preventDefault()}function TC(r){r.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function EC(r){r.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}const Yr=new Zg,En=new F,lr=new F,Xt=new Wt,Ym={X:new F(1,0,0),Y:new F(0,1,0),Z:new F(0,0,1)},ih={type:"change"},Km={type:"mouseDown",mode:null},Zm={type:"mouseUp",mode:null},$m={type:"objectChange"};class AC extends Jg{constructor(e,t=null){super(void 0,t);const n=new LC(this);this._root=n;const i=new DC;this._gizmo=i,n.add(i);const s=new NC;this._plane=s,n.add(s);const a=this;function c(P,S){let k=S;Object.defineProperty(a,P,{get:function(){return k!==void 0?k:S},set:function(O){k!==O&&(k=O,s[P]=O,i[P]=O,a.dispatchEvent({type:P+"-changed",value:O}),a.dispatchEvent(ih))}}),a[P]=S,s[P]=S,i[P]=S}c("camera",e),c("object",void 0),c("enabled",!0),c("axis",null),c("mode","translate"),c("translationSnap",null),c("rotationSnap",null),c("scaleSnap",null),c("space","world"),c("size",1),c("dragging",!1),c("showX",!0),c("showY",!0),c("showZ",!0),c("minX",-1/0),c("maxX",1/0),c("minY",-1/0),c("maxY",1/0),c("minZ",-1/0),c("maxZ",1/0);const u=new F,h=new F,f=new Wt,p=new Wt,m=new F,g=new Wt,x=new F,M=new F,v=new F,_=0,A=new F;c("worldPosition",u),c("worldPositionStart",h),c("worldQuaternion",f),c("worldQuaternionStart",p),c("cameraPosition",m),c("cameraQuaternion",g),c("pointStart",x),c("pointEnd",M),c("rotationAxis",v),c("rotationAngle",_),c("eye",A),this._offset=new F,this._startNorm=new F,this._endNorm=new F,this._cameraScale=new F,this._parentPosition=new F,this._parentQuaternion=new Wt,this._parentQuaternionInv=new Wt,this._parentScale=new F,this._worldScaleStart=new F,this._worldQuaternionInv=new Wt,this._worldScale=new F,this._positionStart=new F,this._quaternionStart=new Wt,this._scaleStart=new F,this._getPointer=wC.bind(this),this._onPointerDown=RC.bind(this),this._onPointerHover=PC.bind(this),this._onPointerMove=CC.bind(this),this._onPointerUp=IC.bind(this),t!==null&&this.connect()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointermove",this._onPointerHover),this.domElement.addEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerHover),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="auto"}getHelper(){return this._root}pointerHover(e){if(this.object===void 0||this.dragging===!0)return;e!==null&&Yr.setFromCamera(e,this.camera);const t=rh(this._gizmo.picker[this.mode],Yr);t?this.axis=t.object.name:this.axis=null}pointerDown(e){if(!(this.object===void 0||this.dragging===!0||e!=null&&e.button!==0)&&this.axis!==null){e!==null&&Yr.setFromCamera(e,this.camera);const t=rh(this._plane,Yr,!0);t&&(this.object.updateMatrixWorld(),this.object.parent.updateMatrixWorld(),this._positionStart.copy(this.object.position),this._quaternionStart.copy(this.object.quaternion),this._scaleStart.copy(this.object.scale),this.object.matrixWorld.decompose(this.worldPositionStart,this.worldQuaternionStart,this._worldScaleStart),this.pointStart.copy(t.point).sub(this.worldPositionStart)),this.dragging=!0,Km.mode=this.mode,this.dispatchEvent(Km)}}pointerMove(e){const t=this.axis,n=this.mode,i=this.object;let s=this.space;if(n==="scale"?s="local":(t==="E"||t==="XYZE"||t==="XYZ")&&(s="world"),i===void 0||t===null||this.dragging===!1||e!==null&&e.button!==-1)return;e!==null&&Yr.setFromCamera(e,this.camera);const a=rh(this._plane,Yr,!0);if(a){if(this.pointEnd.copy(a.point).sub(this.worldPositionStart),n==="translate")this._offset.copy(this.pointEnd).sub(this.pointStart),s==="local"&&t!=="XYZ"&&this._offset.applyQuaternion(this._worldQuaternionInv),t.indexOf("X")===-1&&(this._offset.x=0),t.indexOf("Y")===-1&&(this._offset.y=0),t.indexOf("Z")===-1&&(this._offset.z=0),s==="local"&&t!=="XYZ"?this._offset.applyQuaternion(this._quaternionStart).divide(this._parentScale):this._offset.applyQuaternion(this._parentQuaternionInv).divide(this._parentScale),i.position.copy(this._offset).add(this._positionStart),this.translationSnap&&(s==="local"&&(i.position.applyQuaternion(Xt.copy(this._quaternionStart).invert()),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.position.applyQuaternion(this._quaternionStart)),s==="world"&&(i.parent&&i.position.add(En.setFromMatrixPosition(i.parent.matrixWorld)),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.parent&&i.position.sub(En.setFromMatrixPosition(i.parent.matrixWorld)))),i.position.x=Math.max(this.minX,Math.min(this.maxX,i.position.x)),i.position.y=Math.max(this.minY,Math.min(this.maxY,i.position.y)),i.position.z=Math.max(this.minZ,Math.min(this.maxZ,i.position.z));else if(n==="scale"){if(t.search("XYZ")!==-1){let c=this.pointEnd.length()/this.pointStart.length();this.pointEnd.dot(this.pointStart)<0&&(c*=-1),lr.set(c,c,c)}else En.copy(this.pointStart),lr.copy(this.pointEnd),En.applyQuaternion(this._worldQuaternionInv),lr.applyQuaternion(this._worldQuaternionInv),lr.divide(En),t.search("X")===-1&&(lr.x=1),t.search("Y")===-1&&(lr.y=1),t.search("Z")===-1&&(lr.z=1);i.scale.copy(this._scaleStart).multiply(lr),this.scaleSnap&&(t.search("X")!==-1&&(i.scale.x=Math.round(i.scale.x/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Y")!==-1&&(i.scale.y=Math.round(i.scale.y/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Z")!==-1&&(i.scale.z=Math.round(i.scale.z/this.scaleSnap)*this.scaleSnap||this.scaleSnap))}else if(n==="rotate"){this._offset.copy(this.pointEnd).sub(this.pointStart);const c=20/this.worldPosition.distanceTo(En.setFromMatrixPosition(this.camera.matrixWorld));let u=!1;t==="XYZE"?(this.rotationAxis.copy(this._offset).cross(this.eye).normalize(),this.rotationAngle=this._offset.dot(En.copy(this.rotationAxis).cross(this.eye))*c):(t==="X"||t==="Y"||t==="Z")&&(this.rotationAxis.copy(Ym[t]),En.copy(Ym[t]),s==="local"&&En.applyQuaternion(this.worldQuaternion),En.cross(this.eye),En.length()===0?u=!0:this.rotationAngle=this._offset.dot(En.normalize())*c),(t==="E"||u)&&(this.rotationAxis.copy(this.eye),this.rotationAngle=this.pointEnd.angleTo(this.pointStart),this._startNorm.copy(this.pointStart).normalize(),this._endNorm.copy(this.pointEnd).normalize(),this.rotationAngle*=this._endNorm.cross(this._startNorm).dot(this.eye)<0?1:-1),this.rotationSnap&&(this.rotationAngle=Math.round(this.rotationAngle/this.rotationSnap)*this.rotationSnap),s==="local"&&t!=="E"&&t!=="XYZE"?(i.quaternion.copy(this._quaternionStart),i.quaternion.multiply(Xt.setFromAxisAngle(this.rotationAxis,this.rotationAngle)).normalize()):(this.rotationAxis.applyQuaternion(this._parentQuaternionInv),i.quaternion.copy(Xt.setFromAxisAngle(this.rotationAxis,this.rotationAngle)),i.quaternion.multiply(this._quaternionStart).normalize())}this.dispatchEvent(ih),this.dispatchEvent($m)}}pointerUp(e){e!==null&&e.button!==0||(this.dragging&&this.axis!==null&&(Zm.mode=this.mode,this.dispatchEvent(Zm)),this.dragging=!1,this.axis=null)}dispose(){this.disconnect(),this._root.dispose()}attach(e){return this.object=e,this._root.visible=!0,this}detach(){return this.object=void 0,this.axis=null,this._root.visible=!1,this}reset(){this.enabled&&this.dragging&&(this.object.position.copy(this._positionStart),this.object.quaternion.copy(this._quaternionStart),this.object.scale.copy(this._scaleStart),this.dispatchEvent(ih),this.dispatchEvent($m),this.pointStart.copy(this.pointEnd))}getRaycaster(){return Yr}getMode(){return this.mode}setMode(e){this.mode=e}setTranslationSnap(e){this.translationSnap=e}setRotationSnap(e){this.rotationSnap=e}setScaleSnap(e){this.scaleSnap=e}setSize(e){this.size=e}setSpace(e){this.space=e}}function wC(r){if(this.domElement.ownerDocument.pointerLockElement)return{x:0,y:0,button:r.button};{const e=this.domElement.getBoundingClientRect();return{x:(r.clientX-e.left)/e.width*2-1,y:-(r.clientY-e.top)/e.height*2+1,button:r.button}}}function PC(r){if(this.enabled)switch(r.pointerType){case"mouse":case"pen":this.pointerHover(this._getPointer(r));break}}function RC(r){this.enabled&&(document.pointerLockElement||this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.pointerHover(this._getPointer(r)),this.pointerDown(this._getPointer(r)))}function CC(r){this.enabled&&this.pointerMove(this._getPointer(r))}function IC(r){this.enabled&&(this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.pointerUp(this._getPointer(r)))}function rh(r,e,t){const n=e.intersectObject(r,!0);for(let i=0;i<n.length;i++)if(n[i].object.visible||t)return n[i];return!1}const vc=new pi,Ut=new F(0,1,0),Jm=new F(0,0,0),Qm=new nt,yc=new Wt,Cc=new Wt,_i=new F,eg=new nt,Xo=new F(1,0,0),$r=new F(0,1,0),qo=new F(0,0,1),xc=new F,zo=new F,Ho=new F;class LC extends Ht{constructor(e){super(),this.isTransformControlsRoot=!0,this.controls=e,this.visible=!1}updateMatrixWorld(e){const t=this.controls;t.object!==void 0&&(t.object.updateMatrixWorld(),t.object.parent===null?console.error("TransformControls: The attached 3D object must be a part of the scene graph."):t.object.parent.matrixWorld.decompose(t._parentPosition,t._parentQuaternion,t._parentScale),t.object.matrixWorld.decompose(t.worldPosition,t.worldQuaternion,t._worldScale),t._parentQuaternionInv.copy(t._parentQuaternion).invert(),t._worldQuaternionInv.copy(t.worldQuaternion).invert()),t.camera.updateMatrixWorld(),t.camera.matrixWorld.decompose(t.cameraPosition,t.cameraQuaternion,t._cameraScale),t.camera.isOrthographicCamera?t.camera.getWorldDirection(t.eye).negate():t.eye.copy(t.cameraPosition).sub(t.worldPosition).normalize(),super.updateMatrixWorld(e)}dispose(){this.traverse(function(e){e.geometry&&e.geometry.dispose(),e.material&&e.material.dispose()})}}class DC extends Ht{constructor(){super(),this.isTransformControlsGizmo=!0,this.type="TransformControlsGizmo";const e=new ii({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),t=new Hc({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),n=e.clone();n.opacity=.15;const i=t.clone();i.opacity=.5;const s=e.clone();s.color.setHex(16711680);const a=e.clone();a.color.setHex(65280);const c=e.clone();c.color.setHex(255);const u=e.clone();u.color.setHex(16711680),u.opacity=.5;const h=e.clone();h.color.setHex(65280),h.opacity=.5;const f=e.clone();f.color.setHex(255),f.opacity=.5;const p=e.clone();p.opacity=.25;const m=e.clone();m.color.setHex(16776960),m.opacity=.25,e.clone().color.setHex(16776960);const x=e.clone();x.color.setHex(7895160);const M=new _n(0,.04,.1,12);M.translate(0,.05,0);const v=new Yt(.08,.08,.08);v.translate(0,.04,0);const _=new sn;_.setAttribute("position",new jt([0,0,0,1,0,0],3));const A=new _n(.0075,.0075,.5,3);A.translate(0,.25,0);function P(ce,$){const le=new es(ce,.0075,3,64,$*Math.PI*2);return le.rotateY(Math.PI/2),le.rotateX(Math.PI/2),le}function S(){const ce=new sn;return ce.setAttribute("position",new jt([0,0,0,1,1,1],3)),ce}const k={X:[[new we(M,s),[.5,0,0],[0,0,-Math.PI/2]],[new we(M,s),[-.5,0,0],[0,0,Math.PI/2]],[new we(A,s),[0,0,0],[0,0,-Math.PI/2]]],Y:[[new we(M,a),[0,.5,0]],[new we(M,a),[0,-.5,0],[Math.PI,0,0]],[new we(A,a)]],Z:[[new we(M,c),[0,0,.5],[Math.PI/2,0,0]],[new we(M,c),[0,0,-.5],[-Math.PI/2,0,0]],[new we(A,c),null,[Math.PI/2,0,0]]],XYZ:[[new we(new Ws(.1,0),p.clone()),[0,0,0]]],XY:[[new we(new Yt(.15,.15,.01),f.clone()),[.15,.15,0]]],YZ:[[new we(new Yt(.15,.15,.01),u.clone()),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new we(new Yt(.15,.15,.01),h.clone()),[.15,0,.15],[-Math.PI/2,0,0]]]},O={X:[[new we(new _n(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new we(new _n(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new we(new _n(.2,0,.6,4),n),[0,.3,0]],[new we(new _n(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new we(new _n(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new we(new _n(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XYZ:[[new we(new Ws(.2,0),n)]],XY:[[new we(new Yt(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new we(new Yt(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new we(new Yt(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]]},U={START:[[new we(new Ws(.01,2),i),null,null,null,"helper"]],END:[[new we(new Ws(.01,2),i),null,null,null,"helper"]],DELTA:[[new li(S(),i),null,null,null,"helper"]],X:[[new li(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new li(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new li(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]},z={XYZE:[[new we(P(.5,1),x),null,[0,Math.PI/2,0]]],X:[[new we(P(.5,.5),s)]],Y:[[new we(P(.5,.5),a),null,[0,0,-Math.PI/2]]],Z:[[new we(P(.5,.5),c),null,[0,Math.PI/2,0]]],E:[[new we(P(.75,1),m),null,[0,Math.PI/2,0]]]},I={AXIS:[[new li(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]]},w={XYZE:[[new we(new ia(.25,10,8),n)]],X:[[new we(new es(.5,.1,4,24),n),[0,0,0],[0,-Math.PI/2,-Math.PI/2]]],Y:[[new we(new es(.5,.1,4,24),n),[0,0,0],[Math.PI/2,0,0]]],Z:[[new we(new es(.5,.1,4,24),n),[0,0,0],[0,0,-Math.PI/2]]],E:[[new we(new es(.75,.1,2,24),n)]]},H={X:[[new we(v,s),[.5,0,0],[0,0,-Math.PI/2]],[new we(A,s),[0,0,0],[0,0,-Math.PI/2]],[new we(v,s),[-.5,0,0],[0,0,Math.PI/2]]],Y:[[new we(v,a),[0,.5,0]],[new we(A,a)],[new we(v,a),[0,-.5,0],[0,0,Math.PI]]],Z:[[new we(v,c),[0,0,.5],[Math.PI/2,0,0]],[new we(A,c),[0,0,0],[Math.PI/2,0,0]],[new we(v,c),[0,0,-.5],[-Math.PI/2,0,0]]],XY:[[new we(new Yt(.15,.15,.01),f),[.15,.15,0]]],YZ:[[new we(new Yt(.15,.15,.01),u),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new we(new Yt(.15,.15,.01),h),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new we(new Yt(.1,.1,.1),p.clone())]]},ee={X:[[new we(new _n(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new we(new _n(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new we(new _n(.2,0,.6,4),n),[0,.3,0]],[new we(new _n(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new we(new _n(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new we(new _n(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XY:[[new we(new Yt(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new we(new Yt(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new we(new Yt(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new we(new Yt(.2,.2,.2),n),[0,0,0]]]},J={X:[[new li(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new li(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new li(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]};function oe(ce){const $=new Ht;for(const le in ce)for(let ne=ce[le].length;ne--;){const ge=ce[le][ne][0].clone(),Te=ce[le][ne][1],Oe=ce[le][ne][2],Ye=ce[le][ne][3],yt=ce[le][ne][4];ge.name=le,ge.tag=yt,Te&&ge.position.set(Te[0],Te[1],Te[2]),Oe&&ge.rotation.set(Oe[0],Oe[1],Oe[2]),Ye&&ge.scale.set(Ye[0],Ye[1],Ye[2]),ge.updateMatrix();const he=ge.geometry.clone();he.applyMatrix4(ge.matrix),ge.geometry=he,ge.renderOrder=1/0,ge.position.set(0,0,0),ge.rotation.set(0,0,0),ge.scale.set(1,1,1),$.add(ge)}return $}this.gizmo={},this.picker={},this.helper={},this.add(this.gizmo.translate=oe(k)),this.add(this.gizmo.rotate=oe(z)),this.add(this.gizmo.scale=oe(H)),this.add(this.picker.translate=oe(O)),this.add(this.picker.rotate=oe(w)),this.add(this.picker.scale=oe(ee)),this.add(this.helper.translate=oe(U)),this.add(this.helper.rotate=oe(I)),this.add(this.helper.scale=oe(J)),this.picker.translate.visible=!1,this.picker.rotate.visible=!1,this.picker.scale.visible=!1}updateMatrixWorld(e){const n=(this.mode==="scale"?"local":this.space)==="local"?this.worldQuaternion:Cc;this.gizmo.translate.visible=this.mode==="translate",this.gizmo.rotate.visible=this.mode==="rotate",this.gizmo.scale.visible=this.mode==="scale",this.helper.translate.visible=this.mode==="translate",this.helper.rotate.visible=this.mode==="rotate",this.helper.scale.visible=this.mode==="scale";let i=[];i=i.concat(this.picker[this.mode].children),i=i.concat(this.gizmo[this.mode].children),i=i.concat(this.helper[this.mode].children);for(let s=0;s<i.length;s++){const a=i[s];a.visible=!0,a.rotation.set(0,0,0),a.position.copy(this.worldPosition);let c;if(this.camera.isOrthographicCamera?c=(this.camera.top-this.camera.bottom)/this.camera.zoom:c=this.worldPosition.distanceTo(this.cameraPosition)*Math.min(1.9*Math.tan(Math.PI*this.camera.fov/360)/this.camera.zoom,7),a.scale.set(1,1,1).multiplyScalar(c*this.size/4),a.tag==="helper"){a.visible=!1,a.name==="AXIS"?(a.visible=!!this.axis,this.axis==="X"&&(Xt.setFromEuler(vc.set(0,0,0)),a.quaternion.copy(n).multiply(Xt),Math.abs(Ut.copy(Xo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Y"&&(Xt.setFromEuler(vc.set(0,0,Math.PI/2)),a.quaternion.copy(n).multiply(Xt),Math.abs(Ut.copy($r).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Z"&&(Xt.setFromEuler(vc.set(0,Math.PI/2,0)),a.quaternion.copy(n).multiply(Xt),Math.abs(Ut.copy(qo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="XYZE"&&(Xt.setFromEuler(vc.set(0,Math.PI/2,0)),Ut.copy(this.rotationAxis),a.quaternion.setFromRotationMatrix(Qm.lookAt(Jm,Ut,$r)),a.quaternion.multiply(Xt),a.visible=this.dragging),this.axis==="E"&&(a.visible=!1)):a.name==="START"?(a.position.copy(this.worldPositionStart),a.visible=this.dragging):a.name==="END"?(a.position.copy(this.worldPosition),a.visible=this.dragging):a.name==="DELTA"?(a.position.copy(this.worldPositionStart),a.quaternion.copy(this.worldQuaternionStart),En.set(1e-10,1e-10,1e-10).add(this.worldPositionStart).sub(this.worldPosition).multiplyScalar(-1),En.applyQuaternion(this.worldQuaternionStart.clone().invert()),a.scale.copy(En),a.visible=this.dragging):(a.quaternion.copy(n),this.dragging?a.position.copy(this.worldPositionStart):a.position.copy(this.worldPosition),this.axis&&(a.visible=this.axis.search(a.name)!==-1));continue}a.quaternion.copy(n),this.mode==="translate"||this.mode==="scale"?(a.name==="X"&&Math.abs(Ut.copy(Xo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Y"&&Math.abs(Ut.copy($r).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Z"&&Math.abs(Ut.copy(qo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XY"&&Math.abs(Ut.copy(qo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="YZ"&&Math.abs(Ut.copy(Xo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XZ"&&Math.abs(Ut.copy($r).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1)):this.mode==="rotate"&&(yc.copy(n),Ut.copy(this.eye).applyQuaternion(Xt.copy(n).invert()),a.name.search("E")!==-1&&a.quaternion.setFromRotationMatrix(Qm.lookAt(this.eye,Jm,$r)),a.name==="X"&&(Xt.setFromAxisAngle(Xo,Math.atan2(-Ut.y,Ut.z)),Xt.multiplyQuaternions(yc,Xt),a.quaternion.copy(Xt)),a.name==="Y"&&(Xt.setFromAxisAngle($r,Math.atan2(Ut.x,Ut.z)),Xt.multiplyQuaternions(yc,Xt),a.quaternion.copy(Xt)),a.name==="Z"&&(Xt.setFromAxisAngle(qo,Math.atan2(Ut.y,Ut.x)),Xt.multiplyQuaternions(yc,Xt),a.quaternion.copy(Xt))),a.visible=a.visible&&(a.name.indexOf("X")===-1||this.showX),a.visible=a.visible&&(a.name.indexOf("Y")===-1||this.showY),a.visible=a.visible&&(a.name.indexOf("Z")===-1||this.showZ),a.visible=a.visible&&(a.name.indexOf("E")===-1||this.showX&&this.showY&&this.showZ),a.material._color=a.material._color||a.material.color.clone(),a.material._opacity=a.material._opacity||a.material.opacity,a.material.color.copy(a.material._color),a.material.opacity=a.material._opacity,this.enabled&&this.axis&&(a.name===this.axis||this.axis.split("").some(function(u){return a.name===u}))&&(a.material.color.setHex(16776960),a.material.opacity=1)}super.updateMatrixWorld(e)}}class NC extends we{constructor(){super(new ao(1e5,1e5,2,2),new ii({visible:!1,wireframe:!0,side:Fn,transparent:!0,opacity:.1,toneMapped:!1})),this.isTransformControlsPlane=!0,this.type="TransformControlsPlane"}updateMatrixWorld(e){let t=this.space;switch(this.position.copy(this.worldPosition),this.mode==="scale"&&(t="local"),xc.copy(Xo).applyQuaternion(t==="local"?this.worldQuaternion:Cc),zo.copy($r).applyQuaternion(t==="local"?this.worldQuaternion:Cc),Ho.copy(qo).applyQuaternion(t==="local"?this.worldQuaternion:Cc),Ut.copy(zo),this.mode){case"translate":case"scale":switch(this.axis){case"X":Ut.copy(this.eye).cross(xc),_i.copy(xc).cross(Ut);break;case"Y":Ut.copy(this.eye).cross(zo),_i.copy(zo).cross(Ut);break;case"Z":Ut.copy(this.eye).cross(Ho),_i.copy(Ho).cross(Ut);break;case"XY":_i.copy(Ho);break;case"YZ":_i.copy(xc);break;case"XZ":Ut.copy(Ho),_i.copy(zo);break;case"XYZ":case"E":_i.set(0,0,0);break}break;case"rotate":default:_i.set(0,0,0)}_i.length()===0?this.quaternion.copy(this.cameraQuaternion):(eg.lookAt(En.set(0,0,0),_i,Ut),this.quaternion.setFromRotationMatrix(eg)),super.updateMatrixWorld(e)}}function sh(r){const e=new Wi,t=new Md(.4,1,16),n=new ii({color:r,transparent:!0,opacity:1,side:Fn,depthTest:!1,depthWrite:!1}),i=new we(t,n);i.rotation.x=Math.PI,i.renderOrder=999;const s=new ia(.35,32,32),a=new ii({color:new Ke(1,1,1),emissive:r,emissiveIntensity:2,transparent:!0,opacity:1,depthTest:!1,depthWrite:!1}),c=new we(s,a);return c.position.y=.5,c.renderOrder=999,e.add(i),e.add(c),e}function OC(r){const e=new MR({canvas:r,antialias:!0});e.setPixelRatio(window.devicePixelRatio),e.setSize(r.clientWidth,r.clientHeight),e.shadowMap.enabled=!0,e.shadowMap.type=lg,e.toneMapping=hg,e.toneMappingExposure=1.6,e.outputColorSpace=dn;const t=new TR;t.background=new Ke(1381664),t.fog=new xd(1381664,.03);const n=new Cn(50,r.clientWidth/r.clientHeight,.1,1e3);n.position.set(0,1.6,5);const i=new fC(n,r);i.target.set(0,.9,0),i.enableDamping=!0,i.dampingFactor=.08,i.update();const s=new ao(14,10),a=new is({color:4864558,roughness:.35,metalness:.05}),c=new we(s,a);c.rotation.x=-Math.PI/2,c.position.y=-.01,c.receiveShadow=!0,t.add(c);const u=new Yt(14.2,.06,10.2),h=new is({color:3811866,roughness:.6}),f=new we(u,h);f.position.y=-.04,f.receiveShadow=!0,t.add(f);const p=new KR(2763326,.5);t.add(p);const m=new Rc(16772829,60);m.position.set(-3,3,3),m.target.position.set(0,0,0),m.angle=Math.PI/6,m.penumbra=.5,m.decay=1.5,m.castShadow=!0,m.shadow.mapSize.set(4096,4096),m.shadow.camera.near=1,m.shadow.camera.far=15,m.shadow.bias=-1e-4,t.add(m),t.add(m.target);const g=sh(new Ke(16772829));g.position.copy(m.position),g.lookAt(m.target.position),g.userData.light=m,t.add(g);const x=new Rc(16772829,60);x.position.set(3,3,3),x.target.position.set(0,0,0),x.angle=Math.PI/6,x.penumbra=.5,x.decay=1.5,x.castShadow=!0,x.shadow.mapSize.set(4096,4096),x.shadow.camera.near=1,x.shadow.camera.far=15,x.shadow.bias=-1e-4,t.add(x),t.add(x.target);const M=sh(new Ke(16772829));M.position.copy(x.position),M.lookAt(x.target.position),M.userData.light=x,t.add(M);const v=new Rc(6702250,25);v.position.set(0,2.5,-4),v.target.position.set(0,.5,0),v.angle=Math.PI/5,v.penumbra=.7,v.decay=1.5,v.castShadow=!1,t.add(v),t.add(v.target);const _=sh(new Ke(6702250));_.position.copy(v.position),_.lookAt(v.target.position),_.userData.light=v,t.add(_);const A={ambient:p,spotLeft:m,spotRight:x,backLight:v},P={spotLeftIcon:g,spotRightIcon:M,backLightIcon:_},S=new AC(n,r);S.setMode("translate"),S.setSize(.8),t.add(S),S.addEventListener("dragging-changed",O=>{i.enabled=!O.value});function k(){const O=r.clientWidth,U=r.clientHeight;e.setSize(O,U),n.aspect=O/U,n.updateProjectionMatrix()}return window.addEventListener("resize",k),{scene:t,camera:n,renderer:e,controls:i,lights:A,lightIcons:P,transformControls:S}}var Yo={exports:{}};Yo.exports;var tg;function UC(){return tg||(tg=1,(function(r,e){var t=Object.create,n=Object.defineProperty,i=Object.defineProperties,s=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyDescriptors,c=Object.getOwnPropertyNames,u=Object.getOwnPropertySymbols,h=Object.getPrototypeOf,f=Object.prototype.hasOwnProperty,p=Object.prototype.propertyIsEnumerable,m=(o,l,d)=>l in o?n(o,l,{enumerable:!0,configurable:!0,writable:!0,value:d}):o[l]=d,g=(o,l)=>{for(var d in l||(l={}))f.call(l,d)&&m(o,d,l[d]);if(u)for(var d of u(l))p.call(l,d)&&m(o,d,l[d]);return o},x=(o,l)=>i(o,a(l)),M=(o,l)=>function(){return l||(0,o[c(o)[0]])((l={exports:{}}).exports,l),l.exports},v=(o,l)=>{for(var d in l)n(o,d,{get:l[d],enumerable:!0})},_=(o,l,d,y)=>{if(l&&typeof l=="object"||typeof l=="function")for(let T of c(l))!f.call(o,T)&&T!==d&&n(o,T,{get:()=>l[T],enumerable:!(y=s(l,T))||y.enumerable});return o},A=(o,l,d)=>(d=o!=null?t(h(o)):{},_(!o||!o.__esModule?n(d,"default",{value:o,enumerable:!0}):d,o)),P=o=>_(n({},"__esModule",{value:!0}),o),S=(o,l,d)=>(m(o,typeof l!="symbol"?l+"":l,d),d),k=M({"../node_modules/timing-function/lib/UnitBezier.js"(o,l){l.exports=(function(){function d(y,T,C,B){this.set(y,T,C,B)}return d.prototype.set=function(y,T,C,B){this._cx=3*y,this._bx=3*(C-y)-this._cx,this._ax=1-this._cx-this._bx,this._cy=3*T,this._by=3*(B-T)-this._cy,this._ay=1-this._cy-this._by},d.epsilon=1e-6,d.prototype._sampleCurveX=function(y){return((this._ax*y+this._bx)*y+this._cx)*y},d.prototype._sampleCurveY=function(y){return((this._ay*y+this._by)*y+this._cy)*y},d.prototype._sampleCurveDerivativeX=function(y){return(3*this._ax*y+2*this._bx)*y+this._cx},d.prototype._solveCurveX=function(y,T){var C,B,q,K,se,ve;for(q=void 0,K=void 0,se=void 0,ve=void 0,C=void 0,B=void 0,se=y,B=0;B<8;){if(ve=this._sampleCurveX(se)-y,Math.abs(ve)<T)return se;if(C=this._sampleCurveDerivativeX(se),Math.abs(C)<T)break;se=se-ve/C,B++}if(q=0,K=1,se=y,se<q)return q;if(se>K)return K;for(;q<K;){if(ve=this._sampleCurveX(se),Math.abs(ve-y)<T)return se;y>ve?q=se:K=se,se=(K-q)*.5+q}return se},d.prototype.solve=function(y,T){return this._sampleCurveY(this._solveCurveX(y,T))},d.prototype.solveSimple=function(y){return this._sampleCurveY(this._solveCurveX(y,1e-6))},d})()}}),O=M({"../node_modules/levenshtein-edit-distance/index.js"(o,l){var d,y;d=[],y=[];function T(C,B,q){var K,se,ve,ye,Ce,je,Be,at;if(C===B)return 0;if(K=C.length,se=B.length,K===0)return se;if(se===0)return K;for(q&&(C=C.toLowerCase(),B=B.toLowerCase()),Be=0;Be<K;)y[Be]=C.charCodeAt(Be),d[Be]=++Be;for(at=0;at<se;)for(ve=B.charCodeAt(at),ye=Ce=at++,Be=-1;++Be<K;)je=ve===y[Be]?Ce:Ce+1,Ce=d[Be],d[Be]=ye=Ce>ye?je>ye?ye+1:je:je>Ce?Ce+1:je;return ye}l.exports=T}}),U=M({"../node_modules/propose/propose.js"(o,l){var d=O();function y(){var T,C,B,q,K,se=0,ve=arguments[0],ye=arguments[1],Ce=ye.length,je=arguments[2];je&&(q=je.threshold,K=je.ignoreCase),q===void 0&&(q=0);for(var Be=0;Be<Ce;++Be)K?C=d(ve,ye[Be],!0):C=d(ve,ye[Be]),C>ve.length?T=1-C/ye[Be].length:T=1-C/ve.length,T>se&&(se=T,B=ye[Be]);return se>=q?B:null}l.exports=y}}),z=M({"../node_modules/fast-deep-equal/index.js"(o,l){l.exports=function d(y,T){if(y===T)return!0;if(y&&T&&typeof y=="object"&&typeof T=="object"){if(y.constructor!==T.constructor)return!1;var C,B,q;if(Array.isArray(y)){if(C=y.length,C!=T.length)return!1;for(B=C;B--!==0;)if(!d(y[B],T[B]))return!1;return!0}if(y.constructor===RegExp)return y.source===T.source&&y.flags===T.flags;if(y.valueOf!==Object.prototype.valueOf)return y.valueOf()===T.valueOf();if(y.toString!==Object.prototype.toString)return y.toString()===T.toString();if(q=Object.keys(y),C=q.length,C!==Object.keys(T).length)return!1;for(B=C;B--!==0;)if(!Object.prototype.hasOwnProperty.call(T,q[B]))return!1;for(B=C;B--!==0;){var K=q[B];if(!d(y[K],T[K]))return!1}return!0}return y!==y&&T!==T}}}),I={};v(I,{createRafDriver:()=>Jl,getProject:()=>Sp,notify:()=>Ss,onChange:()=>xu,types:()=>Ql,val:()=>Mp}),r.exports=P(I);var w={};v(w,{createRafDriver:()=>Jl,getProject:()=>Sp,notify:()=>Ss,onChange:()=>xu,types:()=>Ql,val:()=>Mp});var H=nn(),ee=class{constructor(){S(this,"atom",new H.Atom({projects:{}}))}add(o,l){this.atom.setByPointer(d=>d.projects[o],l)}get(o){return this.atom.get().projects[o]}has(o){return!!this.get(o)}},J=new ee,oe=J,ce=new WeakMap;function $(o){return ce.get(o)}function le(o,l){ce.set(o,l)}var ne=[],ge=Array.isArray,Te=ge,Oe=typeof yi=="object"&&yi&&yi.Object===Object&&yi,Ye=Oe,yt=typeof self=="object"&&self&&self.Object===Object&&self,he=Ye||yt||Function("return this")(),me=he,Ne=me.Symbol,Me=Ne,Xe=Object.prototype,Ze=Xe.hasOwnProperty,tt=Xe.toString,St=Me?Me.toStringTag:void 0;function rt(o){var l=Ze.call(o,St),d=o[St];try{o[St]=void 0;var y=!0}catch{}var T=tt.call(o);return y&&(l?o[St]=d:delete o[St]),T}var At=rt,W=Object.prototype,cn=W.toString;function ht(o){return cn.call(o)}var ct=ht,Fe="[object Null]",st="[object Undefined]",ke=Me?Me.toStringTag:void 0;function D(o){return o==null?o===void 0?st:Fe:ke&&ke in Object(o)?At(o):ct(o)}var E=D;function Z(o){return o!=null&&typeof o=="object"}var ue=Z,pe="[object Symbol]";function fe(o){return typeof o=="symbol"||ue(o)&&E(o)==pe}var Ue=fe,Pe=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,De=/^\w*$/;function dt(o,l){if(Te(o))return!1;var d=typeof o;return d=="number"||d=="symbol"||d=="boolean"||o==null||Ue(o)?!0:De.test(o)||!Pe.test(o)||l!=null&&o in Object(l)}var N=dt;function Y(o){var l=typeof o;return o!=null&&(l=="object"||l=="function")}var ae=Y,_e="[object AsyncFunction]",xe="[object Function]",Re="[object GeneratorFunction]",qe="[object Proxy]";function lt(o){if(!ae(o))return!1;var l=E(o);return l==xe||l==Re||l==_e||l==qe}var G=lt,be=me["__core-js_shared__"],ie=be,de=(function(){var o=/[^.]+$/.exec(ie&&ie.keys&&ie.keys.IE_PROTO||"");return o?"Symbol(src)_1."+o:""})();function Ae(o){return!!de&&de in o}var Ee=Ae,Ge=Function.prototype,ot=Ge.toString;function Vt(o){if(o!=null){try{return ot.call(o)}catch{}try{return o+""}catch{}}return""}var pt=Vt,An=/[\\^$.*+?()[\]{}|]/g,kn=/^\[object .+?Constructor\]$/,as=Function.prototype,cs=Object.prototype,ri=as.toString,yr=cs.hasOwnProperty,ls=RegExp("^"+ri.call(yr).replace(An,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function us(o){if(!ae(o)||Ee(o))return!1;var l=G(o)?ls:kn;return l.test(pt(o))}var zn=us;function xr(o,l){return o==null?void 0:o[l]}var Ki=xr;function hs(o,l){var d=Ki(o,l);return zn(d)?d:void 0}var $n=hs,ho=$n(Object,"create"),Ti=ho;function Zi(){this.__data__=Ti?Ti(null):{},this.size=0}var R=Zi;function j(o){var l=this.has(o)&&delete this.__data__[o];return this.size-=l?1:0,l}var Q=j,te="__lodash_hash_undefined__",X=Object.prototype,Se=X.hasOwnProperty;function Le(o){var l=this.__data__;if(Ti){var d=l[o];return d===te?void 0:d}return Se.call(l,o)?l[o]:void 0}var ze=Le,He=Object.prototype,et=He.hasOwnProperty;function $e(o){var l=this.__data__;return Ti?l[o]!==void 0:et.call(l,o)}var Ve=$e,vt="__lodash_hash_undefined__";function wt(o,l){var d=this.__data__;return this.size+=this.has(o)?0:1,d[o]=Ti&&l===void 0?vt:l,this}var Rt=wt;function qt(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}qt.prototype.clear=R,qt.prototype.delete=Q,qt.prototype.get=ze,qt.prototype.has=Ve,qt.prototype.set=Rt;var xt=qt;function We(){this.__data__=[],this.size=0}var Hn=We;function gt(o,l){return o===l||o!==o&&l!==l}var pn=gt;function mi(o,l){for(var d=o.length;d--;)if(pn(o[d][0],l))return d;return-1}var Zt=mi,Ei=Array.prototype,Ct=Ei.splice;function Dn(o){var l=this.__data__,d=Zt(l,o);if(d<0)return!1;var y=l.length-1;return d==y?l.pop():Ct.call(l,d,1),--this.size,!0}var Ai=Dn;function yn(o){var l=this.__data__,d=Zt(l,o);return d<0?void 0:l[d][1]}var mn=yn;function Vn(o){return Zt(this.__data__,o)>-1}var ds=Vn;function fo(o,l){var d=this.__data__,y=Zt(d,o);return y<0?(++this.size,d.push([o,l])):d[y][1]=l,this}var Gc=fo;function $i(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}$i.prototype.clear=Hn,$i.prototype.delete=Ai,$i.prototype.get=mn,$i.prototype.has=ds,$i.prototype.set=Gc;var fs=$i,Wc=$n(me,"Map"),br=Wc;function jc(){this.size=0,this.__data__={hash:new xt,map:new(br||fs),string:new xt}}var Xc=jc;function qc(o){var l=typeof o;return l=="string"||l=="number"||l=="symbol"||l=="boolean"?o!=="__proto__":o===null}var Yc=qc;function Kc(o,l){var d=o.__data__;return Yc(l)?d[typeof l=="string"?"string":"hash"]:d.map}var Sr=Kc;function sa(o){var l=Sr(this,o).delete(o);return this.size-=l?1:0,l}var oa=sa;function Zc(o){return Sr(this,o).get(o)}var $c=Zc;function Jc(o){return Sr(this,o).has(o)}var Qc=Jc;function el(o,l){var d=Sr(this,o),y=d.size;return d.set(o,l),this.size+=d.size==y?0:1,this}var tl=el;function Ji(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}Ji.prototype.clear=Xc,Ji.prototype.delete=oa,Ji.prototype.get=$c,Ji.prototype.has=Qc,Ji.prototype.set=tl;var ps=Ji,nl="Expected a function";function po(o,l){if(typeof o!="function"||l!=null&&typeof l!="function")throw new TypeError(nl);var d=function(){var y=arguments,T=l?l.apply(this,y):y[0],C=d.cache;if(C.has(T))return C.get(T);var B=o.apply(this,y);return d.cache=C.set(T,B)||C,B};return d.cache=new(po.Cache||ps),d}po.Cache=ps;var il=po,rl=500;function sl(o){var l=il(o,function(y){return d.size===rl&&d.clear(),y}),d=l.cache;return l}var ol=sl,al=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,cl=/\\(\\)?/g,ll=ol(function(o){var l=[];return o.charCodeAt(0)===46&&l.push(""),o.replace(al,function(d,y,T,C){l.push(T?C.replace(cl,"$1"):y||d)}),l}),ul=ll;function aa(o,l){for(var d=-1,y=o==null?0:o.length,T=Array(y);++d<y;)T[d]=l(o[d],d,o);return T}var hl=aa,ca=Me?Me.prototype:void 0,la=ca?ca.toString:void 0;function ua(o){if(typeof o=="string")return o;if(Te(o))return hl(o,ua)+"";if(Ue(o))return la?la.call(o):"";var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var ha=ua;function dl(o){return o==null?"":ha(o)}var ms=dl;function da(o,l){return Te(o)?o:N(o,l)?[o]:ul(ms(o))}var Mr=da;function fl(o){if(typeof o=="string"||Ue(o))return o;var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var si=fl;function Tr(o,l){l=Mr(l,o);for(var d=0,y=l.length;o!=null&&d<y;)o=o[si(l[d++])];return d&&d==y?o:void 0}var gs=Tr;function mo(o,l,d){var y=o==null?void 0:gs(o,l);return y===void 0?d:y}var wi=mo;function fa(o,l){return l.length===0?o:wi(o,l)}var Qi=class{constructor(){S(this,"_values",{})}get(o,l){if(this.has(o))return this._values[o];{const d=l();return this._values[o]=d,d}}has(o){return this._values.hasOwnProperty(o)}},en=nn(),_s=(function(){try{var o=$n(Object,"defineProperty");return o({},"",{}),o}catch{}})(),go=_s;function pl(o,l,d){l=="__proto__"&&go?go(o,l,{configurable:!0,enumerable:!0,value:d,writable:!0}):o[l]=d}var Pi=pl,Er=Object.prototype,ml=Er.hasOwnProperty;function gl(o,l,d){var y=o[l];(!(ml.call(o,l)&&pn(y,d))||d===void 0&&!(l in o))&&Pi(o,l,d)}var _o=gl,_l=9007199254740991,pa=/^(?:0|[1-9]\d*)$/;function vl(o,l){var d=typeof o;return l=l??_l,!!l&&(d=="number"||d!="symbol"&&pa.test(o))&&o>-1&&o%1==0&&o<l}var vo=vl;function yl(o,l,d,y){if(!ae(o))return o;l=Mr(l,o);for(var T=-1,C=l.length,B=C-1,q=o;q!=null&&++T<C;){var K=si(l[T]),se=d;if(K==="__proto__"||K==="constructor"||K==="prototype")return o;if(T!=B){var ve=q[K];se=y?y(ve,K,q):void 0,se===void 0&&(se=ae(ve)?ve:vo(l[T+1])?[]:{})}_o(q,K,se),q=q[K]}return o}var ma=yl;function ga(o,l,d){return o==null?o:ma(o,l,d)}var vs=ga,ln=new WeakMap;function xl(o){return yo(o)}function yo(o){if(ln.has(o))return ln.get(o);const l=o.type==="compound"?va(o):o.type==="enum"?_a(o):o.default;return ln.set(o,l),l}function _a(o){const l={$case:o.defaultCase};for(const[d,y]of Object.entries(o.cases))l[d]=yo(y);return l}function va(o){const l={};for(const[d,y]of Object.entries(o.props))l[d]=yo(y);return l}var wn=nn(),bl=A(k());function Sl(o,l,d){return(0,wn.prism)(()=>{const y=(0,wn.val)(l);return wn.prism.memo("driver",()=>y?y.type==="BasicKeyframedTrack"?Ml(o,y,d):(o.logger.error("Track type not yet supported."),(0,wn.prism)(()=>{})):(0,wn.prism)(()=>{}),[y]).getValue()})}function Ml(o,l,d){return(0,wn.prism)(()=>{let y=wn.prism.ref("state",{started:!1}),T=y.current;const C=d.getValue();return(!T.started||C<T.validFrom||T.validTo<=C)&&(y.current=T=Tl(o,d,l)),T.der.getValue()})}var ya=(0,wn.prism)(()=>{});function Tl(o,l,d){const y=l.getValue();if(d.keyframes.length===0)return{started:!0,validFrom:-1/0,validTo:1/0,der:ya};let T=0;for(;;){const C=d.keyframes[T];if(!C)return tn.error;const B=T===d.keyframes.length-1;if(y<C.position)return T===0?tn.beforeFirstKeyframe(C):tn.error;if(C.position===y)return B?tn.lastKeyframe(C):tn.between(C,d.keyframes[T+1],l);if(T===d.keyframes.length-1)return tn.lastKeyframe(C);{const q=T+1;if(d.keyframes[q].position<=y){T=q;continue}else return tn.between(C,d.keyframes[T+1],l)}}}var tn={beforeFirstKeyframe(o){return{started:!0,validFrom:-1/0,validTo:o.position,der:(0,wn.prism)(()=>({left:o.value,progression:0}))}},lastKeyframe(o){return{started:!0,validFrom:o.position,validTo:1/0,der:(0,wn.prism)(()=>({left:o.value,progression:0}))}},between(o,l,d){if(!o.connectedRight)return{started:!0,validFrom:o.position,validTo:l.position,der:(0,wn.prism)(()=>({left:o.value,progression:0}))};const y=C=>(C-o.position)/(l.position-o.position);if(!o.type||o.type==="bezier"){const C=new bl.default(o.handles[2],o.handles[3],l.handles[0],l.handles[1]),B=(0,wn.prism)(()=>{const q=y(d.getValue()),K=C.solveSimple(q);return{left:o.value,right:l.value,progression:K}});return{started:!0,validFrom:o.position,validTo:l.position,der:B}}const T=(0,wn.prism)(()=>{const C=y(d.getValue()),B=Math.floor(C);return{left:o.value,right:l.value,progression:B}});return{started:!0,validFrom:o.position,validTo:l.position,der:T}},error:{started:!0,validFrom:-1/0,validTo:1/0,der:ya}};function Ar(o,l,d){const T=d.get(o);if(T&&T.override===l)return T.merged;const C=g({},o);for(const B of Object.keys(l)){const q=l[B],K=o[B];C[B]=typeof q=="object"&&typeof K=="object"?Ar(K,q,d):q===void 0?K:q}return d.set(o,{override:l,merged:C}),C}function wr(o,l){let d=o;for(const y of l)d=d[y];return d}var Pr=nn(),xa=(o,l)=>{const d=Pr.prism.memo(o,()=>new Pr.Atom(l),[]);return d.set(l),d},It=nn(),xo=nn(),El=/\s/;function ba(o){for(var l=o.length;l--&&El.test(o.charAt(l)););return l}var Sa=ba,Ma=/^\s+/;function Al(o){return o&&o.slice(0,Sa(o)+1).replace(Ma,"")}var ys=Al,bo=NaN,wl=/^[-+]0x[0-9a-f]+$/i,Pl=/^0b[01]+$/i,Ta=/^0o[0-7]+$/i,Rl=parseInt;function Cl(o){if(typeof o=="number")return o;if(Ue(o))return bo;if(ae(o)){var l=typeof o.valueOf=="function"?o.valueOf():o;o=ae(l)?l+"":l}if(typeof o!="string")return o===0?o:+o;o=ys(o);var d=Pl.test(o);return d||Ta.test(o)?Rl(o.slice(2),d?2:8):wl.test(o)?bo:+o}var b=Cl,L=1/0,V=17976931348623157e292;function re(o){if(!o)return o===0?o:0;if(o=b(o),o===L||o===-L){var l=o<0?-1:1;return l*V}return o===o?o:0}var Je=re;function Mt(o){var l=Je(o),d=l%1;return l===l?d?l-d:l:0}var gn=Mt;function Jn(o){return o}var Ea=Jn,er=$n(me,"WeakMap"),Rr=er,Ld=Object.create,o_=(function(){function o(){}return function(l){if(!ae(l))return{};if(Ld)return Ld(l);o.prototype=l;var d=new o;return o.prototype=void 0,d}})(),a_=o_;function c_(o,l){var d=-1,y=o.length;for(l||(l=Array(y));++d<y;)l[d]=o[d];return l}var l_=c_;function u_(o,l){for(var d=-1,y=o==null?0:o.length;++d<y&&l(o[d],d,o)!==!1;);return o}var h_=u_;function d_(o,l,d,y){var T=!d;d||(d={});for(var C=-1,B=l.length;++C<B;){var q=l[C],K=y?y(d[q],o[q],q,d,o):void 0;K===void 0&&(K=o[q]),T?Pi(d,q,K):_o(d,q,K)}return d}var Aa=d_,f_=9007199254740991;function p_(o){return typeof o=="number"&&o>-1&&o%1==0&&o<=f_}var Il=p_;function m_(o){return o!=null&&Il(o.length)&&!G(o)}var Dd=m_,g_=Object.prototype;function __(o){var l=o&&o.constructor,d=typeof l=="function"&&l.prototype||g_;return o===d}var Ll=__;function v_(o,l){for(var d=-1,y=Array(o);++d<o;)y[d]=l(d);return y}var y_=v_,x_="[object Arguments]";function b_(o){return ue(o)&&E(o)==x_}var Nd=b_,Od=Object.prototype,S_=Od.hasOwnProperty,M_=Od.propertyIsEnumerable,T_=Nd((function(){return arguments})())?Nd:function(o){return ue(o)&&S_.call(o,"callee")&&!M_.call(o,"callee")},Ud=T_;function E_(){return!1}var A_=E_,Fd=e&&!e.nodeType&&e,Bd=Fd&&!0&&r&&!r.nodeType&&r,w_=Bd&&Bd.exports===Fd,kd=w_?me.Buffer:void 0,P_=kd?kd.isBuffer:void 0,R_=P_||A_,wa=R_,C_="[object Arguments]",I_="[object Array]",L_="[object Boolean]",D_="[object Date]",N_="[object Error]",O_="[object Function]",U_="[object Map]",F_="[object Number]",B_="[object Object]",k_="[object RegExp]",z_="[object Set]",H_="[object String]",V_="[object WeakMap]",G_="[object ArrayBuffer]",W_="[object DataView]",j_="[object Float32Array]",X_="[object Float64Array]",q_="[object Int8Array]",Y_="[object Int16Array]",K_="[object Int32Array]",Z_="[object Uint8Array]",$_="[object Uint8ClampedArray]",J_="[object Uint16Array]",Q_="[object Uint32Array]",Gt={};Gt[j_]=Gt[X_]=Gt[q_]=Gt[Y_]=Gt[K_]=Gt[Z_]=Gt[$_]=Gt[J_]=Gt[Q_]=!0,Gt[C_]=Gt[I_]=Gt[G_]=Gt[L_]=Gt[W_]=Gt[D_]=Gt[N_]=Gt[O_]=Gt[U_]=Gt[F_]=Gt[B_]=Gt[k_]=Gt[z_]=Gt[H_]=Gt[V_]=!1;function ev(o){return ue(o)&&Il(o.length)&&!!Gt[E(o)]}var tv=ev;function nv(o){return function(l){return o(l)}}var Dl=nv,zd=e&&!e.nodeType&&e,So=zd&&!0&&r&&!r.nodeType&&r,iv=So&&So.exports===zd,Nl=iv&&Ye.process,rv=(function(){try{var o=So&&So.require&&So.require("util").types;return o||Nl&&Nl.binding&&Nl.binding("util")}catch{}})(),xs=rv,Hd=xs&&xs.isTypedArray,sv=Hd?Dl(Hd):tv,Vd=sv,ov=Object.prototype,av=ov.hasOwnProperty;function cv(o,l){var d=Te(o),y=!d&&Ud(o),T=!d&&!y&&wa(o),C=!d&&!y&&!T&&Vd(o),B=d||y||T||C,q=B?y_(o.length,String):[],K=q.length;for(var se in o)(l||av.call(o,se))&&!(B&&(se=="length"||T&&(se=="offset"||se=="parent")||C&&(se=="buffer"||se=="byteLength"||se=="byteOffset")||vo(se,K)))&&q.push(se);return q}var Gd=cv;function lv(o,l){return function(d){return o(l(d))}}var Wd=lv,uv=Wd(Object.keys,Object),hv=uv,dv=Object.prototype,fv=dv.hasOwnProperty;function pv(o){if(!Ll(o))return hv(o);var l=[];for(var d in Object(o))fv.call(o,d)&&d!="constructor"&&l.push(d);return l}var mv=pv;function gv(o){return Dd(o)?Gd(o):mv(o)}var Mo=gv;function _v(o){var l=[];if(o!=null)for(var d in Object(o))l.push(d);return l}var vv=_v,yv=Object.prototype,xv=yv.hasOwnProperty;function bv(o){if(!ae(o))return vv(o);var l=Ll(o),d=[];for(var y in o)y=="constructor"&&(l||!xv.call(o,y))||d.push(y);return d}var Sv=bv;function Mv(o){return Dd(o)?Gd(o,!0):Sv(o)}var Ol=Mv;function Tv(o,l){for(var d=-1,y=l.length,T=o.length;++d<y;)o[T+d]=l[d];return o}var jd=Tv,Ev=Wd(Object.getPrototypeOf,Object),Ul=Ev,Av="[object Object]",wv=Function.prototype,Pv=Object.prototype,Xd=wv.toString,Rv=Pv.hasOwnProperty,Cv=Xd.call(Object);function Iv(o){if(!ue(o)||E(o)!=Av)return!1;var l=Ul(o);if(l===null)return!0;var d=Rv.call(l,"constructor")&&l.constructor;return typeof d=="function"&&d instanceof d&&Xd.call(d)==Cv}var Lv=Iv;function Dv(o,l,d){var y=-1,T=o.length;l<0&&(l=-l>T?0:T+l),d=d>T?T:d,d<0&&(d+=T),T=l>d?0:d-l>>>0,l>>>=0;for(var C=Array(T);++y<T;)C[y]=o[y+l];return C}var qd=Dv;function Nv(o,l,d){var y=o.length;return d=d===void 0?y:d,!l&&d>=y?o:qd(o,l,d)}var Ov=Nv,Uv="\\ud800-\\udfff",Fv="\\u0300-\\u036f",Bv="\\ufe20-\\ufe2f",kv="\\u20d0-\\u20ff",zv=Fv+Bv+kv,Hv="\\ufe0e\\ufe0f",Vv="\\u200d",Gv=RegExp("["+Vv+Uv+zv+Hv+"]");function Wv(o){return Gv.test(o)}var Fl=Wv;function jv(o){return o.split("")}var Xv=jv,Yd="\\ud800-\\udfff",qv="\\u0300-\\u036f",Yv="\\ufe20-\\ufe2f",Kv="\\u20d0-\\u20ff",Zv=qv+Yv+Kv,$v="\\ufe0e\\ufe0f",Jv="["+Yd+"]",Bl="["+Zv+"]",kl="\\ud83c[\\udffb-\\udfff]",Qv="(?:"+Bl+"|"+kl+")",Kd="[^"+Yd+"]",Zd="(?:\\ud83c[\\udde6-\\uddff]){2}",$d="[\\ud800-\\udbff][\\udc00-\\udfff]",e0="\\u200d",Jd=Qv+"?",Qd="["+$v+"]?",t0="(?:"+e0+"(?:"+[Kd,Zd,$d].join("|")+")"+Qd+Jd+")*",n0=Qd+Jd+t0,i0="(?:"+[Kd+Bl+"?",Bl,Zd,$d,Jv].join("|")+")",r0=RegExp(kl+"(?="+kl+")|"+i0+n0,"g");function s0(o){return o.match(r0)||[]}var o0=s0;function a0(o){return Fl(o)?o0(o):Xv(o)}var c0=a0;function l0(o,l,d){return o===o&&(d!==void 0&&(o=o<=d?o:d),l!==void 0&&(o=o>=l?o:l)),o}var u0=l0;function h0(o,l,d){return d===void 0&&(d=l,l=void 0),d!==void 0&&(d=b(d),d=d===d?d:0),l!==void 0&&(l=b(l),l=l===l?l:0),u0(b(o),l,d)}var ef=h0;function d0(){this.__data__=new fs,this.size=0}var f0=d0;function p0(o){var l=this.__data__,d=l.delete(o);return this.size=l.size,d}var m0=p0;function g0(o){return this.__data__.get(o)}var _0=g0;function v0(o){return this.__data__.has(o)}var y0=v0,x0=200;function b0(o,l){var d=this.__data__;if(d instanceof fs){var y=d.__data__;if(!br||y.length<x0-1)return y.push([o,l]),this.size=++d.size,this;d=this.__data__=new ps(y)}return d.set(o,l),this.size=d.size,this}var S0=b0;function bs(o){var l=this.__data__=new fs(o);this.size=l.size}bs.prototype.clear=f0,bs.prototype.delete=m0,bs.prototype.get=_0,bs.prototype.has=y0,bs.prototype.set=S0;var To=bs;function M0(o,l){return o&&Aa(l,Mo(l),o)}var T0=M0;function E0(o,l){return o&&Aa(l,Ol(l),o)}var A0=E0,tf=e&&!e.nodeType&&e,nf=tf&&!0&&r&&!r.nodeType&&r,w0=nf&&nf.exports===tf,rf=w0?me.Buffer:void 0,sf=rf?rf.allocUnsafe:void 0;function P0(o,l){if(l)return o.slice();var d=o.length,y=sf?sf(d):new o.constructor(d);return o.copy(y),y}var R0=P0;function C0(o,l){for(var d=-1,y=o==null?0:o.length,T=0,C=[];++d<y;){var B=o[d];l(B,d,o)&&(C[T++]=B)}return C}var I0=C0;function L0(){return[]}var of=L0,D0=Object.prototype,N0=D0.propertyIsEnumerable,af=Object.getOwnPropertySymbols,O0=af?function(o){return o==null?[]:(o=Object(o),I0(af(o),function(l){return N0.call(o,l)}))}:of,zl=O0;function U0(o,l){return Aa(o,zl(o),l)}var F0=U0,B0=Object.getOwnPropertySymbols,k0=B0?function(o){for(var l=[];o;)jd(l,zl(o)),o=Ul(o);return l}:of,cf=k0;function z0(o,l){return Aa(o,cf(o),l)}var H0=z0;function V0(o,l,d){var y=l(o);return Te(o)?y:jd(y,d(o))}var lf=V0;function G0(o){return lf(o,Mo,zl)}var Hl=G0;function W0(o){return lf(o,Ol,cf)}var j0=W0,X0=$n(me,"DataView"),Vl=X0,q0=$n(me,"Promise"),Gl=q0,Y0=$n(me,"Set"),Wl=Y0,uf="[object Map]",K0="[object Object]",hf="[object Promise]",df="[object Set]",ff="[object WeakMap]",pf="[object DataView]",Z0=pt(Vl),$0=pt(br),J0=pt(Gl),Q0=pt(Wl),ey=pt(Rr),Cr=E;(Vl&&Cr(new Vl(new ArrayBuffer(1)))!=pf||br&&Cr(new br)!=uf||Gl&&Cr(Gl.resolve())!=hf||Wl&&Cr(new Wl)!=df||Rr&&Cr(new Rr)!=ff)&&(Cr=function(o){var l=E(o),d=l==K0?o.constructor:void 0,y=d?pt(d):"";if(y)switch(y){case Z0:return pf;case $0:return uf;case J0:return hf;case Q0:return df;case ey:return ff}return l});var Eo=Cr,ty=Object.prototype,ny=ty.hasOwnProperty;function iy(o){var l=o.length,d=new o.constructor(l);return l&&typeof o[0]=="string"&&ny.call(o,"index")&&(d.index=o.index,d.input=o.input),d}var ry=iy,sy=me.Uint8Array,Pa=sy;function oy(o){var l=new o.constructor(o.byteLength);return new Pa(l).set(new Pa(o)),l}var jl=oy;function ay(o,l){var d=l?jl(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.byteLength)}var cy=ay,ly=/\w*$/;function uy(o){var l=new o.constructor(o.source,ly.exec(o));return l.lastIndex=o.lastIndex,l}var hy=uy,mf=Me?Me.prototype:void 0,gf=mf?mf.valueOf:void 0;function dy(o){return gf?Object(gf.call(o)):{}}var fy=dy;function py(o,l){var d=l?jl(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.length)}var my=py,gy="[object Boolean]",_y="[object Date]",vy="[object Map]",yy="[object Number]",xy="[object RegExp]",by="[object Set]",Sy="[object String]",My="[object Symbol]",Ty="[object ArrayBuffer]",Ey="[object DataView]",Ay="[object Float32Array]",wy="[object Float64Array]",Py="[object Int8Array]",Ry="[object Int16Array]",Cy="[object Int32Array]",Iy="[object Uint8Array]",Ly="[object Uint8ClampedArray]",Dy="[object Uint16Array]",Ny="[object Uint32Array]";function Oy(o,l,d){var y=o.constructor;switch(l){case Ty:return jl(o);case gy:case _y:return new y(+o);case Ey:return cy(o,d);case Ay:case wy:case Py:case Ry:case Cy:case Iy:case Ly:case Dy:case Ny:return my(o,d);case vy:return new y;case yy:case Sy:return new y(o);case xy:return hy(o);case by:return new y;case My:return fy(o)}}var Uy=Oy;function Fy(o){return typeof o.constructor=="function"&&!Ll(o)?a_(Ul(o)):{}}var By=Fy,ky="[object Map]";function zy(o){return ue(o)&&Eo(o)==ky}var Hy=zy,_f=xs&&xs.isMap,Vy=_f?Dl(_f):Hy,Gy=Vy,Wy="[object Set]";function jy(o){return ue(o)&&Eo(o)==Wy}var Xy=jy,vf=xs&&xs.isSet,qy=vf?Dl(vf):Xy,Yy=qy,Ky=1,Zy=2,$y=4,yf="[object Arguments]",Jy="[object Array]",Qy="[object Boolean]",ex="[object Date]",tx="[object Error]",xf="[object Function]",nx="[object GeneratorFunction]",ix="[object Map]",rx="[object Number]",bf="[object Object]",sx="[object RegExp]",ox="[object Set]",ax="[object String]",cx="[object Symbol]",lx="[object WeakMap]",ux="[object ArrayBuffer]",hx="[object DataView]",dx="[object Float32Array]",fx="[object Float64Array]",px="[object Int8Array]",mx="[object Int16Array]",gx="[object Int32Array]",_x="[object Uint8Array]",vx="[object Uint8ClampedArray]",yx="[object Uint16Array]",xx="[object Uint32Array]",Ft={};Ft[yf]=Ft[Jy]=Ft[ux]=Ft[hx]=Ft[Qy]=Ft[ex]=Ft[dx]=Ft[fx]=Ft[px]=Ft[mx]=Ft[gx]=Ft[ix]=Ft[rx]=Ft[bf]=Ft[sx]=Ft[ox]=Ft[ax]=Ft[cx]=Ft[_x]=Ft[vx]=Ft[yx]=Ft[xx]=!0,Ft[tx]=Ft[xf]=Ft[lx]=!1;function Ra(o,l,d,y,T,C){var B,q=l&Ky,K=l&Zy,se=l&$y;if(d&&(B=T?d(o,y,T,C):d(o)),B!==void 0)return B;if(!ae(o))return o;var ve=Te(o);if(ve){if(B=ry(o),!q)return l_(o,B)}else{var ye=Eo(o),Ce=ye==xf||ye==nx;if(wa(o))return R0(o,q);if(ye==bf||ye==yf||Ce&&!T){if(B=K||Ce?{}:By(o),!q)return K?H0(o,A0(B,o)):F0(o,T0(B,o))}else{if(!Ft[ye])return T?o:{};B=Uy(o,ye,q)}}C||(C=new To);var je=C.get(o);if(je)return je;C.set(o,B),Yy(o)?o.forEach(function(mt){B.add(Ra(mt,l,d,mt,o,C))}):Gy(o)&&o.forEach(function(mt,it){B.set(it,Ra(mt,l,d,it,o,C))});var Be=se?K?j0:Hl:K?Ol:Mo,at=ve?void 0:Be(o);return h_(at||o,function(mt,it){at&&(it=mt,mt=o[it]),_o(B,it,Ra(mt,l,d,it,o,C))}),B}var bx=Ra,Sx=1,Mx=4;function Tx(o){return bx(o,Sx|Mx)}var Ex=Tx,Ax="__lodash_hash_undefined__";function wx(o){return this.__data__.set(o,Ax),this}var Px=wx;function Rx(o){return this.__data__.has(o)}var Cx=Rx;function Ca(o){var l=-1,d=o==null?0:o.length;for(this.__data__=new ps;++l<d;)this.add(o[l])}Ca.prototype.add=Ca.prototype.push=Px,Ca.prototype.has=Cx;var Ix=Ca;function Lx(o,l){for(var d=-1,y=o==null?0:o.length;++d<y;)if(l(o[d],d,o))return!0;return!1}var Dx=Lx;function Nx(o,l){return o.has(l)}var Ox=Nx,Ux=1,Fx=2;function Bx(o,l,d,y,T,C){var B=d&Ux,q=o.length,K=l.length;if(q!=K&&!(B&&K>q))return!1;var se=C.get(o),ve=C.get(l);if(se&&ve)return se==l&&ve==o;var ye=-1,Ce=!0,je=d&Fx?new Ix:void 0;for(C.set(o,l),C.set(l,o);++ye<q;){var Be=o[ye],at=l[ye];if(y)var mt=B?y(at,Be,ye,l,o,C):y(Be,at,ye,o,l,C);if(mt!==void 0){if(mt)continue;Ce=!1;break}if(je){if(!Dx(l,function(it,Tt){if(!Ox(je,Tt)&&(Be===it||T(Be,it,d,y,C)))return je.push(Tt)})){Ce=!1;break}}else if(!(Be===at||T(Be,at,d,y,C))){Ce=!1;break}}return C.delete(o),C.delete(l),Ce}var Sf=Bx;function kx(o){var l=-1,d=Array(o.size);return o.forEach(function(y,T){d[++l]=[T,y]}),d}var zx=kx;function Hx(o){var l=-1,d=Array(o.size);return o.forEach(function(y){d[++l]=y}),d}var Vx=Hx,Gx=1,Wx=2,jx="[object Boolean]",Xx="[object Date]",qx="[object Error]",Yx="[object Map]",Kx="[object Number]",Zx="[object RegExp]",$x="[object Set]",Jx="[object String]",Qx="[object Symbol]",eb="[object ArrayBuffer]",tb="[object DataView]",Mf=Me?Me.prototype:void 0,Xl=Mf?Mf.valueOf:void 0;function nb(o,l,d,y,T,C,B){switch(d){case tb:if(o.byteLength!=l.byteLength||o.byteOffset!=l.byteOffset)return!1;o=o.buffer,l=l.buffer;case eb:return!(o.byteLength!=l.byteLength||!C(new Pa(o),new Pa(l)));case jx:case Xx:case Kx:return pn(+o,+l);case qx:return o.name==l.name&&o.message==l.message;case Zx:case Jx:return o==l+"";case Yx:var q=zx;case $x:var K=y&Gx;if(q||(q=Vx),o.size!=l.size&&!K)return!1;var se=B.get(o);if(se)return se==l;y|=Wx,B.set(o,l);var ve=Sf(q(o),q(l),y,T,C,B);return B.delete(o),ve;case Qx:if(Xl)return Xl.call(o)==Xl.call(l)}return!1}var ib=nb,rb=1,sb=Object.prototype,ob=sb.hasOwnProperty;function ab(o,l,d,y,T,C){var B=d&rb,q=Hl(o),K=q.length,se=Hl(l),ve=se.length;if(K!=ve&&!B)return!1;for(var ye=K;ye--;){var Ce=q[ye];if(!(B?Ce in l:ob.call(l,Ce)))return!1}var je=C.get(o),Be=C.get(l);if(je&&Be)return je==l&&Be==o;var at=!0;C.set(o,l),C.set(l,o);for(var mt=B;++ye<K;){Ce=q[ye];var it=o[Ce],Tt=l[Ce];if(y)var xn=B?y(Tt,it,Ce,l,o,C):y(it,Tt,Ce,o,l,C);if(!(xn===void 0?it===Tt||T(it,Tt,d,y,C):xn)){at=!1;break}mt||(mt=Ce=="constructor")}if(at&&!mt){var On=o.constructor,bn=l.constructor;On!=bn&&"constructor"in o&&"constructor"in l&&!(typeof On=="function"&&On instanceof On&&typeof bn=="function"&&bn instanceof bn)&&(at=!1)}return C.delete(o),C.delete(l),at}var cb=ab,lb=1,Tf="[object Arguments]",Ef="[object Array]",Ia="[object Object]",ub=Object.prototype,Af=ub.hasOwnProperty;function hb(o,l,d,y,T,C){var B=Te(o),q=Te(l),K=B?Ef:Eo(o),se=q?Ef:Eo(l);K=K==Tf?Ia:K,se=se==Tf?Ia:se;var ve=K==Ia,ye=se==Ia,Ce=K==se;if(Ce&&wa(o)){if(!wa(l))return!1;B=!0,ve=!1}if(Ce&&!ve)return C||(C=new To),B||Vd(o)?Sf(o,l,d,y,T,C):ib(o,l,K,d,y,T,C);if(!(d&lb)){var je=ve&&Af.call(o,"__wrapped__"),Be=ye&&Af.call(l,"__wrapped__");if(je||Be){var at=je?o.value():o,mt=Be?l.value():l;return C||(C=new To),T(at,mt,d,y,C)}}return Ce?(C||(C=new To),cb(o,l,d,y,T,C)):!1}var db=hb;function wf(o,l,d,y,T){return o===l?!0:o==null||l==null||!ue(o)&&!ue(l)?o!==o&&l!==l:db(o,l,d,y,wf,T)}var Pf=wf,fb=1,pb=2;function mb(o,l,d,y){var T=d.length,C=T,B=!y;if(o==null)return!C;for(o=Object(o);T--;){var q=d[T];if(B&&q[2]?q[1]!==o[q[0]]:!(q[0]in o))return!1}for(;++T<C;){q=d[T];var K=q[0],se=o[K],ve=q[1];if(B&&q[2]){if(se===void 0&&!(K in o))return!1}else{var ye=new To;if(y)var Ce=y(se,ve,K,o,l,ye);if(!(Ce===void 0?Pf(ve,se,fb|pb,y,ye):Ce))return!1}}return!0}var gb=mb;function _b(o){return o===o&&!ae(o)}var Rf=_b;function vb(o){for(var l=Mo(o),d=l.length;d--;){var y=l[d],T=o[y];l[d]=[y,T,Rf(T)]}return l}var yb=vb;function xb(o,l){return function(d){return d==null?!1:d[o]===l&&(l!==void 0||o in Object(d))}}var Cf=xb;function bb(o){var l=yb(o);return l.length==1&&l[0][2]?Cf(l[0][0],l[0][1]):function(d){return d===o||gb(d,o,l)}}var Sb=bb;function Mb(o,l){return o!=null&&l in Object(o)}var Tb=Mb;function Eb(o,l,d){l=Mr(l,o);for(var y=-1,T=l.length,C=!1;++y<T;){var B=si(l[y]);if(!(C=o!=null&&d(o,B)))break;o=o[B]}return C||++y!=T?C:(T=o==null?0:o.length,!!T&&Il(T)&&vo(B,T)&&(Te(o)||Ud(o)))}var Ab=Eb;function wb(o,l){return o!=null&&Ab(o,l,Tb)}var Pb=wb,Rb=1,Cb=2;function Ib(o,l){return N(o)&&Rf(l)?Cf(si(o),l):function(d){var y=wi(d,o);return y===void 0&&y===l?Pb(d,o):Pf(l,y,Rb|Cb)}}var Lb=Ib;function Db(o){return function(l){return l==null?void 0:l[o]}}var If=Db;function Nb(o){return function(l){return gs(l,o)}}var Ob=Nb;function Ub(o){return N(o)?If(si(o)):Ob(o)}var Fb=Ub;function Bb(o){return typeof o=="function"?o:o==null?Ea:typeof o=="object"?Te(o)?Lb(o[0],o[1]):Sb(o):Fb(o)}var kb=Bb;function zb(o){return function(l,d,y){for(var T=-1,C=Object(l),B=y(l),q=B.length;q--;){var K=B[o?q:++T];if(d(C[K],K,C)===!1)break}return l}}var Hb=zb,Vb=Hb(),Gb=Vb;function Wb(o,l){return o&&Gb(o,l,Mo)}var jb=Wb,Xb=function(){return me.Date.now()},ql=Xb,qb="Expected a function",Yb=Math.max,Kb=Math.min;function Zb(o,l,d){var y,T,C,B,q,K,se=0,ve=!1,ye=!1,Ce=!0;if(typeof o!="function")throw new TypeError(qb);l=b(l)||0,ae(d)&&(ve=!!d.leading,ye="maxWait"in d,C=ye?Yb(b(d.maxWait)||0,l):C,Ce="trailing"in d?!!d.trailing:Ce);function je(Ot){var Sn=y,Xn=T;return y=T=void 0,se=Ot,B=o.apply(Xn,Sn),B}function Be(Ot){return se=Ot,q=setTimeout(it,l),ve?je(Ot):B}function at(Ot){var Sn=Ot-K,Xn=Ot-se,gi=l-Sn;return ye?Kb(gi,C-Xn):gi}function mt(Ot){var Sn=Ot-K,Xn=Ot-se;return K===void 0||Sn>=l||Sn<0||ye&&Xn>=C}function it(){var Ot=ql();if(mt(Ot))return Tt(Ot);q=setTimeout(it,at(Ot))}function Tt(Ot){return q=void 0,Ce&&y?je(Ot):(y=T=void 0,B)}function xn(){q!==void 0&&clearTimeout(q),se=0,y=K=T=q=void 0}function On(){return q===void 0?B:Tt(ql())}function bn(){var Ot=ql(),Sn=mt(Ot);if(y=arguments,T=this,K=Ot,Sn){if(q===void 0)return Be(K);if(ye)return clearTimeout(q),q=setTimeout(it,l),je(K)}return q===void 0&&(q=setTimeout(it,l)),B}return bn.cancel=xn,bn.flush=On,bn}var $b=Zb;function Jb(o){var l=o==null?0:o.length;return l?o[l-1]:void 0}var Qb=Jb;function eS(o,l){return l.length<2?o:gs(o,qd(l,0,-1))}var tS=eS;function nS(o){return typeof o=="number"&&o==gn(o)}var iS=nS;function rS(o,l){var d={};return l=kb(l),jb(o,function(y,T,C){Pi(d,T,l(y,T,C))}),d}var sS=rS;function oS(o,l){return l=Mr(l,o),o=tS(o,l),o==null||delete o[si(Qb(l))]}var aS=oS,cS=9007199254740991,lS=Math.floor;function uS(o,l){var d="";if(!o||l<1||l>cS)return d;do l%2&&(d+=o),l=lS(l/2),l&&(o+=o);while(l);return d}var Lf=uS,hS=If("length"),dS=hS,Df="\\ud800-\\udfff",fS="\\u0300-\\u036f",pS="\\ufe20-\\ufe2f",mS="\\u20d0-\\u20ff",gS=fS+pS+mS,_S="\\ufe0e\\ufe0f",vS="["+Df+"]",Yl="["+gS+"]",Kl="\\ud83c[\\udffb-\\udfff]",yS="(?:"+Yl+"|"+Kl+")",Nf="[^"+Df+"]",Of="(?:\\ud83c[\\udde6-\\uddff]){2}",Uf="[\\ud800-\\udbff][\\udc00-\\udfff]",xS="\\u200d",Ff=yS+"?",Bf="["+_S+"]?",bS="(?:"+xS+"(?:"+[Nf,Of,Uf].join("|")+")"+Bf+Ff+")*",SS=Bf+Ff+bS,MS="(?:"+[Nf+Yl+"?",Yl,Of,Uf,vS].join("|")+")",kf=RegExp(Kl+"(?="+Kl+")|"+MS+SS,"g");function TS(o){for(var l=kf.lastIndex=0;kf.test(o);)++l;return l}var ES=TS;function AS(o){return Fl(o)?ES(o):dS(o)}var zf=AS,wS=Math.ceil;function PS(o,l){l=l===void 0?" ":ha(l);var d=l.length;if(d<2)return d?Lf(l,o):l;var y=Lf(l,wS(o/zf(l)));return Fl(l)?Ov(c0(y),0,o).join(""):y.slice(0,o)}var RS=PS;function CS(o,l,d){o=ms(o),l=gn(l);var y=l?zf(o):0;return l&&y<l?RS(l-y,d)+o:o}var Ao=CS;function IS(o,l){return o==null?!0:aS(o,l)}var Hf=IS,LS=5*1e3,DS=class{constructor(o){S(this,"_cache",new Qi),S(this,"_keepHotUntapDebounce"),le(this,o)}get type(){return"Theatre_SheetObject_PublicAPI"}get props(){return $(this).propsP}get sheet(){return $(this).sheet.publicApi}get project(){return $(this).sheet.project.publicApi}get address(){return g({},$(this).address)}_valuesPrism(){return this._cache.get("_valuesPrism",()=>{const o=$(this);return(0,xo.prism)(()=>(0,xo.val)(o.getValues().getValue()))})}onValuesChange(o,l){return xu(this._valuesPrism(),o,l)}get value(){const o=this._valuesPrism();{if(!o.isHot){this._keepHotUntapDebounce!=null&&this._keepHotUntapDebounce.flush();const l=o.keepHot();this._keepHotUntapDebounce=$b(()=>{l(),this._keepHotUntapDebounce=void 0},LS)}this._keepHotUntapDebounce&&this._keepHotUntapDebounce()}return o.getValue()}set initialValue(o){$(this).setInitialValue(o)}};function NS(o){const l=new WeakMap;return d=>(l.has(d)||l.set(d,o(d)),l.get(d))}function La(o){return o.type==="compound"||o.type==="enum"}function Zl(o,l){if(!o)return;const[d,...y]=l;if(d===void 0)return o;if(!La(o))return;const T=o.type==="enum"?o.cases[d]:o.props[d];return Zl(T,y)}function OS(o){return!La(o)}var US=class{constructor(o,l,d){this.sheet=o,this.template=l,this.nativeObject=d,S(this,"$$isPointerToPrismProvider",!0),S(this,"address"),S(this,"publicApi"),S(this,"_initialValue",new It.Atom({})),S(this,"_cache",new Qi),S(this,"_logger"),S(this,"_internalUtilCtx"),this._logger=o._logger.named("SheetObject",l.address.objectKey),this._logger._trace("creating object"),this._internalUtilCtx={logger:this._logger.utilFor.internal()},this.address=x(g({},l.address),{sheetInstanceId:o.address.sheetInstanceId}),this.publicApi=new DS(this)}get type(){return"Theatre_SheetObject"}getValues(){return this._cache.get("getValues()",()=>(0,It.prism)(()=>{const o=(0,It.val)(this.template.getDefaultValues()),l=(0,It.val)(this._initialValue.pointer),d=It.prism.memo("withInitialCache",()=>new WeakMap,[]),y=Ar(o,l,d),T=(0,It.val)(this.template.getStaticValues()),C=It.prism.memo("withStatics",()=>new WeakMap,[]);let q=Ar(y,T,C),K;{const ve=It.prism.memo("seq",()=>this.getSequencedValues(),[]),ye=It.prism.memo("withSeqsCache",()=>new WeakMap,[]);K=(0,It.val)((0,It.val)(ve)),q=Ar(q,K,ye)}return xa("finalAtom",q).pointer}))}getValueByPointer(o){const l=(0,It.val)(this.getValues()),{path:d}=(0,It.getPointerParts)(o);return(0,It.val)(wr(l,d))}pointerToPrism(o){const{path:l}=(0,It.getPointerParts)(o);return(0,It.prism)(()=>{const d=(0,It.val)(this.getValues());return(0,It.val)(wr(d,l))})}getSequencedValues(){return(0,It.prism)(()=>{const o=It.prism.memo("tracksToProcess",()=>this.template.getArrayOfValidSequenceTracks(),[]),l=(0,It.val)(o),d=new It.Atom({}),y=(0,It.val)(this.template.configPointer);return It.prism.effect("processTracks",()=>{const T=[];for(const{trackId:C,pathToProp:B}of l){const q=this._trackIdToPrism(C),K=Zl(y,B),se=K.deserializeAndSanitize,ve=K.interpolate,ye=()=>{const je=q.getValue();if(!je)return d.setByPointer(Tt=>wr(Tt,B),void 0);const Be=se(je.left),at=Be===void 0?K.default:Be;if(je.right===void 0)return d.setByPointer(Tt=>wr(Tt,B),at);const mt=se(je.right),it=mt===void 0?K.default:mt;return d.setByPointer(Tt=>wr(Tt,B),ve(at,it,je.progression))},Ce=q.onStale(ye);ye(),T.push(Ce)}return()=>{for(const C of T)C()}},[y,...l]),d.pointer})}_trackIdToPrism(o){const l=this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[o],d=this.sheet.getSequence().positionPrism;return Sl(this._internalUtilCtx,l,d)}get propsP(){return this._cache.get("propsP",()=>(0,It.pointer)({root:this,path:[]}))}validateValue(o,l){}setInitialValue(o){this.validateValue(this.propsP,o),this._initialValue.set(o)}};function Bt(o){return function(d,y){return o(d,y())}}var Gn={_hmm:Wn(524),_todo:Wn(522),_error:Wn(521),errorDev:Wn(529),errorPublic:Wn(545),_kapow:Wn(268),_warn:Wn(265),warnDev:Wn(273),warnPublic:Wn(289),_debug:Wn(137),debugDev:Wn(145),_trace:Wn(73),traceDev:Wn(81)};function Wn(o){return Object.freeze({audience:Ir(o,8)?"internal":Ir(o,16)?"dev":"public",category:Ir(o,4)?"troubleshooting":Ir(o,2)?"todo":"general",level:Ir(o,512)?512:Ir(o,256)?256:Ir(o,128)?128:64})}function Ir(o,l){return(o&l)===l}function kt(o,l){return((l&32)===32?!0:(l&16)===16?o.dev:(l&8)===8?o.internal:!1)&&o.min<=l}var Ri={loggingConsoleStyle:!0,loggerConsoleStyle:!0,includes:Object.freeze({internal:!1,dev:!1,min:256}),filtered:function(){},include:function(){return{}},create:null,creatExt:null,named(o,l,d){return this.create({names:[...o.names,{name:l,key:d}]})},style:{bold:void 0,italic:void 0,cssMemo:new Map([["",""]]),collapseOnRE:/[a-z- ]+/g,color:void 0,collapsed(o){if(o.length<5)return o;const l=o.replace(this.collapseOnRE,"");return this.cssMemo.has(l)||this.cssMemo.set(l,this.css(o)),l},css(o){var l,d,y,T;const C=this.cssMemo.get(o);if(C)return C;let B="color:".concat((d=(l=this.color)==null?void 0:l.call(this,o))!=null?d:"hsl(".concat((o.charCodeAt(0)+o.charCodeAt(o.length-1))%360,", 100%, 60%)"));return(y=this.bold)!=null&&y.test(o)&&(B+=";font-weight:600"),(T=this.italic)!=null&&T.test(o)&&(B+=";font-style:italic"),this.cssMemo.set(o,B),B}}};function Vf(o=console,l={}){const d=x(g({},Ri),{includes:g({},Ri.includes)}),y={styled:kS.bind(d,o),noStyle:HS.bind(d,o)},T=BS.bind(d);function C(){return d.loggingConsoleStyle&&d.loggerConsoleStyle?y.styled:y.noStyle}return d.create=C(),{configureLogger(B){var q;B==="console"?(d.loggerConsoleStyle=Ri.loggerConsoleStyle,d.create=C()):B.type==="console"?(d.loggerConsoleStyle=(q=B.style)!=null?q:Ri.loggerConsoleStyle,d.create=C()):B.type==="keyed"?(d.creatExt=K=>B.keyed(K.names),d.create=T):B.type==="named"&&(d.creatExt=FS.bind(null,B.named),d.create=T)},configureLogging(B){var q,K,se,ve,ye;d.includes.dev=(q=B.dev)!=null?q:Ri.includes.dev,d.includes.internal=(K=B.internal)!=null?K:Ri.includes.internal,d.includes.min=(se=B.min)!=null?se:Ri.includes.min,d.include=(ve=B.include)!=null?ve:Ri.include,d.loggingConsoleStyle=(ye=B.consoleStyle)!=null?ye:Ri.loggingConsoleStyle,d.create=C()},getLogger(){return d.create({names:[]})}}}function FS(o,l){const d=[];for(let{name:y,key:T}of l.names)d.push(T==null?y:"".concat(y," (").concat(T,")"));return o(d)}function BS(o){const l=g(g({},this.includes),this.include(o)),d=this.filtered,y=this.named.bind(this,o),T=this.creatExt(o),C=kt(l,524),B=kt(l,522),q=kt(l,521),K=kt(l,529),se=kt(l,545),ve=kt(l,265),ye=kt(l,268),Ce=kt(l,273),je=kt(l,289),Be=kt(l,137),at=kt(l,145),mt=kt(l,73),it=kt(l,81),Tt=C?T.error.bind(T,Gn._hmm):d.bind(o,524),xn=B?T.error.bind(T,Gn._todo):d.bind(o,522),On=q?T.error.bind(T,Gn._error):d.bind(o,521),bn=K?T.error.bind(T,Gn.errorDev):d.bind(o,529),Ot=se?T.error.bind(T,Gn.errorPublic):d.bind(o,545),Sn=ye?T.warn.bind(T,Gn._kapow):d.bind(o,268),Xn=ve?T.warn.bind(T,Gn._warn):d.bind(o,265),gi=Ce?T.warn.bind(T,Gn.warnDev):d.bind(o,273),Fr=je?T.warn.bind(T,Gn.warnPublic):d.bind(o,273),Br=Be?T.debug.bind(T,Gn._debug):d.bind(o,137),kr=at?T.debug.bind(T,Gn.debugDev):d.bind(o,145),zr=mt?T.trace.bind(T,Gn._trace):d.bind(o,73),Hr=it?T.trace.bind(T,Gn.traceDev):d.bind(o,81),$t={_hmm:Tt,_todo:xn,_error:On,errorDev:bn,errorPublic:Ot,_kapow:Sn,_warn:Xn,warnDev:gi,warnPublic:Fr,_debug:Br,debugDev:kr,_trace:zr,traceDev:Hr,lazy:{_hmm:C?Bt(Tt):Tt,_todo:B?Bt(xn):xn,_error:q?Bt(On):On,errorDev:K?Bt(bn):bn,errorPublic:se?Bt(Ot):Ot,_kapow:ye?Bt(Sn):Sn,_warn:ve?Bt(Xn):Xn,warnDev:Ce?Bt(gi):gi,warnPublic:je?Bt(Fr):Fr,_debug:Be?Bt(Br):Br,debugDev:at?Bt(kr):kr,_trace:mt?Bt(zr):zr,traceDev:it?Bt(Hr):Hr},named:y,utilFor:{internal(){return{debug:$t._debug,error:$t._error,warn:$t._warn,trace:$t._trace,named(qn,zt){return $t.named(qn,zt).utilFor.internal()}}},dev(){return{debug:$t.debugDev,error:$t.errorDev,warn:$t.warnDev,trace:$t.traceDev,named(qn,zt){return $t.named(qn,zt).utilFor.dev()}}},public(){return{error:$t.errorPublic,warn:$t.warnPublic,debug(qn,zt){$t._warn('(public "debug" filtered out) '.concat(qn),zt)},trace(qn,zt){$t._warn('(public "trace" filtered out) '.concat(qn),zt)},named(qn,zt){return $t.named(qn,zt).utilFor.public()}}}}};return $t}function kS(o,l){const d=g(g({},this.includes),this.include(l)),y=[];let T="";for(let K=0;K<l.names.length;K++){const{name:se,key:ve}=l.names[K];if(T+=" %c".concat(se),y.push(this.style.css(se)),ve!=null){const ye="%c#".concat(ve);T+=ye,y.push(this.style.css(ye))}}const C=this.filtered,B=this.named.bind(this,l),q=[T,...y];return Gf(C,l,d,o,q,zS(q),B)}function zS(o){const l=o.slice(0);for(let d=1;d<l.length;d++)l[d]+=";background-color:#e0005a;padding:2px;color:white";return l}function HS(o,l){const d=g(g({},this.includes),this.include(l));let y="";for(let q=0;q<l.names.length;q++){const{name:K,key:se}=l.names[q];y+=" ".concat(K),se!=null&&(y+="#".concat(se))}const T=this.filtered,C=this.named.bind(this,l),B=[y];return Gf(T,l,d,o,B,B,C)}function Gf(o,l,d,y,T,C,B){const q=kt(d,524),K=kt(d,522),se=kt(d,521),ve=kt(d,529),ye=kt(d,545),Ce=kt(d,265),je=kt(d,268),Be=kt(d,273),at=kt(d,289),mt=kt(d,137),it=kt(d,145),Tt=kt(d,73),xn=kt(d,81),On=q?y.error.bind(y,...T):o.bind(l,524),bn=K?y.error.bind(y,...T):o.bind(l,522),Ot=se?y.error.bind(y,...T):o.bind(l,521),Sn=ve?y.error.bind(y,...T):o.bind(l,529),Xn=ye?y.error.bind(y,...T):o.bind(l,545),gi=je?y.warn.bind(y,...C):o.bind(l,268),Fr=Ce?y.warn.bind(y,...T):o.bind(l,265),Br=Be?y.warn.bind(y,...T):o.bind(l,273),kr=at?y.warn.bind(y,...T):o.bind(l,273),zr=mt?y.info.bind(y,...T):o.bind(l,137),Hr=it?y.info.bind(y,...T):o.bind(l,145),$t=Tt?y.debug.bind(y,...T):o.bind(l,73),qn=xn?y.debug.bind(y,...T):o.bind(l,81),zt={_hmm:On,_todo:bn,_error:Ot,errorDev:Sn,errorPublic:Xn,_kapow:gi,_warn:Fr,warnDev:Br,warnPublic:kr,_debug:zr,debugDev:Hr,_trace:$t,traceDev:qn,lazy:{_hmm:q?Bt(On):On,_todo:K?Bt(bn):bn,_error:se?Bt(Ot):Ot,errorDev:ve?Bt(Sn):Sn,errorPublic:ye?Bt(Xn):Xn,_kapow:je?Bt(gi):gi,_warn:Ce?Bt(Fr):Fr,warnDev:Be?Bt(Br):Br,warnPublic:at?Bt(kr):kr,_debug:mt?Bt(zr):zr,debugDev:it?Bt(Hr):Hr,_trace:Tt?Bt($t):$t,traceDev:xn?Bt(qn):qn},named:B,utilFor:{internal(){return{debug:zt._debug,error:zt._error,warn:zt._warn,trace:zt._trace,named(Li,Di){return zt.named(Li,Di).utilFor.internal()}}},dev(){return{debug:zt.debugDev,error:zt.errorDev,warn:zt.warnDev,trace:zt.traceDev,named(Li,Di){return zt.named(Li,Di).utilFor.dev()}}},public(){return{error:zt.errorPublic,warn:zt.warnPublic,debug(Li,Di){zt._warn('(public "debug" filtered out) '.concat(Li),Di)},trace(Li,Di){zt._warn('(public "trace" filtered out) '.concat(Li),Di)},named(Li,Di){return zt.named(Li,Di).utilFor.public()}}}}};return zt}var Wf=Vf(console,{});Wf.configureLogging({dev:!0,min:64});var Da=Wf.getLogger().named("Theatre.js (default logger)").utilFor.dev(),jf=new WeakMap;function VS(o){const l=jf.get(o);if(l)return l;const d=new Map;return jf.set(o,d),Xf([],o,d),d}function Xf(o,l,d){for(const[y,T]of Object.entries(l.props))if(!La(T)){const C=[...o,y];d.set(JSON.stringify(C),d.size),qf(C,T,d)}for(const[y,T]of Object.entries(l.props))if(La(T)){const C=[...o,y];d.set(JSON.stringify(C),d.size),qf(C,T,d)}}function qf(o,l,d){if(l.type==="compound")Xf(o,l,d);else{if(l.type==="enum")throw new Error("Enums aren't supported yet");d.set(JSON.stringify(o),d.size)}}function Yf(o){return typeof o=="object"&&o!==null&&Object.keys(o).length===0}var GS=class{constructor(o,l,d,y,T){this.sheetTemplate=o,S(this,"address"),S(this,"type","Theatre_SheetObjectTemplate"),S(this,"_config"),S(this,"_temp_actions_atom"),S(this,"_cache",new Qi),S(this,"project"),S(this,"pointerToSheetState"),S(this,"pointerToStaticOverrides"),this.address=x(g({},o.address),{objectKey:l}),this._config=new en.Atom(y),this._temp_actions_atom=new en.Atom(T),this.project=o.project,this.pointerToSheetState=this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId],this.pointerToStaticOverrides=this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey]}get staticConfig(){return this._config.get()}get configPointer(){return this._config.pointer}get _temp_actions(){return this._temp_actions_atom.get()}get _temp_actionsPointer(){return this._temp_actions_atom.pointer}createInstance(o,l,d){return this._config.set(d),new US(o,this,l)}reconfigure(o){this._config.set(o)}_temp_setActions(o){this._temp_actions_atom.set(o)}getDefaultValues(){return this._cache.get("getDefaultValues()",()=>(0,en.prism)(()=>{const o=(0,en.val)(this.configPointer);return xl(o)}))}getStaticValues(){return this._cache.get("getStaticValues",()=>(0,en.prism)(()=>{var o;const l=(o=(0,en.val)(this.pointerToStaticOverrides))!=null?o:{};return(0,en.val)(this.configPointer).deserializeAndSanitize(l)||{}}))}getArrayOfValidSequenceTracks(){return this._cache.get("getArrayOfValidSequenceTracks",()=>(0,en.prism)(()=>{const o=this.project.pointers.historic.sheetsById[this.address.sheetId],l=(0,en.val)(o.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath);if(!l)return ne;const d=[];if(!l)return ne;const y=(0,en.val)(this.configPointer),T=Object.entries(l);for(const[B,q]of T){const K=WS(B);if(!K)continue;const se=Zl(y,K);se&&OS(se)&&d.push({pathToProp:K,trackId:q})}const C=VS(y);return d.sort((B,q)=>{const K=B.pathToProp,se=q.pathToProp,ve=C.get(JSON.stringify(K)),ye=C.get(JSON.stringify(se));return ve>ye?1:-1}),d.length===0?ne:d}))}getMapOfValidSequenceTracks_forStudio(){return this._cache.get("getMapOfValidSequenceTracks_forStudio",()=>(0,en.prism)(()=>{const o=(0,en.val)(this.getArrayOfValidSequenceTracks());let l={};for(const{pathToProp:d,trackId:y}of o)vs(l,d,y);return l}))}getStaticButNotSequencedOverrides(){return this._cache.get("getStaticButNotSequencedOverrides",()=>(0,en.prism)(()=>{const o=(0,en.val)(this.getStaticValues()),l=(0,en.val)(this.getArrayOfValidSequenceTracks()),d=Ex(o);for(const{pathToProp:y}of l){Hf(d,y);let T=y.slice(0,-1);for(;T.length>0;){const C=fa(d,T);if(!Yf(C))break;Hf(d,T),T=T.slice(0,-1)}}if(!Yf(d))return d}))}getDefaultsAtPointer(o){const{path:l}=(0,en.getPointerParts)(o),d=this.getDefaultValues().getValue();return fa(d,l)}};function WS(o){try{return JSON.parse(o)}catch{Da.warn("property ".concat(JSON.stringify(o)," cannot be parsed. Skipping."));return}}var Kf=nn(),jS=NS(o=>JSON.stringify(o));A(U());var XS=class extends Error{},wo=class extends XS{},Zf=nn(),qS=nn(),YS=nn(),un=nn();function tr(){let o,l;const d=new Promise((T,C)=>{o=B=>{T(B),y.status="resolved"},l=B=>{C(B),y.status="rejected"}}),y={resolve:o,reject:l,promise:d,status:"pending"};return y}var KS=()=>{},Na=KS,ZS=nn(),$S=class{constructor(){S(this,"_stopPlayCallback",Na),S(this,"_state",new ZS.Atom({position:0,playing:!1})),S(this,"statePointer"),this.statePointer=this._state.pointer}destroy(){}pause(){this._stopPlayCallback(),this.playing=!1,this._stopPlayCallback=Na}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.setByPointer(l=>l.position,o)}getCurrentPosition(){return this._state.get().position}get playing(){return this._state.get().playing}set playing(o){this._state.setByPointer(l=>l.playing,o)}play(o,l,d,y,T){this.playing&&this.pause(),this.playing=!0;const C=l[1]-l[0];{const Ce=this.getCurrentPosition();Ce<l[0]||Ce>l[1]?y==="normal"||y==="alternate"?this._updatePositionInState(l[0]):(y==="reverse"||y==="alternateReverse")&&this._updatePositionInState(l[1]):y==="normal"||y==="alternate"?Ce===l[1]&&this._updatePositionInState(l[0]):Ce===l[0]&&this._updatePositionInState(l[1])}const B=tr(),q=T.time,K=C*o;let se=this.getCurrentPosition()-l[0];(y==="reverse"||y==="alternateReverse")&&(se=l[1]-this.getCurrentPosition());const ve=Ce=>{const Be=Math.max(Ce-q,0)/1e3,at=Math.min(Be*d+se,K);if(at!==K){const mt=Math.floor(at/C);let it=at/C%1*C;if(y!=="normal")if(y==="reverse")it=C-it;else{const Tt=mt%2===0;y==="alternate"?Tt||(it=C-it):Tt&&(it=C-it)}this._updatePositionInState(it+l[0]),ye()}else{if(y==="normal")this._updatePositionInState(l[1]);else if(y==="reverse")this._updatePositionInState(l[0]);else{const mt=(o-1)%2===0;y==="alternate"?mt?this._updatePositionInState(l[1]):this._updatePositionInState(l[0]):mt?this._updatePositionInState(l[0]):this._updatePositionInState(l[1])}this.playing=!1,B.resolve(!0)}};this._stopPlayCallback=()=>{T.offThisOrNextTick(ve),T.offNextTick(ve),this.playing&&B.resolve(!1)};const ye=()=>T.onNextTick(ve);return T.onThisOrNextTick(ve),B.promise}playDynamicRange(o,l){this.playing&&this.pause(),this.playing=!0;const d=tr(),y=o.keepHot();d.promise.then(y,y);let T=l.time;const C=q=>{const K=Math.max(q-T,0);T=q;const se=K/1e3,ve=this.getCurrentPosition(),ye=o.getValue();if(ve<ye[0]||ve>ye[1])this.gotoPosition(ye[0]);else{let Ce=ve+se;Ce>ye[1]&&(Ce=ye[0]+(Ce-ye[1])),this.gotoPosition(Ce)}B()};this._stopPlayCallback=()=>{l.offThisOrNextTick(C),l.offNextTick(C),d.resolve(!1)};const B=()=>l.onNextTick(C);return l.onThisOrNextTick(C),d.promise}},JS=nn(),QS="__TheatreJS_StudioBundle",$l="__TheatreJS_CoreBundle",eM="__TheatreJS_Notifications",Oa=o=>(...l)=>{var d;switch(o){case"success":{Da.debug(l.slice(0,2).join(`
`));break}case"info":{Da.debug(l.slice(0,2).join(`
`));break}case"warning":{Da.warn(l.slice(0,2).join(`
`));break}}return typeof window<"u"?(d=window[eM])==null?void 0:d.notify[o](...l):void 0},Ss={warning:Oa("warning"),success:Oa("success"),info:Oa("info"),error:Oa("error")};typeof window<"u"&&(window.addEventListener("error",o=>{Ss.error("An error occurred","<pre>".concat(o.message,`</pre>

See **console** for details.`))}),window.addEventListener("unhandledrejection",o=>{Ss.error("An error occurred","<pre>".concat(o.reason,`</pre>

See **console** for details.`))}));var tM=class{constructor(o,l,d){this._decodedBuffer=o,this._audioContext=l,this._nodeDestination=d,S(this,"_mainGain"),S(this,"_state",new JS.Atom({position:0,playing:!1})),S(this,"statePointer"),S(this,"_stopPlayCallback",Na),this.statePointer=this._state.pointer,this._mainGain=this._audioContext.createGain(),this._mainGain.connect(this._nodeDestination)}playDynamicRange(o,l){const d=tr();this._playing&&this.pause(),this._playing=!0;let y;const T=()=>{y==null||y(),y=this._loopInRange(o.getValue(),l).stop},C=o.onStale(T);return T(),this._stopPlayCallback=()=>{y==null||y(),C(),d.resolve(!1)},d.promise}_loopInRange(o,l){let y=this.getCurrentPosition();const T=o[1]-o[0];y<o[0]||y>o[1]?this._updatePositionInState(o[0]):y===o[1]&&this._updatePositionInState(o[0]),y=this.getCurrentPosition();const C=this._audioContext.createBufferSource();C.buffer=this._decodedBuffer,C.connect(this._mainGain),C.playbackRate.value=1,C.loop=!0,C.loopStart=o[0],C.loopEnd=o[1];const B=l.time;let q=y-o[0];C.start(0,y);const K=ye=>{let at=(Math.max(ye-B,0)/1e3*1+q)/T%1*T;this._updatePositionInState(at+o[0]),se()},se=()=>l.onNextTick(K);return l.onThisOrNextTick(K),{stop:()=>{C.stop(),C.disconnect(),l.offThisOrNextTick(K),l.offNextTick(K)}}}get _playing(){return this._state.get().playing}set _playing(o){this._state.setByPointer(l=>l.playing,o)}destroy(){}pause(){this._stopPlayCallback(),this._playing=!1,this._stopPlayCallback=Na}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.reduce(l=>x(g({},l),{position:o}))}getCurrentPosition(){return this._state.get().position}play(o,l,d,y,T){this._playing&&this.pause(),this._playing=!0;let C=this.getCurrentPosition();const B=l[1]-l[0];if(y!=="normal")throw new wo('Audio-controlled sequences can only be played in the "normal" direction. '+"'".concat(y,"' given."));C<l[0]||C>l[1]?this._updatePositionInState(l[0]):C===l[1]&&this._updatePositionInState(l[0]),C=this.getCurrentPosition();const q=tr(),K=this._audioContext.createBufferSource();K.buffer=this._decodedBuffer,K.connect(this._mainGain),K.playbackRate.value=d,o>1e3&&(Ss.warning("Can't play sequences with audio more than 1000 times","The sequence will still play, but only 1000 times. The `iterationCount: ".concat(o,"` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),[{url:"https://www.theatrejs.com/docs/latest/manual/audio",title:"Using Audio"},{url:"https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",title:"Audio API"}]),o=1e3),o>1&&(K.loop=!0,K.loopStart=l[0],K.loopEnd=l[1]);const se=T.time;let ve=C-l[0];const ye=B*o;K.start(0,C,ye-ve);const Ce=at=>{const it=Math.max(at-se,0)/1e3,Tt=Math.min(it*d+ve,ye);if(Tt!==ye){let xn=Tt/B%1*B;this._updatePositionInState(xn+l[0]),Be()}else this._updatePositionInState(l[1]),this._playing=!1,je(),q.resolve(!0)},je=()=>{K.stop(),K.disconnect()};this._stopPlayCallback=()=>{je(),T.offThisOrNextTick(Ce),T.offNextTick(Ce),this._playing&&q.resolve(!1)};const Be=()=>T.onNextTick(Ce);return T.onThisOrNextTick(Ce),q.promise}},nM=nn(),$f=0;function Jl(o){var l;const d=B=>{y.tick(B)},y=new nM.Ticker({onActive(){var B;(B=o==null?void 0:o.start)==null||B.call(o)},onDormant(){var B;(B=o==null?void 0:o.stop)==null||B.call(o)}}),T={tick:d,id:$f++,name:(l=o==null?void 0:o.name)!=null?l:"CustomRafDriver-".concat($f),type:"Theatre_RafDriver_PublicAPI"},C={type:"Theatre_RafDriver_PrivateAPI",publicApi:T,ticker:y,start:o==null?void 0:o.start,stop:o==null?void 0:o.stop};return le(T,C),T}function iM(){let o=null;const y=Jl({name:"DefaultCoreRafDriver",start:()=>{if(typeof window<"u"){const T=C=>{y.tick(C),o=window.requestAnimationFrame(T)};o=window.requestAnimationFrame(T)}else y.tick(0),setTimeout(()=>y.tick(1),0)},stop:()=>{typeof window<"u"&&o!==null&&window.cancelAnimationFrame(o)}});return y}var Ua;function Jf(){return Ua||rM(iM()),Ua}function Qf(){return Jf().ticker}function rM(o){if(Ua)throw new Error("`setCoreRafDriver()` is already called.");Ua=$(o)}var sM=class{get type(){return"Theatre_Sequence_PublicAPI"}constructor(o){le(this,o)}play(o){const l=$(this);if(l._project.isReady()){const d=o!=null&&o.rafDriver?$(o.rafDriver).ticker:Qf();return l.play(o??{},d)}else{const d=tr();return d.resolve(!0),d.promise}}pause(){$(this).pause()}get position(){return $(this).position}set position(o){$(this).position=o}__experimental_getKeyframes(o){return $(this).getKeyframesOfSimpleProp(o)}async attachAudio(o){const{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:T}=await oM(o),C=new tM(y,l,T);return $(this).replacePlaybackController(C),{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:T}}get pointer(){return $(this).pointer}};async function oM(o){function l(){if(o.audioContext)return Promise.resolve(o.audioContext);const se=new AudioContext;return se.state==="running"||typeof window>"u"?Promise.resolve(se):new Promise(ve=>{const ye=()=>{se.resume().catch(Be=>{console.error(Be)})},Ce=["mousedown","keydown","touchstart"],je={capture:!0,passive:!1};Ce.forEach(Be=>{window.addEventListener(Be,ye,je)}),se.addEventListener("statechange",()=>{se.state==="running"&&(Ce.forEach(Be=>{window.removeEventListener(Be,ye,je)}),ve(se))})})}async function d(){if(o.source instanceof AudioBuffer)return o.source;const se=tr();if(typeof o.source!="string")throw new Error("Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer.");let ve;try{ve=await fetch(o.source)}catch(Be){throw console.error(Be),new Error("Could not fetch '".concat(o.source,"'. Network error logged above."))}let ye;try{ye=await ve.arrayBuffer()}catch(Be){throw console.error(Be),new Error("Could not read '".concat(o.source,"' as an arrayBuffer."))}(await y).decodeAudioData(ye,se.resolve,se.reject);let je;try{je=await se.promise}catch(Be){throw console.error(Be),new Error("Could not decode ".concat(o.source," as an audio file."))}return je}const y=l(),T=d(),[C,B]=await Promise.all([y,T]),q=o.destinationNode||C.destination,K=C.createGain();return K.connect(q),{audioContext:C,decodedBuffer:B,gainNode:K,destinationNode:q}}var aM=cM("Theatre_SheetObject");function cM(o){return l=>typeof l=="object"&&!!l&&l.type===o}var lM=class{constructor(o,l,d,y,T){this._project=o,this._sheet=l,this._lengthD=d,this._subUnitsPerUnitD=y,S(this,"address"),S(this,"publicApi"),S(this,"_playbackControllerBox"),S(this,"_prismOfStatePointer"),S(this,"_positionD"),S(this,"_positionFormatterD"),S(this,"_playableRangeD"),S(this,"pointer",(0,YS.pointer)({root:this,path:[]})),S(this,"$$isPointerToPrismProvider",!0),S(this,"_logger"),S(this,"closestGridPosition",C=>{const q=1/this.subUnitsPerUnit;return parseFloat((Math.round(C/q)*q).toFixed(3))}),this._logger=o._logger.named("Sheet",l.address.sheetId).named("Instance",l.address.sheetInstanceId),this.address=x(g({},this._sheet.address),{sequenceName:"default"}),this.publicApi=new sM(this),this._playbackControllerBox=new qS.Atom(T??new $S),this._prismOfStatePointer=(0,un.prism)(()=>this._playbackControllerBox.prism.getValue().statePointer),this._positionD=(0,un.prism)(()=>{const C=this._prismOfStatePointer.getValue();return(0,un.val)(C.position)}),this._positionFormatterD=(0,un.prism)(()=>{const C=(0,un.val)(this._subUnitsPerUnitD);return new uM(C)})}get type(){return"Theatre_Sequence"}pointerToPrism(o){const{path:l}=(0,Zf.getPointerParts)(o);if(l.length===0)return(0,un.prism)(()=>({length:(0,un.val)(this.pointer.length),playing:(0,un.val)(this.pointer.playing),position:(0,un.val)(this.pointer.position),subUnitsPerUnit:(0,un.val)(this.pointer.subUnitsPerUnit)}));if(l.length>1)return(0,un.prism)(()=>{});const[d]=l;return d==="length"?this._lengthD:d==="subUnitsPerUnit"?this._subUnitsPerUnitD:d==="position"?this._positionD:d==="playing"?(0,un.prism)(()=>(0,un.val)(this._prismOfStatePointer.getValue().playing)):(0,un.prism)(()=>{})}getKeyframesOfSimpleProp(o){const{path:l,root:d}=(0,Zf.getPointerParts)(o);if(!aM(d))throw new wo("Argument prop must be a pointer to a SheetObject property");const y=(0,un.val)(this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[d.address.objectKey]);if(!y)return[];const{trackData:T,trackIdByPropPath:C}=y,B=jS(l),q=C[B];if(!q)return[];const K=T[q];return K?K.keyframes:[]}get positionFormatter(){return this._positionFormatterD.getValue()}get prismOfStatePointer(){return this._prismOfStatePointer}get length(){return this._lengthD.getValue()}get positionPrism(){return this._positionD}get position(){return this._playbackControllerBox.get().getCurrentPosition()}get subUnitsPerUnit(){return this._subUnitsPerUnitD.getValue()}get positionSnappedToGrid(){return this.closestGridPosition(this.position)}set position(o){let l=o;this.pause(),l>this.length&&(l=this.length);const d=this.length;this._playbackControllerBox.get().gotoPosition(l>d?d:l)}getDurationCold(){return this._lengthD.getValue()}get playing(){return(0,un.val)(this._playbackControllerBox.get().statePointer.playing)}_makeRangeFromSequenceTemplate(){return(0,un.prism)(()=>[0,(0,un.val)(this._lengthD)])}playDynamicRange(o,l){return this._playbackControllerBox.get().playDynamicRange(o,l)}async play(o,l){const d=this.length,y=o&&o.range?o.range:[0,d],T=o&&typeof o.iterationCount=="number"?o.iterationCount:1,C=o&&typeof o.rate<"u"?o.rate:1,B=o&&o.direction?o.direction:"normal";return await this._play(T,[y[0],y[1]],C,B,l)}_play(o,l,d,y,T){return this._playbackControllerBox.get().play(o,l,d,y,T)}pause(){this._playbackControllerBox.get().pause()}replacePlaybackController(o){this.pause();const l=this._playbackControllerBox.get();this._playbackControllerBox.set(o);const d=l.getCurrentPosition();l.destroy(),o.gotoPosition(d)}},uM=class{constructor(o){this._fps=o}formatSubUnitForGrid(o){const l=o%1,d=1/this._fps;return Math.round(l/d)+"f"}formatFullUnitForGrid(o){let l=o,d="";if(l>=Ms){const T=Math.floor(l/Ms);d+=T+"h",l=l%Ms}if(l>=Dr){const T=Math.floor(l/Dr);d+=T+"m",l=l%Dr}if(l>=Lr){const T=Math.floor(l/Lr);d+=T+"s",l=l%Lr}const y=1/this._fps;if(l>=y){const T=Math.floor(l/y);d+=T+"f",l=l%y}return d.length===0?"0s":d}formatForPlayhead(o){let l=o,d="";if(l>=Ms){const T=Math.floor(l/Ms);d+=Ao(T.toString(),2,"0")+"h",l=l%Ms}if(l>=Dr){const T=Math.floor(l/Dr);d+=Ao(T.toString(),2,"0")+"m",l=l%Dr}else d.length>0&&(d+="00m");if(l>=Lr){const T=Math.floor(l/Lr);d+=Ao(T.toString(),2,"0")+"s",l=l%Lr}else d+="00s";const y=1/this._fps;if(l>=y){const T=Math.round(l/y);d+=Ao(T.toString(),2,"0")+"f",l=l%y}else l/y>.98?(d+=Ao("1",2,"0")+"f",l=l%y):d+="00f";return d.length===0?"00s00f":d}formatBasic(o){return o.toFixed(2)+"s"}},Lr=1,Dr=Lr*60,Ms=Dr*60,Ql={};v(Ql,{boolean:()=>op,compound:()=>tu,file:()=>vM,image:()=>xM,number:()=>sp,rgba:()=>EM,string:()=>ap,stringLiteral:()=>CM});function ep(o,l){return o.length<=l?o:o.substr(0,l-3)+"..."}var hM=o=>typeof o=="string"?'string("'.concat(ep(o,10),'")'):typeof o=="number"?"number(".concat(ep(String(o),10),")"):o===null?"null":o===void 0?"undefined":typeof o=="boolean"?String(o):Array.isArray(o)?"array":typeof o=="object"?"object":"unknown",tp=hM;function dM(o,{removeAlphaIfOpaque:l=!1}={}){const d=(o.a*255|256).toString(16).slice(1),y=(o.r*255|256).toString(16).slice(1)+(o.g*255|256).toString(16).slice(1)+(o.b*255|256).toString(16).slice(1)+(l&&d==="ff"?"":d);return"#".concat(y)}function eu(o){return x(g({},o),{toString(){return dM(this,{removeAlphaIfOpaque:!0})}})}function fM(o){return Object.fromEntries(Object.entries(o).map(([l,d])=>[l,ef(d,0,1)]))}function pM(o){function l(d){return d>=.0031308?1.055*d**(1/2.4)-.055:12.92*d}return fM({r:l(o.r),g:l(o.g),b:l(o.b),a:o.a})}function np(o){function l(d){return d>=.04045?((d+.055)/(1+.055))**2.4:d/12.92}return{r:l(o.r),g:l(o.g),b:l(o.b),a:o.a}}function ip(o){let l=.4122214708*o.r+.5363325363*o.g+.0514459929*o.b,d=.2119034982*o.r+.6806995451*o.g+.1073969566*o.b,y=.0883024619*o.r+.2817188376*o.g+.6299787005*o.b,T=Math.cbrt(l),C=Math.cbrt(d),B=Math.cbrt(y);return{L:.2104542553*T+.793617785*C-.0040720468*B,a:1.9779984951*T-2.428592205*C+.4505937099*B,b:.0259040371*T+.7827717662*C-.808675766*B,alpha:o.a}}function mM(o){let l=o.L+.3963377774*o.a+.2158037573*o.b,d=o.L-.1055613458*o.a-.0638541728*o.b,y=o.L-.0894841775*o.a-1.291485548*o.b,T=l*l*l,C=d*d*d,B=y*y*y;return{r:4.0767416621*T-3.3077115913*C+.2309699292*B,g:-1.2684380046*T+2.6097574011*C-.3413193965*B,b:-.0041960863*T-.7034186147*C+1.707614701*B,a:o.alpha}}var Ci=Symbol("TheatrePropType_Basic");function rp(o){return typeof o=="object"&&!!o&&o[Ci]==="TheatrePropType"}function gM(o){if(typeof o=="number")return sp(o);if(typeof o=="boolean")return op(o);if(typeof o=="string")return ap(o);if(typeof o=="object"&&o){if(rp(o))return o;if(Lv(o))return tu(o);throw new wo("This value is not a valid prop type: ".concat(tp(o)))}else throw new wo("This value is not a valid prop type: ".concat(tp(o)))}function _M(o){const l={};for(const d of Object.keys(o)){const y=o[d];rp(y)?l[d]=y:l[d]=gM(y)}return l}var tu=(o,l={})=>{const d=_M(o),y=new WeakMap;return{type:"compound",props:d,valueType:null,[Ci]:"TheatrePropType",label:l.label,default:sS(d,C=>C.default),deserializeAndSanitize:C=>{if(typeof C!="object"||!C)return;if(y.has(C))return y.get(C);const B={};let q=!1;for(const[K,se]of Object.entries(d))if(Object.prototype.hasOwnProperty.call(C,K)){const ve=se.deserializeAndSanitize(C[K]);ve!=null&&(q=!0,B[K]=ve)}if(y.set(C,B),q)return B}}},vM=(o,l={})=>{const d=(y,T,C)=>{var B;return{type:"file",id:((B=l.interpolate)!=null?B:Po)(y.id,T.id,C)}};return{type:"file",default:{type:"file",id:o},valueType:null,[Ci]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:yM}},yM=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="file"&&(l=!1),!!l)return o},xM=(o,l={})=>{const d=(y,T,C)=>{var B;return{type:"image",id:((B=l.interpolate)!=null?B:Po)(y.id,T.id,C)}};return{type:"image",default:{type:"image",id:o},valueType:null,[Ci]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:bM}},bM=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="image"&&(l=!1),!!l)return o},sp=(o,l={})=>{var d;return x(g({type:"number",valueType:0,default:o,[Ci]:"TheatrePropType"},l||{}),{label:l.label,nudgeFn:(d=l.nudgeFn)!=null?d:IM,nudgeMultiplier:typeof l.nudgeMultiplier=="number"?l.nudgeMultiplier:void 0,interpolate:TM,deserializeAndSanitize:SM(l.range)})},SM=o=>o?l=>{if(typeof l=="number"&&isFinite(l))return ef(l,o[0],o[1])}:MM,MM=o=>typeof o=="number"&&isFinite(o)?o:void 0,TM=(o,l,d)=>o+d*(l-o),EM=(o={r:0,g:0,b:0,a:1},l={})=>{const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return{type:"rgba",valueType:null,default:eu(d),[Ci]:"TheatrePropType",label:l.label,interpolate:wM,deserializeAndSanitize:AM}},AM=o=>{if(!o)return;let l=!0;for(const y of["r","g","b","a"])(!Object.prototype.hasOwnProperty.call(o,y)||typeof o[y]!="number")&&(l=!1);if(!l)return;const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return eu(d)},wM=(o,l,d)=>{const y=ip(np(o)),T=ip(np(l)),C={L:(1-d)*y.L+d*T.L,a:(1-d)*y.a+d*T.a,b:(1-d)*y.b+d*T.b,alpha:(1-d)*y.alpha+d*T.alpha},B=pM(mM(C));return eu(B)},op=(o,l={})=>{var d;return{type:"boolean",default:o,valueType:null,[Ci]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:PM}},PM=o=>typeof o=="boolean"?o:void 0;function Po(o){return o}var ap=(o,l={})=>{var d;return{type:"string",default:o,valueType:null,[Ci]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:RM}};function RM(o){return typeof o=="string"?o:void 0}function CM(o,l,d={}){var y,T;return{type:"stringLiteral",default:o,valuesAndLabels:g({},l),[Ci]:"TheatrePropType",valueType:null,as:(y=d.as)!=null?y:"menu",label:d.label,interpolate:(T=d.interpolate)!=null?T:Po,deserializeAndSanitize(C){if(typeof C=="string"&&Object.prototype.hasOwnProperty.call(l,C))return C}}}var IM=({config:o,deltaX:l,deltaFraction:d,magnitude:y})=>{var T;const{range:C}=o;return!o.nudgeMultiplier&&C&&!C.includes(1/0)&&!C.includes(-1/0)?d*(C[1]-C[0])*y:l*y*((T=o.nudgeMultiplier)!=null?T:1)},LM=o=>o.replace(/^[\s\/]*/,"").replace(/[\s\/]*$/,"").replace(/\s*\/\s*/g," / ");function Fa(o,l){return LM(o)}A(z());var DM=class{get type(){return"Theatre_Sheet_PublicAPI"}constructor(o){le(this,o)}object(o,l,d){const y=$(this),T=Fa(o),C=y.getObject(T),B=null,q=d==null?void 0:d.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;if(C)return q&&C.template._temp_setActions(q),C.publicApi;{const K=tu(l);return y.createObject(T,B,K,q).publicApi}}__experimental_getExistingObject(o){const l=$(this),d=Fa(o),y=l.getObject(d);return y==null?void 0:y.publicApi}get sequence(){return $(this).getSequence().publicApi}get project(){return $(this).project.publicApi}get address(){return g({},$(this).address)}detachObject(o){const l=$(this),d=Fa(o);if(!l.getObject(d)){Ss.warning(`Couldn't delete object "`.concat(d,'"'),'There is no object with key "'.concat(d,`".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(d,'")` with the correct key.')),console.warn('Object key "'.concat(d,'" does not exist.'));return}l.deleteObject(d)}},Ro=nn(),NM=class{constructor(o,l){this.template=o,this.instanceId=l,S(this,"_objects",new Ro.Atom({})),S(this,"_sequence"),S(this,"address"),S(this,"publicApi"),S(this,"project"),S(this,"objectsP",this._objects.pointer),S(this,"type","Theatre_Sheet"),S(this,"_logger"),this._logger=o.project._logger.named("Sheet",l),this._logger._trace("creating sheet"),this.project=o.project,this.address=x(g({},o.address),{sheetInstanceId:this.instanceId}),this.publicApi=new DM(this)}createObject(o,l,d,y={}){const C=this.template.getObjectTemplate(o,l,d,y).createInstance(this,l,d);return this._objects.setByPointer(B=>B[o],C),C}getObject(o){return this._objects.get()[o]}deleteObject(o){this._objects.reduce(l=>{const d=g({},l);return delete d[o],d})}getSequence(){if(!this._sequence){const o=(0,Ro.prism)(()=>{const d=(0,Ro.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length);return OM(d)}),l=(0,Ro.prism)(()=>{const d=(0,Ro.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit);return UM(d)});this._sequence=new lM(this.template.project,this,o,l)}return this._sequence}},OM=o=>typeof o=="number"&&isFinite(o)&&o>0?o:10,UM=o=>typeof o=="number"&&iS(o)&&o>=1&&o<=1e3?o:30,FM=class{constructor(o,l){this.project=o,S(this,"type","Theatre_SheetTemplate"),S(this,"address"),S(this,"_instances",new Kf.Atom({})),S(this,"instancesP",this._instances.pointer),S(this,"_objectTemplates",new Kf.Atom({})),S(this,"objectTemplatesP",this._objectTemplates.pointer),this.address=x(g({},o.address),{sheetId:l})}getInstance(o){let l=this._instances.get()[o];return l||(l=new NM(this,o),this._instances.setByPointer(d=>d[o],l)),l}getObjectTemplate(o,l,d,y){let T=this._objectTemplates.get()[o];return T||(T=new GS(this,o,l,d,y),this._objectTemplates.setByPointer(C=>C[o],T)),T}},nu=nn(),cp=nn(),BM=o=>new Promise(l=>setTimeout(l,o)),kM=BM;function Qn(o){for(var l=arguments.length,d=Array(l>1?l-1:0),y=1;y<l;y++)d[y-1]=arguments[y];throw Error("[Immer] minified error nr: "+o+(d.length?" "+d.map(function(T){return"'"+T+"'"}).join(","):"")+". Find the full error at: https://bit.ly/3cXEKWf")}function Nr(o){return!!o&&!!o[Nn]}function Or(o){return!!o&&((function(l){if(!l||typeof l!="object")return!1;var d=Object.getPrototypeOf(l);if(d===null)return!0;var y=Object.hasOwnProperty.call(d,"constructor")&&d.constructor;return y===Object||typeof y=="function"&&Function.toString.call(y)===YM})(o)||Array.isArray(o)||!!o[vp]||!!o.constructor[vp]||ru(o)||su(o))}function zM(o){return Nr(o)||Qn(23,o),o[Nn].t}function Co(o,l,d){d===void 0&&(d=!1),Ts(o)===0?(d?Object.keys:_u)(o).forEach(function(y){d&&typeof y=="symbol"||l(y,o[y],o)}):o.forEach(function(y,T){return l(T,y,o)})}function Ts(o){var l=o[Nn];return l?l.i>3?l.i-4:l.i:Array.isArray(o)?1:ru(o)?2:su(o)?3:0}function iu(o,l){return Ts(o)===2?o.has(l):Object.prototype.hasOwnProperty.call(o,l)}function HM(o,l){return Ts(o)===2?o.get(l):o[l]}function lp(o,l,d){var y=Ts(o);y===2?o.set(l,d):y===3?(o.delete(l),o.add(d)):o[l]=d}function VM(o,l){return o===l?o!==0||1/o==1/l:o!=o&&l!=l}function ru(o){return XM&&o instanceof Map}function su(o){return qM&&o instanceof Set}function Ur(o){return o.o||o.t}function ou(o){if(Array.isArray(o))return Array.prototype.slice.call(o);var l=KM(o);delete l[Nn];for(var d=_u(l),y=0;y<d.length;y++){var T=d[y],C=l[T];C.writable===!1&&(C.writable=!0,C.configurable=!0),(C.get||C.set)&&(l[T]={configurable:!0,writable:!0,enumerable:C.enumerable,value:o[T]})}return Object.create(Object.getPrototypeOf(o),l)}function au(o,l){return l===void 0&&(l=!1),cu(o)||Nr(o)||!Or(o)||(Ts(o)>1&&(o.set=o.add=o.clear=o.delete=GM),Object.freeze(o),l&&Co(o,function(d,y){return au(y,!0)},!0)),o}function GM(){Qn(2)}function cu(o){return o==null||typeof o!="object"||Object.isFrozen(o)}function Ii(o){var l=ZM[o];return l||Qn(18,o),l}function up(){return Io}function lu(o,l){l&&(Ii("Patches"),o.u=[],o.s=[],o.v=l)}function Ba(o){uu(o),o.p.forEach(WM),o.p=null}function uu(o){o===Io&&(Io=o.l)}function hp(o){return Io={p:[],l:Io,h:o,m:!0,_:0}}function WM(o){var l=o[Nn];l.i===0||l.i===1?l.j():l.O=!0}function hu(o,l){l._=l.p.length;var d=l.p[0],y=o!==void 0&&o!==d;return l.h.g||Ii("ES5").S(l,o,y),y?(d[Nn].P&&(Ba(l),Qn(4)),Or(o)&&(o=ka(l,o),l.l||za(l,o)),l.u&&Ii("Patches").M(d[Nn],o,l.u,l.s)):o=ka(l,d,[]),Ba(l),l.u&&l.v(l.u,l.s),o!==_p?o:void 0}function ka(o,l,d){if(cu(l))return l;var y=l[Nn];if(!y)return Co(l,function(C,B){return dp(o,y,l,C,B,d)},!0),l;if(y.A!==o)return l;if(!y.P)return za(o,y.t,!0),y.t;if(!y.I){y.I=!0,y.A._--;var T=y.i===4||y.i===5?y.o=ou(y.k):y.o;Co(y.i===3?new Set(T):T,function(C,B){return dp(o,y,T,C,B,d)}),za(o,T,!1),d&&o.u&&Ii("Patches").R(y,d,o.u,o.s)}return y.o}function dp(o,l,d,y,T,C){if(Nr(T)){var B=ka(o,T,C&&l&&l.i!==3&&!iu(l.D,y)?C.concat(y):void 0);if(lp(d,y,B),!Nr(B))return;o.m=!1}if(Or(T)&&!cu(T)){if(!o.h.F&&o._<1)return;ka(o,T),l&&l.A.l||za(o,T)}}function za(o,l,d){d===void 0&&(d=!1),o.h.F&&o.m&&au(l,d)}function du(o,l){var d=o[Nn];return(d?Ur(d):o)[l]}function fp(o,l){if(l in o)for(var d=Object.getPrototypeOf(o);d;){var y=Object.getOwnPropertyDescriptor(d,l);if(y)return y;d=Object.getPrototypeOf(d)}}function fu(o){o.P||(o.P=!0,o.l&&fu(o.l))}function pu(o){o.o||(o.o=ou(o.t))}function mu(o,l,d){var y=ru(l)?Ii("MapSet").N(l,d):su(l)?Ii("MapSet").T(l,d):o.g?(function(T,C){var B=Array.isArray(T),q={i:B?1:0,A:C?C.A:up(),P:!1,I:!1,D:{},l:C,t:T,k:null,o:null,j:null,C:!1},K=q,se=Ha;B&&(K=[q],se=Va);var ve=Proxy.revocable(K,se),ye=ve.revoke,Ce=ve.proxy;return q.k=Ce,q.j=ye,Ce})(l,d):Ii("ES5").J(l,d);return(d?d.A:up()).p.push(y),y}function jM(o){return Nr(o)||Qn(22,o),(function l(d){if(!Or(d))return d;var y,T=d[Nn],C=Ts(d);if(T){if(!T.P&&(T.i<4||!Ii("ES5").K(T)))return T.t;T.I=!0,y=pp(d,C),T.I=!1}else y=pp(d,C);return Co(y,function(B,q){T&&HM(T.t,B)===q||lp(y,B,l(q))}),C===3?new Set(y):y})(o)}function pp(o,l){switch(l){case 2:return new Map(o);case 3:return Array.from(o)}return ou(o)}var mp,Io,gu=typeof Symbol<"u"&&typeof Symbol("x")=="symbol",XM=typeof Map<"u",qM=typeof Set<"u",gp=typeof Proxy<"u"&&Proxy.revocable!==void 0&&typeof Reflect<"u",_p=gu?Symbol.for("immer-nothing"):((mp={})["immer-nothing"]=!0,mp),vp=gu?Symbol.for("immer-draftable"):"__$immer_draftable",Nn=gu?Symbol.for("immer-state"):"__$immer_state",YM=""+Object.prototype.constructor,_u=typeof Reflect<"u"&&Reflect.ownKeys?Reflect.ownKeys:Object.getOwnPropertySymbols!==void 0?function(o){return Object.getOwnPropertyNames(o).concat(Object.getOwnPropertySymbols(o))}:Object.getOwnPropertyNames,KM=Object.getOwnPropertyDescriptors||function(o){var l={};return _u(o).forEach(function(d){l[d]=Object.getOwnPropertyDescriptor(o,d)}),l},ZM={},Ha={get:function(o,l){if(l===Nn)return o;var d=Ur(o);if(!iu(d,l))return(function(T,C,B){var q,K=fp(C,B);return K?"value"in K?K.value:(q=K.get)===null||q===void 0?void 0:q.call(T.k):void 0})(o,d,l);var y=d[l];return o.I||!Or(y)?y:y===du(o.t,l)?(pu(o),o.o[l]=mu(o.A.h,y,o)):y},has:function(o,l){return l in Ur(o)},ownKeys:function(o){return Reflect.ownKeys(Ur(o))},set:function(o,l,d){var y=fp(Ur(o),l);if(y!=null&&y.set)return y.set.call(o.k,d),!0;if(!o.P){var T=du(Ur(o),l),C=T==null?void 0:T[Nn];if(C&&C.t===d)return o.o[l]=d,o.D[l]=!1,!0;if(VM(d,T)&&(d!==void 0||iu(o.t,l)))return!0;pu(o),fu(o)}return o.o[l]===d&&typeof d!="number"&&(d!==void 0||l in o.o)||(o.o[l]=d,o.D[l]=!0,!0)},deleteProperty:function(o,l){return du(o.t,l)!==void 0||l in o.t?(o.D[l]=!1,pu(o),fu(o)):delete o.D[l],o.o&&delete o.o[l],!0},getOwnPropertyDescriptor:function(o,l){var d=Ur(o),y=Reflect.getOwnPropertyDescriptor(d,l);return y&&{writable:!0,configurable:o.i!==1||l!=="length",enumerable:y.enumerable,value:d[l]}},defineProperty:function(){Qn(11)},getPrototypeOf:function(o){return Object.getPrototypeOf(o.t)},setPrototypeOf:function(){Qn(12)}},Va={};Co(Ha,function(o,l){Va[o]=function(){return arguments[0]=arguments[0][0],l.apply(this,arguments)}}),Va.deleteProperty=function(o,l){return Ha.deleteProperty.call(this,o[0],l)},Va.set=function(o,l,d){return Ha.set.call(this,o[0],l,d,o[0])};var $M=(function(){function o(d){var y=this;this.g=gp,this.F=!0,this.produce=function(T,C,B){if(typeof T=="function"&&typeof C!="function"){var q=C;C=T;var K=y;return function(je){var Be=this;je===void 0&&(je=q);for(var at=arguments.length,mt=Array(at>1?at-1:0),it=1;it<at;it++)mt[it-1]=arguments[it];return K.produce(je,function(Tt){var xn;return(xn=C).call.apply(xn,[Be,Tt].concat(mt))})}}var se;if(typeof C!="function"&&Qn(6),B!==void 0&&typeof B!="function"&&Qn(7),Or(T)){var ve=hp(y),ye=mu(y,T,void 0),Ce=!0;try{se=C(ye),Ce=!1}finally{Ce?Ba(ve):uu(ve)}return typeof Promise<"u"&&se instanceof Promise?se.then(function(je){return lu(ve,B),hu(je,ve)},function(je){throw Ba(ve),je}):(lu(ve,B),hu(se,ve))}if(!T||typeof T!="object")return(se=C(T))===_p?void 0:(se===void 0&&(se=T),y.F&&au(se,!0),se);Qn(21,T)},this.produceWithPatches=function(T,C){return typeof T=="function"?function(K){for(var se=arguments.length,ve=Array(se>1?se-1:0),ye=1;ye<se;ye++)ve[ye-1]=arguments[ye];return y.produceWithPatches(K,function(Ce){return T.apply(void 0,[Ce].concat(ve))})}:[y.produce(T,C,function(K,se){B=K,q=se}),B,q];var B,q},typeof(d==null?void 0:d.useProxies)=="boolean"&&this.setUseProxies(d.useProxies),typeof(d==null?void 0:d.autoFreeze)=="boolean"&&this.setAutoFreeze(d.autoFreeze)}var l=o.prototype;return l.createDraft=function(d){Or(d)||Qn(8),Nr(d)&&(d=jM(d));var y=hp(this),T=mu(this,d,void 0);return T[Nn].C=!0,uu(y),T},l.finishDraft=function(d,y){var T=d&&d[Nn],C=T.A;return lu(C,y),hu(void 0,C)},l.setAutoFreeze=function(d){this.F=d},l.setUseProxies=function(d){d&&!gp&&Qn(20),this.g=d},l.applyPatches=function(d,y){var T;for(T=y.length-1;T>=0;T--){var C=y[T];if(C.path.length===0&&C.op==="replace"){d=C.value;break}}var B=Ii("Patches").$;return Nr(d)?B(d,y):this.produce(d,function(q){return B(q,y.slice(T+1))})},o})(),jn=new $M;jn.produce,jn.produceWithPatches.bind(jn),jn.setAutoFreeze.bind(jn),jn.setUseProxies.bind(jn),jn.applyPatches.bind(jn),jn.createDraft.bind(jn),jn.finishDraft.bind(jn);var JM={currentProjectStateDefinitionVersion:"0.4.0"},vu=JM;async function QM(o,l,d){await kM(0),o.transaction(({drafts:y})=>{var T;const C=l.address.projectId;y.ephemeral.coreByProject[C]={lastExportedObject:null,loadingState:{type:"loading"}},y.ahistoric.coreByProject[C]={ahistoricStuff:""};function B(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]={sheetsById:{},definitionVersion:vu.currentProjectStateDefinitionVersion,revisionHistory:[]}}function q(ye){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]=ye}function K(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"}}function se(ye){y.ephemeral.coreByProject[C].loadingState={type:"browserStateIsNotBasedOnDiskState",onDiskState:ye}}const ve=(T=zM(y.historic))==null?void 0:T.coreByProject[l.address.projectId];ve?d&&ve.revisionHistory.indexOf(d.revisionHistory[0])==-1?se(d):K():d?q(d):B()})}function yp(){}function xp(o){var l,d;const y=(l=o==null?void 0:o.logging)!=null&&l.internal?(d=o.logging.min)!=null?d:256:1/0,T=y<=128,C=y<=512,B=Vf(void 0,{_debug:T?console.debug.bind(console,"_coreLogger(TheatreInternalLogger) debug"):yp,_error:C?console.error.bind(console,"_coreLogger(TheatreInternalLogger) error"):yp});if(o){const{logger:q,logging:K}=o;q&&B.configureLogger(q),K?B.configureLogging(K):B.configureLogging({dev:!1})}return B.getLogger().named("Theatre")}var eT=class{constructor(o,l={},d){this.config=l,this.publicApi=d,S(this,"pointers"),S(this,"_pointerProxies"),S(this,"address"),S(this,"_studioReadyDeferred"),S(this,"_assetStorageReadyDeferred"),S(this,"_readyPromise"),S(this,"_sheetTemplates",new cp.Atom({})),S(this,"sheetTemplatesP",this._sheetTemplates.pointer),S(this,"_studio"),S(this,"assetStorage"),S(this,"type","Theatre_Project"),S(this,"_logger");var y;this._logger=xp({logging:{dev:!0}}).named("Project",o),this._logger.traceDev("creating project"),this.address={projectId:o};const T=new cp.Atom({ahistoric:{ahistoricStuff:""},historic:(y=l.state)!=null?y:{sheetsById:{},definitionVersion:vu.currentProjectStateDefinitionVersion,revisionHistory:[]},ephemeral:{loadingState:{type:"loaded"},lastExportedObject:null}});this._assetStorageReadyDeferred=tr(),this.assetStorage={getAssetUrl:C=>{var B;return"".concat((B=l.assets)==null?void 0:B.baseUrl,"/").concat(C)},createAsset:()=>{throw new Error("Please wait for Project.ready to use assets.")}},this._pointerProxies={historic:new nu.PointerProxy(T.pointer.historic),ahistoric:new nu.PointerProxy(T.pointer.ahistoric),ephemeral:new nu.PointerProxy(T.pointer.ephemeral)},this.pointers={historic:this._pointerProxies.historic.pointer,ahistoric:this._pointerProxies.ahistoric.pointer,ephemeral:this._pointerProxies.ephemeral.pointer},oe.add(o,this),this._studioReadyDeferred=tr(),this._readyPromise=Promise.all([this._studioReadyDeferred.promise,this._assetStorageReadyDeferred.promise]).then(()=>{}),l.state?setTimeout(()=>{this._studio||(this._studioReadyDeferred.resolve(void 0),this._assetStorageReadyDeferred.resolve(void 0),this._logger._trace("ready deferred resolved with no state"))},0):typeof window>"u"?console.error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. ')+"You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"):setTimeout(()=>{if(!this._studio)throw new Error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. This is fine ')+"while you are using @theatre/core along with @theatre/studio. But since @theatre/studio "+'is not loaded, the state of project "'.concat(o,`" will be empty.

`)+`To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`)},1e3)}attachToStudio(o){if(this._studio){if(this._studio!==o)throw new Error("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));console.warn("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));return}this._studio=o,o.initialized.then(async()=>{var l;await QM(o,this,this.config.state),this._pointerProxies.historic.setPointer(o.atomP.historic.coreByProject[this.address.projectId]),this._pointerProxies.ahistoric.setPointer(o.atomP.ahistoric.coreByProject[this.address.projectId]),this._pointerProxies.ephemeral.setPointer(o.atomP.ephemeral.coreByProject[this.address.projectId]),await o.createAssetStorage(this,(l=this.config.assets)==null?void 0:l.baseUrl).then(d=>{this.assetStorage=d,this._assetStorageReadyDeferred.resolve(void 0)}),this._studioReadyDeferred.resolve(void 0)}).catch(l=>{throw console.error(l),l})}get isAttachedToStudio(){return!!this._studio}get ready(){return this._readyPromise}isReady(){return this._studioReadyDeferred.status==="resolved"&&this._assetStorageReadyDeferred.status==="resolved"}getOrCreateSheet(o,l="default"){let d=this._sheetTemplates.get()[o];return d||(d=new FM(this,o),this._sheetTemplates.reduce(y=>x(g({},y),{[o]:d}))),d.getInstance(l)}},tT=class{get type(){return"Theatre_Project_PublicAPI"}constructor(o,l={}){le(this,new eT(o,l,this))}get ready(){return $(this).ready}get isReady(){return $(this).isReady()}get address(){return g({},$(this).address)}getAssetUrl(o){if(!this.isReady){console.error("Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`.");return}return o.id?$(this).assetStorage.getAssetUrl(o.id):void 0}sheet(o,l="default"){const d=Fa(o);return $(this).getOrCreateSheet(d,l).publicApi}};A(z());var bp=nn(),yu=nn();function Sp(o,l={}){const d=oe.get(o);if(d)return d.publicApi;const T=xp().named("Project",o);return l.state?(iT(o,l.state),T._debug("deep validated config.state on disk")):T._debug("no config.state"),new tT(o,l)}var nT=(o,l)=>{if(Array.isArray(l)||l==null||l.definitionVersion!==vu.currentProjectStateDefinitionVersion)throw new wo("Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(o),", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state"))},iT=(o,l)=>{nT(o,l)};function xu(o,l,d){const y=d?$(d).ticker:Qf();if((0,bp.isPointer)(o))return(0,yu.pointerToPrism)(o).onChange(y,l,!0);if((0,yu.isPrism)(o))return o.onChange(y,l,!0);throw new Error("Called onChange(p) where p is neither a pointer nor a prism.")}function Mp(o){if((0,bp.isPointer)(o))return(0,yu.pointerToPrism)(o).getValue();throw new Error("Called val(p) where p is not a pointer.")}var rT=class{constructor(){S(this,"_studio")}get type(){return"Theatre_CoreBundle"}get version(){return"0.7.2"}getBitsForStudio(o,l){if(this._studio)throw new Error("@theatre/core is already attached to @theatre/studio");this._studio=o;const d={projectsP:oe.atom.pointer.projects,privateAPI:$,coreExports:w,getCoreRafDriver:Jf};l(d)}};sT();function sT(){if(typeof window>"u")return;const o=window[$l];if(typeof o<"u")throw typeof o=="object"&&o&&typeof o.version=="string"?new Error(`It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
1. You might have two separate versions of Theatre.js in node_modules.
2. Or this might be a bundling misconfiguration, in case you're using a bundler like Webpack/ESBuild/Rollup.

Note that it **is okay** to import '@theatre/core' multiple times. But those imports should point to the same module.`):new Error("The variable window.".concat($l," seems to be already set by a module other than @theatre/core."));const l=new rT;window[$l]=l;const d=window[QS];d&&d!==null&&d.type==="Theatre_StudioBundle"&&d.registerCoreBundle(l)}/*! Bundled license information:

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
		*/})(Yo,Yo.exports)),Yo.exports}var Kt=UC();let oh=null,id=null;const e_=new Map;function FC(){return oh=Kt.getProject("HumanBody Theatre"),id=oh.sheet("Main"),{project:oh,sheet:id}}function Cd(){return id}function BC(r,e){const t=r.object("Camera",{position:Kt.types.compound({x:Kt.types.number(e.position.x,{range:[-50,50]}),y:Kt.types.number(e.position.y,{range:[-10,20]}),z:Kt.types.number(e.position.z,{range:[-50,50]})}),fov:Kt.types.number(e.fov,{range:[10,120]})});return t.onValuesChange(n=>{e.position.set(n.position.x,n.position.y,n.position.z),e.fov=n.fov,e.updateProjectionMatrix()}),e_.set("Camera",t),t}function bc(r,e,t){const n={position:Kt.types.compound({x:Kt.types.number(t.position.x,{range:[-20,20]}),y:Kt.types.number(t.position.y,{range:[0,20]}),z:Kt.types.number(t.position.z,{range:[-20,20]})}),intensity:Kt.types.number(t.intensity,{range:[0,100]}),color:Kt.types.rgba({r:t.color.r,g:t.color.g,b:t.color.b,a:1})},i=r.object(e,n);return i.onValuesChange(s=>{t.position.set(s.position.x,s.position.y,s.position.z),t.intensity=s.intensity,t.color.setRGB(s.color.r,s.color.g,s.color.b)}),e_.set(e,i),i}function Id(r,e,t){const n=r.object(e,{position:Kt.types.compound({x:Kt.types.number(t.position.x,{range:[-20,20]}),y:Kt.types.number(t.position.y,{range:[-5,10]}),z:Kt.types.number(t.position.z,{range:[-20,20]})}),rotation:Kt.types.compound({x:Kt.types.number(0,{range:[-180,180]}),y:Kt.types.number(0,{range:[-180,180]}),z:Kt.types.number(0,{range:[-180,180]})}),scale:Kt.types.number(1,{range:[.01,10]})});return n.onValuesChange(i=>{t.position.set(i.position.x,i.position.y,i.position.z),t.rotation.set(i.rotation.x*Math.PI/180,i.rotation.y*Math.PI/180,i.rotation.z*Math.PI/180),t.scale.setScalar(i.scale)}),n}function ng(r,e){if(e===BT)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),r;if(e===$h||e===Tg){let t=r.getIndex();if(t===null){const a=[],c=r.getAttribute("position");if(c!==void 0){for(let u=0;u<c.count;u++)a.push(u);r.setIndex(a),t=r.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),r}const n=t.count-2,i=[];if(e===$h)for(let a=1;a<=n;a++)i.push(t.getX(0)),i.push(t.getX(a)),i.push(t.getX(a+1));else for(let a=0;a<n;a++)a%2===0?(i.push(t.getX(a)),i.push(t.getX(a+1)),i.push(t.getX(a+2))):(i.push(t.getX(a+2)),i.push(t.getX(a+1)),i.push(t.getX(a)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const s=r.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),r}class kC extends os{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new WC(t)}),this.register(function(t){return new jC(t)}),this.register(function(t){return new eI(t)}),this.register(function(t){return new tI(t)}),this.register(function(t){return new nI(t)}),this.register(function(t){return new qC(t)}),this.register(function(t){return new YC(t)}),this.register(function(t){return new KC(t)}),this.register(function(t){return new ZC(t)}),this.register(function(t){return new GC(t)}),this.register(function(t){return new $C(t)}),this.register(function(t){return new XC(t)}),this.register(function(t){return new QC(t)}),this.register(function(t){return new JC(t)}),this.register(function(t){return new HC(t)}),this.register(function(t){return new iI(t)}),this.register(function(t){return new rI(t)})}load(e,t,n,i){const s=this;let a;if(this.resourcePath!=="")a=this.resourcePath;else if(this.path!==""){const h=$o.extractUrlBase(e);a=$o.resolveURL(h,this.path)}else a=$o.extractUrlBase(e);this.manager.itemStart(e);const c=function(h){i?i(h):console.error(h),s.manager.itemError(e),s.manager.itemEnd(e)},u=new Ed(this.manager);u.setPath(this.path),u.setResponseType("arraybuffer"),u.setRequestHeader(this.requestHeader),u.setWithCredentials(this.withCredentials),u.load(e,function(h){try{s.parse(h,a,function(f){t(f),s.manager.itemEnd(e)},c)}catch(f){c(f)}},n,c)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s;const a={},c={},u=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(u.decode(new Uint8Array(e,0,4))===t_){try{a[_t.KHR_BINARY_GLTF]=new sI(e)}catch(p){i&&i(p);return}s=JSON.parse(a[_t.KHR_BINARY_GLTF].content)}else s=JSON.parse(u.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const h=new vI(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});h.fileLoader.setRequestHeader(this.requestHeader);for(let f=0;f<this.pluginCallbacks.length;f++){const p=this.pluginCallbacks[f](h);p.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),c[p.name]=p,a[p.name]=!0}if(s.extensionsUsed)for(let f=0;f<s.extensionsUsed.length;++f){const p=s.extensionsUsed[f],m=s.extensionsRequired||[];switch(p){case _t.KHR_MATERIALS_UNLIT:a[p]=new VC;break;case _t.KHR_DRACO_MESH_COMPRESSION:a[p]=new oI(s,this.dracoLoader);break;case _t.KHR_TEXTURE_TRANSFORM:a[p]=new aI;break;case _t.KHR_MESH_QUANTIZATION:a[p]=new cI;break;default:m.indexOf(p)>=0&&c[p]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+p+'".')}}h.setExtensions(a),h.setPlugins(c),h.parse(n,i)}parseAsync(e,t){const n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}}function zC(){let r={};return{get:function(e){return r[e]},add:function(e,t){r[e]=t},remove:function(e){delete r[e]},removeAll:function(){r={}}}}const _t={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class HC{constructor(e){this.parser=e,this.name=_t.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){const s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let i=t.cache.get(n);if(i)return i;const s=t.json,u=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e];let h;const f=new Ke(16777215);u.color!==void 0&&f.setRGB(u.color[0],u.color[1],u.color[2],Ln);const p=u.range!==void 0?u.range:0;switch(u.type){case"directional":h=new YR(f),h.target.position.set(0,0,-1),h.add(h.target);break;case"point":h=new Kg(f),h.distance=p;break;case"spot":h=new Rc(f),h.distance=p,u.spot=u.spot||{},u.spot.innerConeAngle=u.spot.innerConeAngle!==void 0?u.spot.innerConeAngle:0,u.spot.outerConeAngle=u.spot.outerConeAngle!==void 0?u.spot.outerConeAngle:Math.PI/4,h.angle=u.spot.outerConeAngle,h.penumbra=1-u.spot.innerConeAngle/u.spot.outerConeAngle,h.target.position.set(0,0,-1),h.add(h.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+u.type)}return h.position.set(0,0,0),h.decay=2,Hi(h,u),u.intensity!==void 0&&(h.intensity=u.intensity),h.name=t.createUniqueName(u.name||"light_"+e),i=Promise.resolve(h),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,s=n.json.nodes[e],c=(s.extensions&&s.extensions[this.name]||{}).light;return c===void 0?null:this._loadLight(c).then(function(u){return n._getNodeRef(t.cache,c,u)})}}class VC{constructor(){this.name=_t.KHR_MATERIALS_UNLIT}getMaterialType(){return ii}extendParams(e,t,n){const i=[];e.color=new Ke(1,1,1),e.opacity=1;const s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){const a=s.baseColorFactor;e.color.setRGB(a[0],a[1],a[2],Ln),e.opacity=a[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,dn))}return Promise.all(i)}}class GC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}}class WC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];if(a.clearcoatFactor!==void 0&&(t.clearcoat=a.clearcoatFactor),a.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",a.clearcoatTexture)),a.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=a.clearcoatRoughnessFactor),a.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",a.clearcoatRoughnessTexture)),a.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",a.clearcoatNormalTexture)),a.clearcoatNormalTexture.scale!==void 0)){const c=a.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new Qe(c,c)}return Promise.all(s)}}class jC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.dispersion=s.dispersion!==void 0?s.dispersion:0,Promise.resolve()}}class XC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.iridescenceFactor!==void 0&&(t.iridescence=a.iridescenceFactor),a.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",a.iridescenceTexture)),a.iridescenceIor!==void 0&&(t.iridescenceIOR=a.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),a.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=a.iridescenceThicknessMinimum),a.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=a.iridescenceThicknessMaximum),a.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",a.iridescenceThicknessTexture)),Promise.all(s)}}class qC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[];t.sheenColor=new Ke(0,0,0),t.sheenRoughness=0,t.sheen=1;const a=i.extensions[this.name];if(a.sheenColorFactor!==void 0){const c=a.sheenColorFactor;t.sheenColor.setRGB(c[0],c[1],c[2],Ln)}return a.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=a.sheenRoughnessFactor),a.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",a.sheenColorTexture,dn)),a.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",a.sheenRoughnessTexture)),Promise.all(s)}}class YC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.transmissionFactor!==void 0&&(t.transmission=a.transmissionFactor),a.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",a.transmissionTexture)),Promise.all(s)}}class KC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.thickness=a.thicknessFactor!==void 0?a.thicknessFactor:0,a.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",a.thicknessTexture)),t.attenuationDistance=a.attenuationDistance||1/0;const c=a.attenuationColor||[1,1,1];return t.attenuationColor=new Ke().setRGB(c[0],c[1],c[2],Ln),Promise.all(s)}}class ZC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}}class $C{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.specularIntensity=a.specularFactor!==void 0?a.specularFactor:1,a.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",a.specularTexture));const c=a.specularColorFactor||[1,1,1];return t.specularColor=new Ke().setRGB(c[0],c[1],c[2],Ln),a.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",a.specularColorTexture,dn)),Promise.all(s)}}class JC{constructor(e){this.parser=e,this.name=_t.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return t.bumpScale=a.bumpFactor!==void 0?a.bumpFactor:1,a.bumpTexture!==void 0&&s.push(n.assignTexture(t,"bumpMap",a.bumpTexture)),Promise.all(s)}}class QC{constructor(e){this.parser=e,this.name=_t.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Si}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.anisotropyStrength!==void 0&&(t.anisotropy=a.anisotropyStrength),a.anisotropyRotation!==void 0&&(t.anisotropyRotation=a.anisotropyRotation),a.anisotropyTexture!==void 0&&s.push(n.assignTexture(t,"anisotropyMap",a.anisotropyTexture)),Promise.all(s)}}class eI{constructor(e){this.parser=e,this.name=_t.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;const s=i.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,a)}}class tI{constructor(e){this.parser=e,this.name=_t.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class nI{constructor(e){this.parser=e,this.name=_t.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class iI{constructor(e){this.name=_t.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),a=this.parser.options.meshoptDecoder;if(!a||!a.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(c){const u=i.byteOffset||0,h=i.byteLength||0,f=i.count,p=i.byteStride,m=new Uint8Array(c,u,h);return a.decodeGltfBufferAsync?a.decodeGltfBufferAsync(f,p,m,i.mode,i.filter).then(function(g){return g.buffer}):a.ready.then(function(){const g=new ArrayBuffer(f*p);return a.decodeGltfBuffer(new Uint8Array(g),f,p,m,i.mode,i.filter),g})})}else return null}}class rI{constructor(e){this.name=_t.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const i=t.meshes[n.mesh];for(const h of i.primitives)if(h.mode!==ti.TRIANGLES&&h.mode!==ti.TRIANGLE_STRIP&&h.mode!==ti.TRIANGLE_FAN&&h.mode!==void 0)return null;const a=n.extensions[this.name].attributes,c=[],u={};for(const h in a)c.push(this.parser.getDependency("accessor",a[h]).then(f=>(u[h]=f,u[h])));return c.length<1?null:(c.push(this.parser.createNodeMesh(e)),Promise.all(c).then(h=>{const f=h.pop(),p=f.isGroup?f.children:[f],m=h[0].count,g=[];for(const x of p){const M=new nt,v=new F,_=new Wt,A=new F(1,1,1),P=new CR(x.geometry,x.material,m);for(let S=0;S<m;S++)u.TRANSLATION&&v.fromBufferAttribute(u.TRANSLATION,S),u.ROTATION&&_.fromBufferAttribute(u.ROTATION,S),u.SCALE&&A.fromBufferAttribute(u.SCALE,S),P.setMatrixAt(S,M.compose(v,_,A));for(const S in u)if(S==="_COLOR_0"){const k=u[S];P.instanceColor=new ed(k.array,k.itemSize,k.normalized)}else S!=="TRANSLATION"&&S!=="ROTATION"&&S!=="SCALE"&&x.geometry.setAttribute(S,u[S]);Ht.prototype.copy.call(P,x),this.parser.assignFinalMaterial(P),g.push(P)}return f.isGroup?(f.clear(),f.add(...g),f):g[0]}))}}const t_="glTF",Vo=12,ig={JSON:1313821514,BIN:5130562};class sI{constructor(e){this.name=_t.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Vo),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==t_)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const i=this.header.length-Vo,s=new DataView(e,Vo);let a=0;for(;a<i;){const c=s.getUint32(a,!0);a+=4;const u=s.getUint32(a,!0);if(a+=4,u===ig.JSON){const h=new Uint8Array(e,Vo+a,c);this.content=n.decode(h)}else if(u===ig.BIN){const h=Vo+a;this.body=e.slice(h,h+c)}a+=c}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class oI{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=_t.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,c={},u={},h={};for(const f in a){const p=rd[f]||f.toLowerCase();c[p]=a[f]}for(const f in e.attributes){const p=rd[f]||f.toLowerCase();if(a[f]!==void 0){const m=n.accessors[e.attributes[f]],g=Ks[m.componentType];h[p]=g.name,u[p]=m.normalized===!0}}return t.getDependency("bufferView",s).then(function(f){return new Promise(function(p,m){i.decodeDracoFile(f,function(g){for(const x in g.attributes){const M=g.attributes[x],v=u[x];v!==void 0&&(M.normalized=v)}p(g)},c,h,Ln,m)})})}}class aI{constructor(){this.name=_t.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class cI{constructor(){this.name=_t.KHR_MESH_QUANTIZATION}}class n_ extends ra{constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let a=0;a!==i;a++)t[a]=n[s+a];return t}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=c*2,h=c*3,f=i-t,p=(n-t)/f,m=p*p,g=m*p,x=e*h,M=x-h,v=-2*g+3*m,_=g-m,A=1-v,P=_-m+p;for(let S=0;S!==c;S++){const k=a[M+S+c],O=a[M+S+u]*f,U=a[x+S+c],z=a[x+S]*f;s[S]=A*k+P*O+v*U+_*z}return s}}const lI=new Wt;class uI extends n_{interpolate_(e,t,n,i){const s=super.interpolate_(e,t,n,i);return lI.fromArray(s).normalize().toArray(s),s}}const ti={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},Ks={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},rg={9728:In,9729:Zn,9984:fg,9985:Sc,9986:Go,9987:Vi},sg={33071:fr,33648:Ic,10497:Qs},ah={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},rd={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},ur={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},hI={CUBICSPLINE:void 0,LINEAR:ea,STEP:Qo},ch={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function dI(r){return r.DefaultMaterial===void 0&&(r.DefaultMaterial=new is({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:Xi})),r.DefaultMaterial}function Kr(r,e,t){for(const n in t.extensions)r[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function Hi(r,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(r.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function fI(r,e,t){let n=!1,i=!1,s=!1;for(let h=0,f=e.length;h<f;h++){const p=e[h];if(p.POSITION!==void 0&&(n=!0),p.NORMAL!==void 0&&(i=!0),p.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(r);const a=[],c=[],u=[];for(let h=0,f=e.length;h<f;h++){const p=e[h];if(n){const m=p.POSITION!==void 0?t.getDependency("accessor",p.POSITION):r.attributes.position;a.push(m)}if(i){const m=p.NORMAL!==void 0?t.getDependency("accessor",p.NORMAL):r.attributes.normal;c.push(m)}if(s){const m=p.COLOR_0!==void 0?t.getDependency("accessor",p.COLOR_0):r.attributes.color;u.push(m)}}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u)]).then(function(h){const f=h[0],p=h[1],m=h[2];return n&&(r.morphAttributes.position=f),i&&(r.morphAttributes.normal=p),s&&(r.morphAttributes.color=m),r.morphTargetsRelative=!0,r})}function pI(r,e){if(r.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)r.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(r.morphTargetInfluences.length===t.length){r.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)r.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function mI(r){let e;const t=r.extensions&&r.extensions[_t.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+lh(t.attributes):e=r.indices+":"+lh(r.attributes)+":"+r.mode,r.targets!==void 0)for(let n=0,i=r.targets.length;n<i;n++)e+=":"+lh(r.targets[n]);return e}function lh(r){let e="";const t=Object.keys(r).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+r[t[n]]+";";return e}function sd(r){switch(r){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function gI(r){return r.search(/\.jpe?g($|\?)/i)>0||r.search(/^data\:image\/jpeg/)===0?"image/jpeg":r.search(/\.webp($|\?)/i)>0||r.search(/^data\:image\/webp/)===0?"image/webp":r.search(/\.ktx2($|\?)/i)>0||r.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const _I=new nt;class vI{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new zC,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=-1,s=!1,a=-1;if(typeof navigator<"u"){const c=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(c)===!0;const u=c.match(/Version\/(\d+)/);i=n&&u?parseInt(u[1],10):-1,s=c.indexOf("Firefox")>-1,a=s?c.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&i<17||s&&a<98?this.textureLoader=new WR(this.options.manager):this.textureLoader=new ZR(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Ed(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(a){return a._markDefs&&a._markDefs()}),Promise.all(this._invokeAll(function(a){return a.beforeRoot&&a.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(a){const c={scene:a[0][i.scene||0],scenes:a[0],animations:a[1],cameras:a[2],asset:i.asset,parser:n,userData:{}};return Kr(s,c,i),Hi(c,i),Promise.all(n._invokeAll(function(u){return u.afterRoot&&u.afterRoot(c)})).then(function(){for(const u of c.scenes)u.updateMatrixWorld();e(c)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){const a=t[i].joints;for(let c=0,u=a.length;c<u;c++)e[a[c]].isBone=!0}for(let i=0,s=e.length;i<s;i++){const a=e[i];a.mesh!==void 0&&(this._addNodeRef(this.meshCache,a.mesh),a.skin!==void 0&&(n[a.mesh].isSkinnedMesh=!0)),a.camera!==void 0&&this._addNodeRef(this.cameraCache,a.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const i=n.clone(),s=(a,c)=>{const u=this.associations.get(a);u!=null&&this.associations.set(c,u);for(const[h,f]of a.children.entries())s(f,c.children[h])};return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const i=e(t[n]);if(i)return i}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let i=0;i<t.length;i++){const s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){const n=e+":"+t;let i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,a){return n.getDependency(e,a)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[_t.KHR_BINARY_GLTF].body);const i=this.options;return new Promise(function(s,a){n.load($o.resolveURL(t.uri,i.path),s,void 0,function(){a(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){const t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){const a=ah[i.type],c=Ks[i.componentType],u=i.normalized===!0,h=new c(i.count*a);return Promise.resolve(new Qt(h,a,u))}const s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(a){const c=a[0],u=ah[i.type],h=Ks[i.componentType],f=h.BYTES_PER_ELEMENT,p=f*u,m=i.byteOffset||0,g=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,x=i.normalized===!0;let M,v;if(g&&g!==p){const _=Math.floor(m/g),A="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count;let P=t.cache.get(A);P||(M=new h(c,_*g,i.count*g/f),P=new ER(M,g/f),t.cache.add(A,P)),v=new bd(P,u,m%g/f,x)}else c===null?M=new h(i.count*u):M=new h(c,m,i.count*u),v=new Qt(M,u,x);if(i.sparse!==void 0){const _=ah.SCALAR,A=Ks[i.sparse.indices.componentType],P=i.sparse.indices.byteOffset||0,S=i.sparse.values.byteOffset||0,k=new A(a[1],P,i.sparse.count*_),O=new h(a[2],S,i.sparse.count*u);c!==null&&(v=new Qt(v.array.slice(),v.itemSize,v.normalized)),v.normalized=!1;for(let U=0,z=k.length;U<z;U++){const I=k[U];if(v.setX(I,O[U*u]),u>=2&&v.setY(I,O[U*u+1]),u>=3&&v.setZ(I,O[U*u+2]),u>=4&&v.setW(I,O[U*u+3]),u>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}v.normalized=x}return v})}loadTexture(e){const t=this.json,n=this.options,s=t.textures[e].source,a=t.images[s];let c=this.textureLoader;if(a.uri){const u=n.manager.getHandler(a.uri);u!==null&&(c=u)}return this.loadTextureImage(e,s,c)}loadTextureImage(e,t,n){const i=this,s=this.json,a=s.textures[e],c=s.images[t],u=(c.uri||c.bufferView)+":"+a.sampler;if(this.textureCache[u])return this.textureCache[u];const h=this.loadImageSource(t,n).then(function(f){f.flipY=!1,f.name=a.name||c.name||"",f.name===""&&typeof c.uri=="string"&&c.uri.startsWith("data:image/")===!1&&(f.name=c.uri);const m=(s.samplers||{})[a.sampler]||{};return f.magFilter=rg[m.magFilter]||Zn,f.minFilter=rg[m.minFilter]||Vi,f.wrapS=sg[m.wrapS]||Qs,f.wrapT=sg[m.wrapT]||Qs,f.generateMipmaps=!f.isCompressedTexture&&f.minFilter!==In&&f.minFilter!==Zn,i.associations.set(f,{textures:e}),f}).catch(function(){return null});return this.textureCache[u]=h,h}loadImageSource(e,t){const n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(p=>p.clone());const a=i.images[e],c=self.URL||self.webkitURL;let u=a.uri||"",h=!1;if(a.bufferView!==void 0)u=n.getDependency("bufferView",a.bufferView).then(function(p){h=!0;const m=new Blob([p],{type:a.mimeType});return u=c.createObjectURL(m),u});else if(a.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const f=Promise.resolve(u).then(function(p){return new Promise(function(m,g){let x=m;t.isImageBitmapLoader===!0&&(x=function(M){const v=new fn(M);v.needsUpdate=!0,m(v)}),t.load($o.resolveURL(p,s.path),x,void 0,g)})}).then(function(p){return h===!0&&c.revokeObjectURL(u),Hi(p,a),p.userData.mimeType=a.mimeType||gI(a.uri),p}).catch(function(p){throw console.error("THREE.GLTFLoader: Couldn't load texture",u),p});return this.sourceCache[e]=f,f}assignTexture(e,t,n,i){const s=this;return this.getDependency("texture",n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),s.extensions[_t.KHR_TEXTURE_TRANSFORM]){const c=n.extensions!==void 0?n.extensions[_t.KHR_TEXTURE_TRANSFORM]:void 0;if(c){const u=s.associations.get(a);a=s.extensions[_t.KHR_TEXTURE_TRANSFORM].extendTexture(a,c),s.associations.set(a,u)}}return i!==void 0&&(a.colorSpace=i),e[t]=a,a})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){const c="PointsMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new jg,xi.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,u.sizeAttenuation=!1,this.cache.add(c,u)),n=u}else if(e.isLine){const c="LineBasicMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Hc,xi.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,this.cache.add(c,u)),n=u}if(i||s||a){let c="ClonedMaterial:"+n.uuid+":";i&&(c+="derivative-tangents:"),s&&(c+="vertex-colors:"),a&&(c+="flat-shading:");let u=this.cache.get(c);u||(u=n.clone(),s&&(u.vertexColors=!0),a&&(u.flatShading=!0),i&&(u.normalScale&&(u.normalScale.y*=-1),u.clearcoatNormalScale&&(u.clearcoatNormalScale.y*=-1)),this.cache.add(c,u),this.associations.set(u,this.associations.get(n))),n=u}e.material=n}getMaterialType(){return is}loadMaterial(e){const t=this,n=this.json,i=this.extensions,s=n.materials[e];let a;const c={},u=s.extensions||{},h=[];if(u[_t.KHR_MATERIALS_UNLIT]){const p=i[_t.KHR_MATERIALS_UNLIT];a=p.getMaterialType(),h.push(p.extendParams(c,s,t))}else{const p=s.pbrMetallicRoughness||{};if(c.color=new Ke(1,1,1),c.opacity=1,Array.isArray(p.baseColorFactor)){const m=p.baseColorFactor;c.color.setRGB(m[0],m[1],m[2],Ln),c.opacity=m[3]}p.baseColorTexture!==void 0&&h.push(t.assignTexture(c,"map",p.baseColorTexture,dn)),c.metalness=p.metallicFactor!==void 0?p.metallicFactor:1,c.roughness=p.roughnessFactor!==void 0?p.roughnessFactor:1,p.metallicRoughnessTexture!==void 0&&(h.push(t.assignTexture(c,"metalnessMap",p.metallicRoughnessTexture)),h.push(t.assignTexture(c,"roughnessMap",p.metallicRoughnessTexture))),a=this._invokeOne(function(m){return m.getMaterialType&&m.getMaterialType(e)}),h.push(Promise.all(this._invokeAll(function(m){return m.extendMaterialParams&&m.extendMaterialParams(e,c)})))}s.doubleSided===!0&&(c.side=Fn);const f=s.alphaMode||ch.OPAQUE;if(f===ch.BLEND?(c.transparent=!0,c.depthWrite=!1):(c.transparent=!1,f===ch.MASK&&(c.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&a!==ii&&(h.push(t.assignTexture(c,"normalMap",s.normalTexture)),c.normalScale=new Qe(1,1),s.normalTexture.scale!==void 0)){const p=s.normalTexture.scale;c.normalScale.set(p,p)}if(s.occlusionTexture!==void 0&&a!==ii&&(h.push(t.assignTexture(c,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(c.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&a!==ii){const p=s.emissiveFactor;c.emissive=new Ke().setRGB(p[0],p[1],p[2],Ln)}return s.emissiveTexture!==void 0&&a!==ii&&h.push(t.assignTexture(c,"emissiveMap",s.emissiveTexture,dn)),Promise.all(h).then(function(){const p=new a(c);return s.name&&(p.name=s.name),Hi(p,s),t.associations.set(p,{materials:e}),s.extensions&&Kr(i,p,s),p})}createUniqueName(e){const t=Pt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,i=this.primitiveCache;function s(c){return n[_t.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(c,t).then(function(u){return og(u,c,t)})}const a=[];for(let c=0,u=e.length;c<u;c++){const h=e[c],f=mI(h),p=i[f];if(p)a.push(p.promise);else{let m;h.extensions&&h.extensions[_t.KHR_DRACO_MESH_COMPRESSION]?m=s(h):m=og(new sn,h,t),i[f]={primitive:h,promise:m},a.push(m)}}return Promise.all(a)}loadMesh(e){const t=this,n=this.json,i=this.extensions,s=n.meshes[e],a=s.primitives,c=[];for(let u=0,h=a.length;u<h;u++){const f=a[u].material===void 0?dI(this.cache):this.getDependency("material",a[u].material);c.push(f)}return c.push(t.loadGeometries(a)),Promise.all(c).then(function(u){const h=u.slice(0,u.length-1),f=u[u.length-1],p=[];for(let g=0,x=f.length;g<x;g++){const M=f[g],v=a[g];let _;const A=h[g];if(v.mode===ti.TRIANGLES||v.mode===ti.TRIANGLE_STRIP||v.mode===ti.TRIANGLE_FAN||v.mode===void 0)_=s.isSkinnedMesh===!0?new wR(M,A):new we(M,A),_.isSkinnedMesh===!0&&_.normalizeSkinWeights(),v.mode===ti.TRIANGLE_STRIP?_.geometry=ng(_.geometry,Tg):v.mode===ti.TRIANGLE_FAN&&(_.geometry=ng(_.geometry,$h));else if(v.mode===ti.LINES)_=new Wg(M,A);else if(v.mode===ti.LINE_STRIP)_=new li(M,A);else if(v.mode===ti.LINE_LOOP)_=new IR(M,A);else if(v.mode===ti.POINTS)_=new LR(M,A);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+v.mode);Object.keys(_.geometry.morphAttributes).length>0&&pI(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),Hi(_,s),v.extensions&&Kr(i,_,v),t.assignFinalMaterial(_),p.push(_)}for(let g=0,x=p.length;g<x;g++)t.associations.set(p[g],{meshes:e,primitives:g});if(p.length===1)return s.extensions&&Kr(i,p[0],s),p[0];const m=new Wi;s.extensions&&Kr(i,m,s),t.associations.set(m,{meshes:e});for(let g=0,x=p.length;g<x;g++)m.add(p[g]);return m})}loadCamera(e){let t;const n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new Cn(wg.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new vd(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),Hi(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this._loadNodeShallow(t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){const s=i.pop(),a=i,c=[],u=[];for(let h=0,f=a.length;h<f;h++){const p=a[h];if(p){c.push(p);const m=new nt;s!==null&&m.fromArray(s.array,h*16),u.push(m)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[h])}return new zc(c,u)})}loadAnimation(e){const t=this.json,n=this,i=t.animations[e],s=i.name?i.name:"animation_"+e,a=[],c=[],u=[],h=[],f=[];for(let p=0,m=i.channels.length;p<m;p++){const g=i.channels[p],x=i.samplers[g.sampler],M=g.target,v=M.node,_=i.parameters!==void 0?i.parameters[x.input]:x.input,A=i.parameters!==void 0?i.parameters[x.output]:x.output;M.node!==void 0&&(a.push(this.getDependency("node",v)),c.push(this.getDependency("accessor",_)),u.push(this.getDependency("accessor",A)),h.push(x),f.push(M))}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u),Promise.all(h),Promise.all(f)]).then(function(p){const m=p[0],g=p[1],x=p[2],M=p[3],v=p[4],_=[];for(let A=0,P=m.length;A<P;A++){const S=m[A],k=g[A],O=x[A],U=M[A],z=v[A];if(S===void 0)continue;S.updateMatrix&&S.updateMatrix();const I=n._createAnimationTracks(S,k,O,U,z);if(I)for(let w=0;w<I.length;w++)_.push(I[w])}return new Uc(s,void 0,_)})}createNodeMesh(e){const t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){const a=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&a.traverse(function(c){if(c.isMesh)for(let u=0,h=i.weights.length;u<h;u++)c.morphTargetInfluences[u]=i.weights[u]}),a})}loadNode(e){const t=this.json,n=this,i=t.nodes[e],s=n._loadNodeShallow(e),a=[],c=i.children||[];for(let h=0,f=c.length;h<f;h++)a.push(n.getDependency("node",c[h]));const u=i.skin===void 0?Promise.resolve(null):n.getDependency("skin",i.skin);return Promise.all([s,Promise.all(a),u]).then(function(h){const f=h[0],p=h[1],m=h[2];m!==null&&f.traverse(function(g){g.isSkinnedMesh&&g.bind(m,_I)});for(let g=0,x=p.length;g<x;g++)f.add(p[g]);return f})}_loadNodeShallow(e){const t=this.json,n=this.extensions,i=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const s=t.nodes[e],a=s.name?i.createUniqueName(s.name):"",c=[],u=i._invokeOne(function(h){return h.createNodeMesh&&h.createNodeMesh(e)});return u&&c.push(u),s.camera!==void 0&&c.push(i.getDependency("camera",s.camera).then(function(h){return i._getNodeRef(i.cameraCache,s.camera,h)})),i._invokeAll(function(h){return h.createNodeAttachment&&h.createNodeAttachment(e)}).forEach(function(h){c.push(h)}),this.nodeCache[e]=Promise.all(c).then(function(h){let f;if(s.isBone===!0?f=new Sd:h.length>1?f=new Wi:h.length===1?f=h[0]:f=new Ht,f!==h[0])for(let p=0,m=h.length;p<m;p++)f.add(h[p]);if(s.name&&(f.userData.name=s.name,f.name=a),Hi(f,s),s.extensions&&Kr(n,f,s),s.matrix!==void 0){const p=new nt;p.fromArray(s.matrix),f.applyMatrix4(p)}else s.translation!==void 0&&f.position.fromArray(s.translation),s.rotation!==void 0&&f.quaternion.fromArray(s.rotation),s.scale!==void 0&&f.scale.fromArray(s.scale);return i.associations.has(f)||i.associations.set(f,{}),i.associations.get(f).nodes=e,f}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],i=this,s=new Wi;n.name&&(s.name=i.createUniqueName(n.name)),Hi(s,n),n.extensions&&Kr(t,s,n);const a=n.nodes||[],c=[];for(let u=0,h=a.length;u<h;u++)c.push(i.getDependency("node",a[u]));return Promise.all(c).then(function(u){for(let f=0,p=u.length;f<p;f++)s.add(u[f]);const h=f=>{const p=new Map;for(const[m,g]of i.associations)(m instanceof xi||m instanceof fn)&&p.set(m,g);return f.traverse(m=>{const g=i.associations.get(m);g!=null&&p.set(m,g)}),p};return i.associations=h(s),s})}_createAnimationTracks(e,t,n,i,s){const a=[],c=e.name?e.name:e.uuid,u=[];ur[s.path]===ur.weights?e.traverse(function(m){m.morphTargetInfluences&&u.push(m.name?m.name:m.uuid)}):u.push(c);let h;switch(ur[s.path]){case ur.weights:h=ro;break;case ur.rotation:h=rs;break;case ur.position:case ur.scale:h=ss;break;default:switch(n.itemSize){case 1:h=ro;break;case 2:case 3:default:h=ss;break}break}const f=i.interpolation!==void 0?hI[i.interpolation]:ea,p=this._getArrayFromAccessor(n);for(let m=0,g=u.length;m<g;m++){const x=new h(u[m]+"."+ur[s.path],t.array,p,f);i.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(x),a.push(x)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=sd(t.constructor),i=new Float32Array(t.length);for(let s=0,a=t.length;s<a;s++)i[s]=t[s]*n;t=i}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const i=this instanceof rs?uI:n_;return new i(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function yI(r,e,t){const n=e.attributes,i=new Yi;if(n.POSITION!==void 0){const c=t.json.accessors[n.POSITION],u=c.min,h=c.max;if(u!==void 0&&h!==void 0){if(i.set(new F(u[0],u[1],u[2]),new F(h[0],h[1],h[2])),c.normalized){const f=sd(Ks[c.componentType]);i.min.multiplyScalar(f),i.max.multiplyScalar(f)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const s=e.targets;if(s!==void 0){const c=new F,u=new F;for(let h=0,f=s.length;h<f;h++){const p=s[h];if(p.POSITION!==void 0){const m=t.json.accessors[p.POSITION],g=m.min,x=m.max;if(g!==void 0&&x!==void 0){if(u.setX(Math.max(Math.abs(g[0]),Math.abs(x[0]))),u.setY(Math.max(Math.abs(g[1]),Math.abs(x[1]))),u.setZ(Math.max(Math.abs(g[2]),Math.abs(x[2]))),m.normalized){const M=sd(Ks[m.componentType]);u.multiplyScalar(M)}c.max(u)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(c)}r.boundingBox=i;const a=new bi;i.getCenter(a.center),a.radius=i.min.distanceTo(i.max)/2,r.boundingSphere=a}function og(r,e,t){const n=e.attributes,i=[];function s(a,c){return t.getDependency("accessor",a).then(function(u){r.setAttribute(c,u)})}for(const a in n){const c=rd[a]||a.toLowerCase();c in r.attributes||i.push(s(n[a],c))}if(e.indices!==void 0&&!r.index){const a=t.getDependency("accessor",e.indices).then(function(c){r.setIndex(c)});i.push(a)}return bt.workingColorSpace!==Ln&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${bt.workingColorSpace}" not supported.`),Hi(r,e),yI(r,e,t),Promise.all(i).then(function(){return e.targets!==void 0?fI(r,e.targets,t):r})}class xI extends os{constructor(e){super(e),this.animateBonePositions=!0,this.animateBoneRotations=!0}load(e,t,n,i){const s=this,a=new Ed(s.manager);a.setPath(s.path),a.setRequestHeader(s.requestHeader),a.setWithCredentials(s.withCredentials),a.load(e,function(c){try{t(s.parse(c))}catch(u){i?i(u):console.error(u),s.manager.itemError(e)}},n,i)}parse(e){function t(g){c(g)!=="HIERARCHY"&&console.error("THREE.BVHLoader: HIERARCHY expected.");const x=[],M=i(g,c(g),x);c(g)!=="MOTION"&&console.error("THREE.BVHLoader: MOTION expected.");let v=c(g).split(/[\s]+/);const _=parseInt(v[1]);isNaN(_)&&console.error("THREE.BVHLoader: Failed to read number of frames."),v=c(g).split(/[\s]+/);const A=parseFloat(v[2]);isNaN(A)&&console.error("THREE.BVHLoader: Failed to read frame time.");for(let P=0;P<_;P++)v=c(g).split(/[\s]+/),n(v,P*A,M);return x}function n(g,x,M){if(M.type==="ENDSITE")return;const v={time:x,position:new F,rotation:new Wt};M.frames.push(v);const _=new Wt,A=new F(1,0,0),P=new F(0,1,0),S=new F(0,0,1);for(let k=0;k<M.channels.length;k++)switch(M.channels[k]){case"Xposition":v.position.x=parseFloat(g.shift().trim());break;case"Yposition":v.position.y=parseFloat(g.shift().trim());break;case"Zposition":v.position.z=parseFloat(g.shift().trim());break;case"Xrotation":_.setFromAxisAngle(A,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Yrotation":_.setFromAxisAngle(P,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Zrotation":_.setFromAxisAngle(S,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;default:console.warn("THREE.BVHLoader: Invalid channel type.")}for(let k=0;k<M.children.length;k++)n(g,x,M.children[k])}function i(g,x,M){const v={name:"",type:"",frames:[]};M.push(v);let _=x.split(/[\s]+/);_[0].toUpperCase()==="END"&&_[1].toUpperCase()==="SITE"?(v.type="ENDSITE",v.name="ENDSITE"):(v.name=_[1],v.type=_[0].toUpperCase()),c(g)!=="{"&&console.error("THREE.BVHLoader: Expected opening { after type & name"),_=c(g).split(/[\s]+/),_[0]!=="OFFSET"&&console.error("THREE.BVHLoader: Expected OFFSET but got: "+_[0]),_.length!==4&&console.error("THREE.BVHLoader: Invalid number of values for OFFSET.");const A=new F(parseFloat(_[1]),parseFloat(_[2]),parseFloat(_[3]));if((isNaN(A.x)||isNaN(A.y)||isNaN(A.z))&&console.error("THREE.BVHLoader: Invalid values of OFFSET."),v.offset=A,v.type!=="ENDSITE"){_=c(g).split(/[\s]+/),_[0]!=="CHANNELS"&&console.error("THREE.BVHLoader: Expected CHANNELS definition.");const P=parseInt(_[1]);v.channels=_.splice(2,P),v.children=[]}for(;;){const P=c(g);if(P==="}")return v;v.children.push(i(g,P,M))}}function s(g,x){const M=new Sd;if(x.push(M),M.position.add(g.offset),M.name=g.name,g.type!=="ENDSITE")for(let v=0;v<g.children.length;v++)M.add(s(g.children[v],x));return M}function a(g){const x=[];for(let M=0;M<g.length;M++){const v=g[M];if(v.type==="ENDSITE")continue;const _=[],A=[],P=[];for(let S=0;S<v.frames.length;S++){const k=v.frames[S];_.push(k.time),A.push(k.position.x+v.offset.x),A.push(k.position.y+v.offset.y),A.push(k.position.z+v.offset.z),P.push(k.rotation.x),P.push(k.rotation.y),P.push(k.rotation.z),P.push(k.rotation.w)}u.animateBonePositions&&x.push(new ss(v.name+".position",_,A)),u.animateBoneRotations&&x.push(new rs(v.name+".quaternion",_,P))}return new Uc("animation",-1,x)}function c(g){let x;for(;(x=g.shift().trim()).length===0;);return x}const u=this,h=e.split(/[\r\n]+/g),f=t(h),p=[];s(f[0],p);const m=a(f);return{skeleton:new zc(p),clip:m}}}const i_=new kC,bI=new xI;let so=0;async function SI(r,e){return new Promise((t,n)=>{i_.load(r,i=>{const s=i.scene;e.add(s),s.traverse(u=>{u.isMesh&&(u.castShadow=!0,u.receiveShadow=!0)}),so++;const a=`Asset ${so}`,c=Cd();c&&Id(c,a,s),t(s)},void 0,i=>n(i))})}async function MI(r,e){const t=URL.createObjectURL(r);try{return await SI(t,e)}finally{URL.revokeObjectURL(t)}}const TI=[{color:13935988,roughness:.55,metalness:0},{color:13935988,roughness:.55,metalness:0},{color:1118481,roughness:.8,metalness:0},{color:657930,roughness:.1,metalness:0},{color:16052456,roughness:.2,metalness:0},{color:16052456,roughness:.05,metalness:0,opacity:.3,transparent:!0},{color:4881051,roughness:.15,metalness:0},{color:11885162,roughness:.7,metalness:0},{color:15789280,roughness:.3,metalness:0},{color:14723210,roughness:.4,metalness:0},{color:14723210,roughness:.4,metalness:0}];function od(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Float32Array(t.buffer)}function r_(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Uint32Array(t.buffer)}function s_(r){for(let e=0;e<r.length;e+=3){const t=r[e+1],n=r[e+2];r[e+1]=n,r[e+2]=-t}}function EI(r){const e=od(r.vertices),t=r_(r.faces);s_(e);const n=new sn,i=new Qt(e,3),s=new Qt(t,1);if(n.setAttribute("position",i),n.setIndex(s),r.uvs){const f=od(r.uvs);n.setAttribute("uv",new Qt(f,2))}n.computeVertexNormals();const a=TI.map(f=>new is({color:f.color,roughness:f.roughness,metalness:f.metalness,side:Fn,transparent:f.transparent||!1,opacity:f.opacity!==void 0?f.opacity:1,flatShading:!1})),c=r.groups||[];let u;if(s&&c.length>0){for(const f of c)n.addGroup(f.start,f.count,f.materialIndex);u=new we(n,a)}else u=new we(n,a[0]);u.castShadow=!0,u.receiveShadow=!0;const h=new Wi;return h.add(u),h}async function uh(r,e,t){const n=new URLSearchParams;if(e.body_type&&n.set("body_type",e.body_type),e.morphs&&typeof e.morphs=="object")for(const[m,g]of Object.entries(e.morphs))g!=null&&n.set(`morph_${m}`,String(g));if(e.user_morphs&&typeof e.user_morphs=="object")for(const[m,g]of Object.entries(e.user_morphs))g!=null&&n.set(`morph_${m}`,String(g));const i=["age","mass","tone","height"],s=e.meta||{};for(const m of i){const g=s[m]??e[`meta_${m}`];g!=null&&n.set(`meta_${m}`,String(g))}const a=`/api/character/mesh/?${n.toString()}`,c=await fetch(a);if(!c.ok)throw new Error(`Character mesh API error: ${c.status}`);const u=await c.json(),h=EI(u);if(r.add(h),e.hair_style&&e.hair_style.url)try{const m=await AI(e.hair_style.url);m.userData.isHair=!0,m.traverse(g=>{g.isMesh&&(g.userData.isHair=!0)}),h.add(m),console.log("✓ Hair loaded:",e.hair_style.name)}catch(m){console.error("Failed to load hair:",m)}if(e.garments&&Array.isArray(e.garments))for(const m of e.garments)try{const g=await wI(m,e.body_type);g.userData.isGarment=!0,h.add(g),console.log("✓ Garment loaded:",m.id)}catch(g){console.error("Failed to load garment:",m.id,g)}so++;const f=t||`Character ${so}`,p=Cd();return p&&Id(p,f,h),h}async function AI(r){return new Promise((e,t)=>{i_.load(r,n=>{const i=n.scene;i.traverse(s=>{if(s.isMesh&&(s.castShadow=!0,s.receiveShadow=!0,s.material)){if(s.material.color){const a=s.material.color;a.r>.9&&a.g>.9&&a.b>.9&&s.material.color.setRGB(.1,.08,.06)}s.material.roughness===void 0&&(s.material.roughness=.8),s.material.metalness===void 0&&(s.material.metalness=0)}}),e(i)},void 0,n=>t(n))})}async function wI(r,e){const{id:t,offset:n=.006,stiffness:i=.8,color:s=[.3,.35,.5],roughness:a=.8,metalness:c=0}=r,u=s[0]??.3,h=s[1]??.35,f=s[2]??.5,p=`garment_id=${encodeURIComponent(t)}&body_type=${encodeURIComponent(e)}&offset=${n}&stiffness=${i}&color_r=${u.toFixed(3)}&color_g=${h.toFixed(3)}&color_b=${f.toFixed(3)}`,m=await fetch(`/api/character/garment/fit/?${p}`);if(!m.ok)throw new Error(`Garment fit API error: ${m.status}`);const g=await m.json();if(g.error)throw new Error(g.error);const x=od(g.vertices);s_(x);const M=r_(g.faces),v=new sn;v.setAttribute("position",new Qt(x,3)),v.setIndex(new Qt(M,1)),v.computeVertexNormals();const _=new Ke(g.color[0],g.color[1],g.color[2]),A=new is({color:_,roughness:a,metalness:c,side:Fn,polygonOffset:!0,polygonOffsetFactor:-1,polygonOffsetUnit:-1}),P=new we(v,A);return P.castShadow=!0,P.receiveShadow=!0,P}function PI(r,e,t){const n=bI.parse(r),i=new hC(n.skeleton.bones[0]);i.skeleton=n.skeleton,i.visible=!0,i.userData.isRig=!0;const s=n.skeleton.bones[0];s.userData.isRig=!0,e.add(s),e.add(i);const a=new uC(s),c=a.clipAction(n.clip);c.setLoop(Mg),c.play(),c.paused=!0,so++;const u=Cd();u&&Id(u,t||`BVH ${so}`,s);const h=n.clip.duration||1;return{mixer:a,action:c,skeleton:i,clip:n.clip,rootBone:s,duration:h}}class RI{constructor(e){this._canvas=e,this._recorder=null,this._chunks=[]}start(e=30){const t=this._canvas.captureStream(e);this._chunks=[];const n=MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm;codecs=vp8";this._recorder=new MediaRecorder(t,{mimeType:n,videoBitsPerSecond:8e6}),this._recorder.ondataavailable=i=>{i.data.size>0&&this._chunks.push(i.data)},this._recorder.start()}stop(){return new Promise(e=>{this._recorder.onstop=()=>{const t=new Blob(this._chunks,{type:"video/webm"});this._chunks=[],e(t)},this._recorder.stop()})}get isRecording(){var e;return((e=this._recorder)==null?void 0:e.state)==="recording"}async stopAndDownload(e="theatre-export.webm"){const t=await this.stop(),n=URL.createObjectURL(t),i=document.createElement("a");i.href=n,i.download=e,i.click(),URL.revokeObjectURL(n)}}async function CI(){const r=await fetch("/api/character/scenes/");if(!r.ok)throw new Error(`Scene list error: ${r.status}`);return(await r.json()).scenes||[]}async function II(r){const e=await fetch(`/api/character/scene/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Scene load error: ${e.status}`);return e.json()}async function LI(r,e){const t=await fetch("/api/character/scene/save/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:r,data:e})});if(!t.ok){const n=await t.json().catch(()=>({}));throw new Error(n.error||`Scene save error: ${t.status}`)}return t.json()}async function DI(){const r=await fetch("/api/character/models/");if(!r.ok)throw new Error(`Model list error: ${r.status}`);return(await r.json()).presets||[]}async function ag(r){const e=await fetch(`/api/character/model/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Model load error: ${e.status}`);return e.json()}async function NI(){const r=await fetch("/api/character/animations/");if(!r.ok)throw new Error(`Animation list error: ${r.status}`);return(await r.json()).categories||{}}async function OI(r,e){const t=`/api/character/bvh/${encodeURIComponent(r)}/${encodeURIComponent(e)}/`,n=await fetch(t);if(!n.ok)throw new Error(`BVH load error: ${n.status}`);return n.text()}const hh={ballet_stage:{name:"Ballet Stage",description:"Warme Spotlights, theatralisch dunkel",camera:{position:{x:0,y:1.6,z:5},fov:35},lights:{spotLeft:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:-3,y:6,z:3}},spotRight:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:3,y:6,z:3}},backLight:{intensity:25,color:{r:.4,g:.267,b:.667},position:{x:0,y:5,z:-4}}}},studio_bright:{name:"Studio Bright",description:"Helle, gleichmäßige Beleuchtung für Details",camera:{position:{x:0,y:1.6,z:4},fov:40},lights:{spotLeft:{intensity:80,color:{r:1,g:1,b:1},position:{x:-2,y:5,z:4}},spotRight:{intensity:80,color:{r:1,g:1,b:1},position:{x:2,y:5,z:4}},backLight:{intensity:30,color:{r:.9,g:.95,b:1},position:{x:0,y:4,z:-3}}}},cinematic_moody:{name:"Cinematic Moody",description:"Dramatisches Film-noir-Licht, starke Schatten",camera:{position:{x:2,y:1.4,z:4},fov:28},lights:{spotLeft:{intensity:15,color:{r:1,g:.8,b:.6},position:{x:-4,y:7,z:2}},spotRight:{intensity:2,color:{r:.6,g:.7,b:.9},position:{x:4,y:3,z:3}},backLight:{intensity:10,color:{r:.3,g:.5,b:1},position:{x:1,y:6,z:-5}}}},fashion_show:{name:"Fashion Show",description:"Laufsteg-Beleuchtung, kühles Weiß von oben",camera:{position:{x:0,y:1.2,z:6},fov:50},lights:{spotLeft:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:-2,y:8,z:2}},spotRight:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:2,y:8,z:2}},backLight:{intensity:5,color:{r:1,g:1,b:1},position:{x:0,y:3,z:-2}}}},sunset_warm:{name:"Sunset Warm",description:"Goldene Stunde, warmes Orange-Gold",camera:{position:{x:-1,y:1.5,z:4.5},fov:42},lights:{spotLeft:{intensity:14,color:{r:1,g:.7,b:.4},position:{x:-5,y:4,z:3}},spotRight:{intensity:6,color:{r:1,g:.85,b:.7},position:{x:3,y:5,z:2}},backLight:{intensity:8,color:{r:.8,g:.4,b:.6},position:{x:2,y:5,z:-4}}}}};function dh(r,e,t,n){console.log(`[Preset] Applying: ${r.name}`),e.position.set(r.camera.position.x,r.camera.position.y,r.camera.position.z),e.fov=r.camera.fov,e.updateProjectionMatrix(),n&&(n.target.set(0,.9,0),n.update()),fh(t.spotLeft,r.lights.spotLeft),fh(t.spotRight,r.lights.spotRight),fh(t.backLight,r.lights.backLight),console.log(`✓ Preset "${r.name}" applied (direct Three.js)`)}function fh(r,e){r&&(r.intensity=e.intensity,r.color.setRGB(e.color.r,e.color.g,e.color.b),r.position.set(e.position.x,e.position.y,e.position.z))}window.addEventListener("DOMContentLoaded",()=>{const r=document.getElementById("theatre-canvas");if(!r){console.error("theatre-canvas not found");return}const{scene:e,camera:t,renderer:n,controls:i,lights:s,lightIcons:a,transformControls:c}=OC(r);window.scene=e,window.lights=s,window.lightIcons=a,window.transformControls=c,window.activeMixer=null,window.isPlaying=!1,window.currentTime=0,window.animDuration=1;const u=new Zg,h=new Qe;let f=null;const p=[];r.addEventListener("click",N=>{const Y=r.getBoundingClientRect();h.x=(N.clientX-Y.left)/Y.width*2-1,h.y=-((N.clientY-Y.top)/Y.height)*2+1,u.setFromCamera(h,t);const ae=[a.spotLeftIcon,a.spotRightIcon,a.backLightIcon],_e=u.intersectObjects(ae,!0);if(_e.length>0){let Re=_e[0].object;for(;Re.parent&&!Re.userData.light;)Re=Re.parent;if(Re.userData.light){f=Re,c.attach(Re),console.log("✓ Licht ausgewählt:",Re.userData.light),Ue(Re.userData.light);return}}const xe=u.intersectObjects(p,!0);if(xe.length>0){let Re=xe[0].object;for(;Re.parent&&!Re.userData.isCharacter;)Re=Re.parent;if(Re.userData.isCharacter){f=null,c.attach(Re),console.log("✓ Character ausgewählt:",Re.userData.presetName),Pe(Re);return}}c.detach(),f=null,De()});const{sheet:m}=FC();BC(m,t),bc(m,"Spot Left",s.spotLeft),bc(m,"Spot Right",s.spotRight),bc(m,"Back Light",s.backLight);const g=new RI(n.domElement);let x=null,M=null;const v=new $R;document.querySelectorAll(".menu-item").forEach(N=>{const Y=N.querySelector(".menu-dropdown");Y&&(N.addEventListener("click",ae=>{ae.stopPropagation(),document.querySelectorAll(".menu-item").forEach(_e=>_e.classList.remove("active")),N.classList.toggle("active")}),Y.addEventListener("click",ae=>{ae.stopPropagation()}))}),document.addEventListener("click",()=>{document.querySelectorAll(".menu-item").forEach(N=>N.classList.remove("active"))}),document.querySelectorAll("[data-preset]").forEach(N=>{N.addEventListener("click",()=>{const Y=N.getAttribute("data-preset"),ae=hh[Y];ae?(dh(ae,t,s,i),console.log("✓ Applied preset:",ae.name),document.querySelectorAll(".menu-item").forEach(_e=>_e.classList.remove("active"))):console.error("Preset not found:",Y)})}),document.querySelectorAll(".panel-tab").forEach(N=>{N.addEventListener("click",()=>{const Y=N.getAttribute("data-tab");document.querySelectorAll(".panel-tab").forEach(_e=>_e.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(_e=>_e.classList.remove("active")),N.classList.add("active");const ae=document.getElementById(Y);ae&&ae.classList.add("active")})});const _=document.getElementById("btn-translate-mode"),A=document.getElementById("btn-rotate-mode"),P=document.getElementById("btn-toggle-lights");_&&_.addEventListener("click",()=>{c.setMode("translate"),_.classList.add("active"),A.classList.remove("active")}),A&&A.addEventListener("click",()=>{c.setMode("rotate"),A.classList.add("active"),_.classList.remove("active")});let S=!0;P&&P.addEventListener("click",()=>{S=!S,Object.values(a).forEach(N=>{N.visible=S}),S?P.classList.add("active"):P.classList.remove("active")});const k=document.getElementById("btn-toggle-model");let O=!0;k&&k.addEventListener("click",()=>{O=!O,e.traverse(N=>{N.isMesh&&!N.userData.isGarment&&!N.userData.isHair&&!N.userData.isRig&&(N.visible=O)}),k.classList.toggle("active",O)});const U=document.getElementById("btn-toggle-clothes");let z=!0;U&&U.addEventListener("click",()=>{z=!z,e.traverse(N=>{N.isMesh&&(N.userData.isGarment||N.userData.isHair)&&(N.visible=z)}),U.classList.toggle("active",z)});const I=document.getElementById("btn-toggle-rig");let w=!1;I&&I.addEventListener("click",()=>{w=!w,e.traverse(N=>{(N.isSkeletonHelper||N.userData.isRig)&&(N.visible=w)}),I.classList.toggle("active",w)});const H=document.getElementById("btn-play-animation");H&&H.addEventListener("click",()=>{const N=document.getElementById("btnPlayPause");N&&N.click()});function ee(N){const Y=document.getElementById(N);Y&&(Y.style.display="flex")}function J(N){const Y=document.getElementById(N);Y&&(Y.style.display="none")}document.querySelectorAll("[data-close-modal]").forEach(N=>{N.addEventListener("click",()=>{var Y;(Y=N.closest(".theatre-modal-overlay"))==null||Y.style.removeProperty("display")})}),document.querySelectorAll(".theatre-modal-overlay").forEach(N=>{N.addEventListener("click",Y=>{Y.target===N&&N.style.removeProperty("display")})});const oe=document.getElementById("menu-scene-load");oe&&oe.addEventListener("click",async()=>{const N=document.getElementById("scene-list-body");N.innerHTML='<div class="loading-msg">Lade Scenes...</div>',ee("modal-scene-load");try{const Y=await CI();if(Y.length===0){N.innerHTML='<div class="loading-msg">Keine Scenes gefunden.</div>';return}N.innerHTML="";for(const ae of Y){const _e=document.createElement("div");_e.style.cssText="padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;",_e.innerHTML=`<span>${ae.label||ae.name}</span>`,_e.addEventListener("click",()=>ce(ae.name)),_e.addEventListener("mouseenter",()=>_e.style.background="rgba(124, 92, 191, 0.2)"),_e.addEventListener("mouseleave",()=>_e.style.background=""),N.appendChild(_e)}}catch(Y){N.innerHTML=`<div class="loading-msg">Fehler: ${Y.message}</div>`}});async function ce(N){J("modal-scene-load");try{const Y=await II(N);if(console.log("Scene loaded:",N,Y),Y.characters&&Array.isArray(Y.characters))for(const ae of Y.characters){const _e=await uh(e,ae,ae.name||N);_e.userData.isCharacter=!0,_e.userData.presetName=ae.name||N,_e.userData.bodyType=ae.body_type||"Unknown",p.push(_e)}}catch(Y){console.error("Scene load error:",Y),alert("Scene laden fehlgeschlagen: "+Y.message)}}const $=document.getElementById("menu-scene-save"),le=document.getElementById("scene-save-btn"),ne=document.getElementById("scene-save-name");$&&$.addEventListener("click",()=>{ee("modal-scene-save"),ne&&(ne.value="",ne.focus())}),le&&ne&&(le.addEventListener("click",async()=>{const N=ne.value.trim();if(N){le.disabled=!0,le.textContent="Speichere...";try{const Y={camera:{position:t.position.toArray(),fov:t.fov,target:i.target.toArray()},lights:{spotLeft:{position:s.spotLeft.position.toArray(),intensity:s.spotLeft.intensity,color:"#"+s.spotLeft.color.getHexString()},spotRight:{position:s.spotRight.position.toArray(),intensity:s.spotRight.intensity,color:"#"+s.spotRight.color.getHexString()},backLight:{position:s.backLight.position.toArray(),intensity:s.backLight.intensity,color:"#"+s.backLight.color.getHexString()}},characters:[]},ae=await LI(N,Y);console.log("Scene saved:",ae),J("modal-scene-save")}catch(Y){console.error("Scene save error:",Y),alert("Scene speichern fehlgeschlagen: "+Y.message)}le.disabled=!1,le.textContent="Speichern"}}),ne.addEventListener("keydown",N=>{N.key==="Enter"&&le.click()}));const ge=document.getElementById("model-list"),Te=document.getElementById("menu-model-load");async function Oe(){try{const N=await DI();if(N.length===0){ge.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';return}ge.innerHTML="";for(const Y of N){const ae=document.createElement("div");ae.className="anim-item",ae.textContent=Y.label||Y.name,ae.addEventListener("click",async()=>{try{const _e=await ag(Y.name),xe=await uh(e,_e,Y.name);xe.userData.isCharacter=!0,xe.userData.presetName=Y.name,xe.userData.bodyType=_e.body_type||"Unknown",p.push(xe),console.log("Model loaded:",Y.name),document.querySelectorAll("#model-list .anim-item").forEach(Re=>Re.classList.remove("active")),ae.classList.add("active")}catch(_e){console.error("Model load error:",_e),alert("Modell laden fehlgeschlagen: "+_e.message)}}),ge.appendChild(ae)}}catch(N){ge.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${N.message}</div>`}}Oe(),Te&&Te.addEventListener("click",()=>{document.querySelectorAll(".panel-tab").forEach(ae=>ae.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ae=>ae.classList.remove("active"));const N=document.querySelector('[data-tab="tab-models"]'),Y=document.getElementById("tab-models");N&&N.classList.add("active"),Y&&Y.classList.add("active")});const Ye=document.getElementById("anim-tree");async function yt(){try{const N=await NI(),Y=Object.keys(N);if(Y.length===0){Ye.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';return}Ye.innerHTML="";for(const ae of Y){const _e=N[ae],xe=document.createElement("div");xe.className="anim-cat";const Re=document.createElement("div");Re.className="anim-cat-header",Re.innerHTML=`<i class="fas fa-chevron-right"></i> ${ae} (${_e.length})`,Re.addEventListener("click",()=>{xe.classList.toggle("open")}),xe.appendChild(Re);const qe=document.createElement("div");qe.className="anim-cat-body";for(const lt of _e){const G=document.createElement("div");G.className="anim-item",G.textContent=lt.name,G.addEventListener("click",async()=>{await he(lt.category,lt.name),document.querySelectorAll("#anim-tree .anim-item").forEach(be=>be.classList.remove("active")),G.classList.add("active")}),qe.appendChild(G)}xe.appendChild(qe),Ye.appendChild(xe)}}catch(N){Ye.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${N.message}</div>`}}async function he(N,Y){try{const ae=await OI(N,Y),{mixer:_e,action:xe,duration:Re}=PI(ae,e,`${N}/${Y}`);x&&x.stopAllAction(),x=_e,M=xe,window.activeMixer=x,E(Re),Fe=!1,st=0,ke=Re,window.isPlaying=!1,window.currentTime=0,window.animDuration=Re,ue(),console.log("Animation loaded:",N,Y,Re)}catch(ae){console.error("Animation load error:",ae),alert("Animation laden fehlgeschlagen: "+ae.message)}}yt();const me=document.getElementById("menu-add-glb"),Ne=document.getElementById("glb-file-input");me&&Ne&&(me.addEventListener("click",()=>Ne.click()),Ne.addEventListener("change",async()=>{const N=Ne.files[0];if(N){try{await MI(N,e)}catch(Y){console.error("GLB load error:",Y),alert("Fehler beim Laden der GLB-Datei: "+Y.message)}Ne.value=""}})),document.querySelectorAll("[data-preset]").forEach(N=>{N.addEventListener("click",()=>{const Y=N.getAttribute("data-preset"),ae=hh[Y];ae?(dh(ae,t,s,i),console.log("✓ Applied preset:",ae.name)):console.error("Preset not found:",Y)})});const Me=document.getElementById("menu-add-light");let Xe=0;Me&&Me.addEventListener("click",()=>{Xe++;const N=new Kg(16777215,1,15);N.position.set((Math.random()-.5)*6,2+Math.random()*3,(Math.random()-.5)*6),e.add(N);const Y=new we(new ia(.08,8,8),new ii({color:16776960}));N.add(Y),bc(m,`Light ${Xe}`,N)});const Ze=document.getElementById("menu-export-video");Ze&&Ze.addEventListener("click",async()=>{g.isRecording?(Ze.innerHTML='<i class="fas fa-file-video"></i> Export Video',await g.stopAndDownload()):(g.start(30),Ze.innerHTML='<i class="fas fa-stop"></i> Stop Recording')});const tt=document.getElementById("btnPlayPause"),St=document.getElementById("btnStop"),rt=document.getElementById("btnFrameBack"),At=document.getElementById("btnFrameFwd"),W=document.getElementById("timelineSlider"),cn=document.getElementById("timeCurrent"),ht=document.getElementById("timeDuration"),ct=document.getElementById("playIcon");let Fe=!1,st=0,ke=1,D=1;function E(N){ke=N||1,ht.textContent=Z(ke),W.max=ke}function Z(N){const Y=Math.floor(N/60),ae=Math.floor(N%60);return`${String(Y).padStart(2,"0")}:${String(ae).padStart(2,"0")}`}function ue(){cn.textContent=Z(st),W.value=st,ct&&(ct.className=Fe?"fas fa-pause":"fas fa-play")}function pe(N){!x||!M||(st=Math.max(0,Math.min(N,ke)),M.time=st,x.update(0),ue())}tt&&tt.addEventListener("click",()=>{x&&(Fe=!Fe,window.isPlaying=Fe,Fe&&M?(M.paused=!1,M.play()):M&&(M.paused=!0),ue())}),St&&St.addEventListener("click",()=>{x&&(Fe=!1,st=0,pe(0),M&&(M.stop(),M.paused=!0),ue())}),rt&&rt.addEventListener("click",()=>{pe(st-1/30)}),At&&At.addEventListener("click",()=>{pe(st+1/30)}),W&&(W.addEventListener("mousedown",()=>{}),W.addEventListener("mouseup",()=>{}),W.addEventListener("input",()=>{const N=parseFloat(W.value);pe(N)})),document.querySelectorAll(".speed-btn").forEach(N=>{N.addEventListener("click",()=>{const Y=parseFloat(N.getAttribute("data-speed"));D=Y,x&&(x.timeScale=Y),document.querySelectorAll(".speed-btn").forEach(ae=>ae.classList.remove("active")),N.classList.add("active")})}),document.addEventListener("keydown",N=>{N.target.tagName!=="INPUT"&&(N.code==="Space"?(N.preventDefault(),tt&&tt.click()):N.code==="ArrowLeft"?(N.preventDefault(),rt&&rt.click()):N.code==="ArrowRight"&&(N.preventDefault(),At&&At.click()))});async function fe(){try{const N=await fetch("/api/settings/theatre/");if(!N.ok)return;const Y=await N.json();if(Y.preset){const ae=hh[Y.preset];ae&&(dh(ae,t,s,i),console.log("✓ Auto-applied preset:",ae.name))}if(Y.model)try{const ae=await ag(Y.model),_e=await uh(e,ae,Y.model);if(_e.userData.isCharacter=!0,_e.userData.presetName=Y.model,_e.userData.bodyType=ae.body_type||"Unknown",p.push(_e),console.log("✓ Auto-loaded model:",Y.model),Y.animation){const[xe,Re]=Y.animation.split("/");xe&&Re&&(await he(xe,Re),console.log("✓ Auto-loaded animation:",Y.animation))}}catch(ae){console.warn("Auto-load model/animation failed:",ae)}}catch(N){console.warn("Failed to load Theatre defaults:",N)}}setTimeout(fe,500);function Ue(N){document.querySelectorAll(".panel-tab").forEach(ot=>ot.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ot=>ot.classList.remove("active"));const Y=document.querySelector('[data-tab="tab-properties"]'),ae=document.getElementById("tab-properties");Y&&Y.classList.add("active"),ae&&ae.classList.add("active");const _e=document.getElementById("properties-content");if(!_e)return;const xe=N===s.spotLeft?"Spot Left":N===s.spotRight?"Spot Right":N===s.backLight?"Back Light":"Light",Re="#"+N.color.getHexString();_e.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${xe}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${N.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${N.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${Re}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${N.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${N.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${N.position.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="light-rot-x" value="${(N.rotation.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(N.rotation.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(N.rotation.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const qe=document.getElementById("light-intensity"),lt=document.getElementById("light-intensity-value"),G=document.getElementById("light-color"),be=document.getElementById("light-pos-x"),ie=document.getElementById("light-pos-y"),de=document.getElementById("light-pos-z");if(qe&&(qe.oninput=ot=>{N.intensity=parseFloat(ot.target.value),lt.textContent=N.intensity.toFixed(1)}),G&&(G.oninput=ot=>{N.color.setHex(parseInt(ot.target.value.substring(1),16)),f&&f.children.forEach(Vt=>{Vt.material&&(Vt.material.color.copy(N.color),Vt.material.emissive&&Vt.material.emissive.copy(N.color))})}),be&&ie&&de){const ot=()=>{N.position.set(parseFloat(be.value),parseFloat(ie.value),parseFloat(de.value)),f&&(f.position.copy(N.position),f.lookAt(N.target.position))};be.oninput=ot,ie.oninput=ot,de.oninput=ot}const Ae=document.getElementById("light-rot-x"),Ee=document.getElementById("light-rot-y"),Ge=document.getElementById("light-rot-z");if(Ae&&Ee&&Ge){const ot=()=>{N.rotation.set(parseFloat(Ae.value)*Math.PI/180,parseFloat(Ee.value)*Math.PI/180,parseFloat(Ge.value)*Math.PI/180),f&&f.rotation.copy(N.rotation)};Ae.oninput=ot,Ee.oninput=ot,Ge.oninput=ot}}function Pe(N){document.querySelectorAll(".panel-tab").forEach(Ge=>Ge.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Ge=>Ge.classList.remove("active"));const Y=document.querySelector('[data-tab="tab-properties"]'),ae=document.getElementById("tab-properties");Y&&Y.classList.add("active"),ae&&ae.classList.add("active");const _e=document.getElementById("properties-content");if(!_e)return;const xe=N.userData.presetName||"Character",Re=N.userData.bodyType||"Unknown",qe=N.position,lt=N.rotation;_e.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${xe}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${Re}</span>
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
                            <input type="number" id="char-rot-x" value="${(lt.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(lt.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(lt.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const G=document.getElementById("char-pos-x"),be=document.getElementById("char-pos-y"),ie=document.getElementById("char-pos-z");if(G&&be&&ie){const Ge=()=>{N.position.set(parseFloat(G.value),parseFloat(be.value),parseFloat(ie.value))};G.oninput=Ge,be.oninput=Ge,ie.oninput=Ge}const de=document.getElementById("char-rot-x"),Ae=document.getElementById("char-rot-y"),Ee=document.getElementById("char-rot-z");if(de&&Ae&&Ee){const Ge=()=>{N.rotation.set(parseFloat(de.value)*Math.PI/180,parseFloat(Ae.value)*Math.PI/180,parseFloat(Ee.value)*Math.PI/180)};de.oninput=Ge,Ae.oninput=Ge,Ee.oninput=Ge}}function De(){const N=document.getElementById("properties-content");N&&(N.innerHTML=`
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `)}function dt(){requestAnimationFrame(dt);const N=v.getDelta();if(x&&Fe&&(x.update(N*D),st=M?M.time:0,st>=ke&&(st=0,M&&(M.time=0)),ue()),f&&f.userData.light){const Y=f.userData.light;Y.position.copy(f.position),f.lookAt(Y.target.position)}i.update(),n.render(e,t)}dt()});
