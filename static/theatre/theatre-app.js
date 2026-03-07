/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const js={ROTATE:0,DOLLY:1,PAN:2},zs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},cT=0,Ap=1,lT=2,ug=1,uT=2,Xi=3,Ji=0,qn=1,Xn=2,br=0,Xs=1,wp=2,Pp=3,Rp=4,hT=5,ns=100,dT=101,fT=102,pT=103,mT=104,gT=200,_T=201,vT=202,yT=203,gh=204,_h=205,xT=206,bT=207,ST=208,MT=209,TT=210,ET=211,AT=212,wT=213,PT=214,vh=0,yh=1,xh=2,$s=3,bh=4,Sh=5,Mh=6,Th=7,hg=0,RT=1,CT=2,Sr=0,IT=1,LT=2,DT=3,dg=4,NT=5,OT=6,UT=7,Cp="attached",FT="detached",fg=300,Zs=301,Js=302,Eh=303,Ah=304,kc=306,Qs=1e3,yr=1001,Dc=1002,zn=1003,pg=1004,Go=1005,ii=1006,Mc=1007,Yi=1008,Qi=1009,mg=1010,gg=1011,Jo=1012,ld=1013,ss=1014,vi=1015,na=1016,ud=1017,hd=1018,eo=1020,_g=35902,vg=1021,yg=1022,li=1023,xg=1024,bg=1025,qs=1026,to=1027,dd=1028,fd=1029,Sg=1030,pd=1031,md=1033,Tc=33776,Ec=33777,Ac=33778,wc=33779,wh=35840,Ph=35841,Rh=35842,Ch=35843,Ih=36196,Lh=37492,Dh=37496,Nh=37808,Oh=37809,Uh=37810,Fh=37811,Bh=37812,kh=37813,zh=37814,Hh=37815,Vh=37816,Gh=37817,Wh=37818,jh=37819,Xh=37820,qh=37821,Pc=36492,Yh=36494,Kh=36495,Mg=36283,$h=36284,Zh=36285,Jh=36286,BT=2200,gd=2201,kT=2202,Qo=2300,ea=2301,Mu=2302,Hs=2400,Vs=2401,Nc=2402,_d=2500,zT=2501,HT=0,Tg=1,Qh=2,VT=3200,GT=3201,Eg=0,WT=1,vr="",bn="srgb",Hn="srgb-linear",zc="linear",Ht="srgb",Es=7680,Ip=519,jT=512,XT=513,qT=514,Ag=515,YT=516,KT=517,$T=518,ZT=519,ed=35044,Lp="300 es",Ki=2e3,Oc=2001;class Tr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,a=i.length;s<a;s++)i[s].call(this,e);e.target=null}}}const Ln=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Dp=1234567;const Ko=Math.PI/180,no=180/Math.PI;function yi(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Ln[r&255]+Ln[r>>8&255]+Ln[r>>16&255]+Ln[r>>24&255]+"-"+Ln[e&255]+Ln[e>>8&255]+"-"+Ln[e>>16&15|64]+Ln[e>>24&255]+"-"+Ln[t&63|128]+Ln[t>>8&255]+"-"+Ln[t>>16&255]+Ln[t>>24&255]+Ln[n&255]+Ln[n>>8&255]+Ln[n>>16&255]+Ln[n>>24&255]).toLowerCase()}function wn(r,e,t){return Math.max(e,Math.min(t,r))}function vd(r,e){return(r%e+e)%e}function JT(r,e,t,n,i){return n+(r-e)*(i-n)/(t-e)}function QT(r,e,t){return r!==e?(t-r)/(e-r):0}function $o(r,e,t){return(1-t)*r+t*e}function eE(r,e,t,n){return $o(r,e,1-Math.exp(-t*n))}function tE(r,e=1){return e-Math.abs(vd(r,e*2)-e)}function nE(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*(3-2*r))}function iE(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*r*(r*(r*6-15)+10))}function rE(r,e){return r+Math.floor(Math.random()*(e-r+1))}function sE(r,e){return r+Math.random()*(e-r)}function oE(r){return r*(.5-Math.random())}function aE(r){r!==void 0&&(Dp=r);let e=Dp+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function cE(r){return r*Ko}function lE(r){return r*no}function uE(r){return(r&r-1)===0&&r!==0}function hE(r){return Math.pow(2,Math.ceil(Math.log(r)/Math.LN2))}function dE(r){return Math.pow(2,Math.floor(Math.log(r)/Math.LN2))}function fE(r,e,t,n,i){const s=Math.cos,a=Math.sin,c=s(t/2),u=a(t/2),h=s((e+n)/2),f=a((e+n)/2),p=s((e-n)/2),m=a((e-n)/2),g=s((n-e)/2),x=a((n-e)/2);switch(i){case"XYX":r.set(c*f,u*p,u*m,c*h);break;case"YZY":r.set(u*m,c*f,u*p,c*h);break;case"ZXZ":r.set(u*p,u*m,c*f,c*h);break;case"XZX":r.set(c*f,u*x,u*g,c*h);break;case"YXY":r.set(u*g,c*f,u*x,c*h);break;case"ZYZ":r.set(u*x,u*g,c*f,c*h);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function gi(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function kt(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}const wg={DEG2RAD:Ko,RAD2DEG:no,generateUUID:yi,clamp:wn,euclideanModulo:vd,mapLinear:JT,inverseLerp:QT,lerp:$o,damp:eE,pingpong:tE,smoothstep:nE,smootherstep:iE,randInt:rE,randFloat:sE,randFloatSpread:oE,seededRandom:aE,degToRad:cE,radToDeg:lE,isPowerOfTwo:uE,ceilPowerOfTwo:hE,floorPowerOfTwo:dE,setQuaternionFromProperEuler:fE,normalize:kt,denormalize:gi};class tt{constructor(e=0,t=0){tt.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(wn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*i+e.x,this.y=s*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class gt{constructor(e,t,n,i,s,a,c,u,h){gt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h)}set(e,t,n,i,s,a,c,u,h){const f=this.elements;return f[0]=e,f[1]=i,f[2]=c,f[3]=t,f[4]=s,f[5]=u,f[6]=n,f[7]=a,f[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[3],u=n[6],h=n[1],f=n[4],p=n[7],m=n[2],g=n[5],x=n[8],M=i[0],v=i[3],_=i[6],A=i[1],w=i[4],b=i[7],B=i[2],U=i[5],O=i[8];return s[0]=a*M+c*A+u*B,s[3]=a*v+c*w+u*U,s[6]=a*_+c*b+u*O,s[1]=h*M+f*A+p*B,s[4]=h*v+f*w+p*U,s[7]=h*_+f*b+p*O,s[2]=m*M+g*A+x*B,s[5]=m*v+g*w+x*U,s[8]=m*_+g*b+x*O,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8];return t*a*f-t*c*h-n*s*f+n*c*u+i*s*h-i*a*u}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=f*a-c*h,m=c*u-f*s,g=h*s-a*u,x=t*p+n*m+i*g;if(x===0)return this.set(0,0,0,0,0,0,0,0,0);const M=1/x;return e[0]=p*M,e[1]=(i*h-f*n)*M,e[2]=(c*n-i*a)*M,e[3]=m*M,e[4]=(f*t-i*u)*M,e[5]=(i*s-c*t)*M,e[6]=g*M,e[7]=(n*u-h*t)*M,e[8]=(a*t-n*s)*M,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,a,c){const u=Math.cos(s),h=Math.sin(s);return this.set(n*u,n*h,-n*(u*a+h*c)+a+e,-i*h,i*u,-i*(-h*a+u*c)+c+t,0,0,1),this}scale(e,t){return this.premultiply(Tu.makeScale(e,t)),this}rotate(e){return this.premultiply(Tu.makeRotation(-e)),this}translate(e,t){return this.premultiply(Tu.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Tu=new gt;function Pg(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function ta(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function pE(){const r=ta("canvas");return r.style.display="block",r}const Np={};function Wo(r){r in Np||(Np[r]=!0,console.warn(r))}function mE(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function gE(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function _E(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const wt={enabled:!0,workingColorSpace:Hn,spaces:{},convert:function(r,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Ht&&(r.r=Zi(r.r),r.g=Zi(r.g),r.b=Zi(r.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(r.applyMatrix3(this.spaces[e].toXYZ),r.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Ht&&(r.r=Ys(r.r),r.g=Ys(r.g),r.b=Ys(r.b))),r},fromWorkingColorSpace:function(r,e){return this.convert(r,this.workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===vr?zc:this.spaces[r].transfer},getLuminanceCoefficients:function(r,e=this.workingColorSpace){return r.fromArray(this.spaces[e].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,e,t){return r.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace}};function Zi(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ys(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}const Op=[.64,.33,.3,.6,.15,.06],Up=[.2126,.7152,.0722],Fp=[.3127,.329],Bp=new gt().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),kp=new gt().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);wt.define({[Hn]:{primaries:Op,whitePoint:Fp,transfer:zc,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Up,workingColorSpaceConfig:{unpackColorSpace:bn},outputColorSpaceConfig:{drawingBufferColorSpace:bn}},[bn]:{primaries:Op,whitePoint:Fp,transfer:Ht,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Up,outputColorSpaceConfig:{drawingBufferColorSpace:bn}}});let As;class vE{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{As===void 0&&(As=ta("canvas")),As.width=e.width,As.height=e.height;const n=As.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=As}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=ta("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let a=0;a<s.length;a++)s[a]=Zi(s[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Zi(t[n]/255)*255):t[n]=Zi(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let yE=0;class Rg{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:yE++}),this.uuid=yi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let a=0,c=i.length;a<c;a++)i[a].isDataTexture?s.push(Eu(i[a].image)):s.push(Eu(i[a]))}else s=Eu(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function Eu(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?vE.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let xE=0;class Sn extends Tr{constructor(e=Sn.DEFAULT_IMAGE,t=Sn.DEFAULT_MAPPING,n=yr,i=yr,s=ii,a=Yi,c=li,u=Qi,h=Sn.DEFAULT_ANISOTROPY,f=vr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:xE++}),this.uuid=yi(),this.name="",this.source=new Rg(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=a,this.anisotropy=h,this.format=c,this.internalFormat=null,this.type=u,this.offset=new tt(0,0),this.repeat=new tt(1,1),this.center=new tt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new gt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==fg)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Qs:e.x=e.x-Math.floor(e.x);break;case yr:e.x=e.x<0?0:1;break;case Dc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Qs:e.y=e.y-Math.floor(e.y);break;case yr:e.y=e.y<0?0:1;break;case Dc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Sn.DEFAULT_IMAGE=null;Sn.DEFAULT_MAPPING=fg;Sn.DEFAULT_ANISOTROPY=1;class Dt{constructor(e=0,t=0,n=0,i=1){Dt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const u=e.elements,h=u[0],f=u[4],p=u[8],m=u[1],g=u[5],x=u[9],M=u[2],v=u[6],_=u[10];if(Math.abs(f-m)<.01&&Math.abs(p-M)<.01&&Math.abs(x-v)<.01){if(Math.abs(f+m)<.1&&Math.abs(p+M)<.1&&Math.abs(x+v)<.1&&Math.abs(h+g+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const w=(h+1)/2,b=(g+1)/2,B=(_+1)/2,U=(f+m)/4,O=(p+M)/4,H=(x+v)/4;return w>b&&w>B?w<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(w),i=U/n,s=O/n):b>B?b<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(b),n=U/i,s=H/i):B<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(B),n=O/s,i=H/s),this.set(n,i,s,t),this}let A=Math.sqrt((v-x)*(v-x)+(p-M)*(p-M)+(m-f)*(m-f));return Math.abs(A)<.001&&(A=1),this.x=(v-x)/A,this.y=(p-M)/A,this.z=(m-f)/A,this.w=Math.acos((h+g+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class bE extends Tr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Dt(0,0,e,t),this.scissorTest=!1,this.viewport=new Dt(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ii,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new Sn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let c=0;c<a;c++)this.textures[c]=s.clone(),this.textures[c].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Rg(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class os extends bE{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Cg extends Sn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=zn,this.minFilter=zn,this.wrapR=yr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class SE extends Sn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=zn,this.minFilter=zn,this.wrapR=yr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class en{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,a,c){let u=n[i+0],h=n[i+1],f=n[i+2],p=n[i+3];const m=s[a+0],g=s[a+1],x=s[a+2],M=s[a+3];if(c===0){e[t+0]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p;return}if(c===1){e[t+0]=m,e[t+1]=g,e[t+2]=x,e[t+3]=M;return}if(p!==M||u!==m||h!==g||f!==x){let v=1-c;const _=u*m+h*g+f*x+p*M,A=_>=0?1:-1,w=1-_*_;if(w>Number.EPSILON){const B=Math.sqrt(w),U=Math.atan2(B,_*A);v=Math.sin(v*U)/B,c=Math.sin(c*U)/B}const b=c*A;if(u=u*v+m*b,h=h*v+g*b,f=f*v+x*b,p=p*v+M*b,v===1-c){const B=1/Math.sqrt(u*u+h*h+f*f+p*p);u*=B,h*=B,f*=B,p*=B}}e[t]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p}static multiplyQuaternionsFlat(e,t,n,i,s,a){const c=n[i],u=n[i+1],h=n[i+2],f=n[i+3],p=s[a],m=s[a+1],g=s[a+2],x=s[a+3];return e[t]=c*x+f*p+u*g-h*m,e[t+1]=u*x+f*m+h*p-c*g,e[t+2]=h*x+f*g+c*m-u*p,e[t+3]=f*x-c*p-u*m-h*g,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,a=e._order,c=Math.cos,u=Math.sin,h=c(n/2),f=c(i/2),p=c(s/2),m=u(n/2),g=u(i/2),x=u(s/2);switch(a){case"XYZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"YXZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"ZXY":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"ZYX":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"YZX":this._x=m*f*p+h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p-m*g*x;break;case"XZY":this._x=m*f*p-h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p+m*g*x;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],a=t[1],c=t[5],u=t[9],h=t[2],f=t[6],p=t[10],m=n+c+p;if(m>0){const g=.5/Math.sqrt(m+1);this._w=.25/g,this._x=(f-u)*g,this._y=(s-h)*g,this._z=(a-i)*g}else if(n>c&&n>p){const g=2*Math.sqrt(1+n-c-p);this._w=(f-u)/g,this._x=.25*g,this._y=(i+a)/g,this._z=(s+h)/g}else if(c>p){const g=2*Math.sqrt(1+c-n-p);this._w=(s-h)/g,this._x=(i+a)/g,this._y=.25*g,this._z=(u+f)/g}else{const g=2*Math.sqrt(1+p-n-c);this._w=(a-i)/g,this._x=(s+h)/g,this._y=(u+f)/g,this._z=.25*g}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(wn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,a=e._w,c=t._x,u=t._y,h=t._z,f=t._w;return this._x=n*f+a*c+i*h-s*u,this._y=i*f+a*u+s*c-n*h,this._z=s*f+a*h+n*u-i*c,this._w=a*f-n*c-i*u-s*h,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,a=this._w;let c=a*e._w+n*e._x+i*e._y+s*e._z;if(c<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,c=-c):this.copy(e),c>=1)return this._w=a,this._x=n,this._y=i,this._z=s,this;const u=1-c*c;if(u<=Number.EPSILON){const g=1-t;return this._w=g*a+t*this._w,this._x=g*n+t*this._x,this._y=g*i+t*this._y,this._z=g*s+t*this._z,this.normalize(),this}const h=Math.sqrt(u),f=Math.atan2(h,c),p=Math.sin((1-t)*f)/h,m=Math.sin(t*f)/h;return this._w=a*p+this._w*m,this._x=n*p+this._x*m,this._y=i*p+this._y*m,this._z=s*p+this._z*m,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class F{constructor(e=0,t=0,n=0){F.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(zp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(zp.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,a=e.y,c=e.z,u=e.w,h=2*(a*i-c*n),f=2*(c*t-s*i),p=2*(s*n-a*t);return this.x=t+u*h+a*p-c*f,this.y=n+u*f+c*h-s*p,this.z=i+u*p+s*f-a*h,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,a=t.x,c=t.y,u=t.z;return this.x=i*u-s*c,this.y=s*a-n*u,this.z=n*c-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Au.copy(this).projectOnVector(e),this.sub(Au)}reflect(e){return this.sub(Au.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(wn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Au=new F,zp=new en;class er{constructor(e=new F(1/0,1/0,1/0),t=new F(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(di.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(di.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=di.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,c=s.count;a<c;a++)e.isMesh===!0?e.getVertexPosition(a,di):di.fromBufferAttribute(s,a),di.applyMatrix4(e.matrixWorld),this.expandByPoint(di);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Wa.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Wa.copy(n.boundingBox)),Wa.applyMatrix4(e.matrixWorld),this.union(Wa)}const i=e.children;for(let s=0,a=i.length;s<a;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,di),di.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Lo),ja.subVectors(this.max,Lo),ws.subVectors(e.a,Lo),Ps.subVectors(e.b,Lo),Rs.subVectors(e.c,Lo),cr.subVectors(Ps,ws),lr.subVectors(Rs,Ps),Xr.subVectors(ws,Rs);let t=[0,-cr.z,cr.y,0,-lr.z,lr.y,0,-Xr.z,Xr.y,cr.z,0,-cr.x,lr.z,0,-lr.x,Xr.z,0,-Xr.x,-cr.y,cr.x,0,-lr.y,lr.x,0,-Xr.y,Xr.x,0];return!wu(t,ws,Ps,Rs,ja)||(t=[1,0,0,0,1,0,0,0,1],!wu(t,ws,Ps,Rs,ja))?!1:(Xa.crossVectors(cr,lr),t=[Xa.x,Xa.y,Xa.z],wu(t,ws,Ps,Rs,ja))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,di).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(di).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(zi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),zi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),zi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),zi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),zi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),zi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),zi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),zi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(zi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const zi=[new F,new F,new F,new F,new F,new F,new F,new F],di=new F,Wa=new er,ws=new F,Ps=new F,Rs=new F,cr=new F,lr=new F,Xr=new F,Lo=new F,ja=new F,Xa=new F,qr=new F;function wu(r,e,t,n,i){for(let s=0,a=r.length-3;s<=a;s+=3){qr.fromArray(r,s);const c=i.x*Math.abs(qr.x)+i.y*Math.abs(qr.y)+i.z*Math.abs(qr.z),u=e.dot(qr),h=t.dot(qr),f=n.dot(qr);if(Math.max(-Math.max(u,h,f),Math.min(u,h,f))>c)return!1}return!0}const ME=new er,Do=new F,Pu=new F;class wi{constructor(e=new F,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):ME.setFromPoints(e).getCenter(n);let i=0;for(let s=0,a=e.length;s<a;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Do.subVectors(e,this.center);const t=Do.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Do,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Pu.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Do.copy(e.center).add(Pu)),this.expandByPoint(Do.copy(e.center).sub(Pu))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Hi=new F,Ru=new F,qa=new F,ur=new F,Cu=new F,Ya=new F,Iu=new F;class oo{constructor(e=new F,t=new F(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Hi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Hi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Hi.copy(this.origin).addScaledVector(this.direction,t),Hi.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Ru.copy(e).add(t).multiplyScalar(.5),qa.copy(t).sub(e).normalize(),ur.copy(this.origin).sub(Ru);const s=e.distanceTo(t)*.5,a=-this.direction.dot(qa),c=ur.dot(this.direction),u=-ur.dot(qa),h=ur.lengthSq(),f=Math.abs(1-a*a);let p,m,g,x;if(f>0)if(p=a*u-c,m=a*c-u,x=s*f,p>=0)if(m>=-x)if(m<=x){const M=1/f;p*=M,m*=M,g=p*(p+a*m+2*c)+m*(a*p+m+2*u)+h}else m=s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m=-s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m<=-x?(p=Math.max(0,-(-a*s+c)),m=p>0?-s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h):m<=x?(p=0,m=Math.min(Math.max(-s,-u),s),g=m*(m+2*u)+h):(p=Math.max(0,-(a*s+c)),m=p>0?s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h);else m=a>0?-s:s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;return n&&n.copy(this.origin).addScaledVector(this.direction,p),i&&i.copy(Ru).addScaledVector(qa,m),g}intersectSphere(e,t){Hi.subVectors(e.center,this.origin);const n=Hi.dot(this.direction),i=Hi.dot(Hi)-n*n,s=e.radius*e.radius;if(i>s)return null;const a=Math.sqrt(s-i),c=n-a,u=n+a;return u<0?null:c<0?this.at(u,t):this.at(c,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,a,c,u;const h=1/this.direction.x,f=1/this.direction.y,p=1/this.direction.z,m=this.origin;return h>=0?(n=(e.min.x-m.x)*h,i=(e.max.x-m.x)*h):(n=(e.max.x-m.x)*h,i=(e.min.x-m.x)*h),f>=0?(s=(e.min.y-m.y)*f,a=(e.max.y-m.y)*f):(s=(e.max.y-m.y)*f,a=(e.min.y-m.y)*f),n>a||s>i||((s>n||isNaN(n))&&(n=s),(a<i||isNaN(i))&&(i=a),p>=0?(c=(e.min.z-m.z)*p,u=(e.max.z-m.z)*p):(c=(e.max.z-m.z)*p,u=(e.min.z-m.z)*p),n>u||c>i)||((c>n||n!==n)&&(n=c),(u<i||i!==i)&&(i=u),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,Hi)!==null}intersectTriangle(e,t,n,i,s){Cu.subVectors(t,e),Ya.subVectors(n,e),Iu.crossVectors(Cu,Ya);let a=this.direction.dot(Iu),c;if(a>0){if(i)return null;c=1}else if(a<0)c=-1,a=-a;else return null;ur.subVectors(this.origin,e);const u=c*this.direction.dot(Ya.crossVectors(ur,Ya));if(u<0)return null;const h=c*this.direction.dot(Cu.cross(ur));if(h<0||u+h>a)return null;const f=-c*ur.dot(Iu);return f<0?null:this.at(f/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class ot{constructor(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v){ot.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v)}set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v){const _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=a,_[9]=c,_[13]=u,_[2]=h,_[6]=f,_[10]=p,_[14]=m,_[3]=g,_[7]=x,_[11]=M,_[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new ot().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Cs.setFromMatrixColumn(e,0).length(),s=1/Cs.setFromMatrixColumn(e,1).length(),a=1/Cs.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,a=Math.cos(n),c=Math.sin(n),u=Math.cos(i),h=Math.sin(i),f=Math.cos(s),p=Math.sin(s);if(e.order==="XYZ"){const m=a*f,g=a*p,x=c*f,M=c*p;t[0]=u*f,t[4]=-u*p,t[8]=h,t[1]=g+x*h,t[5]=m-M*h,t[9]=-c*u,t[2]=M-m*h,t[6]=x+g*h,t[10]=a*u}else if(e.order==="YXZ"){const m=u*f,g=u*p,x=h*f,M=h*p;t[0]=m+M*c,t[4]=x*c-g,t[8]=a*h,t[1]=a*p,t[5]=a*f,t[9]=-c,t[2]=g*c-x,t[6]=M+m*c,t[10]=a*u}else if(e.order==="ZXY"){const m=u*f,g=u*p,x=h*f,M=h*p;t[0]=m-M*c,t[4]=-a*p,t[8]=x+g*c,t[1]=g+x*c,t[5]=a*f,t[9]=M-m*c,t[2]=-a*h,t[6]=c,t[10]=a*u}else if(e.order==="ZYX"){const m=a*f,g=a*p,x=c*f,M=c*p;t[0]=u*f,t[4]=x*h-g,t[8]=m*h+M,t[1]=u*p,t[5]=M*h+m,t[9]=g*h-x,t[2]=-h,t[6]=c*u,t[10]=a*u}else if(e.order==="YZX"){const m=a*u,g=a*h,x=c*u,M=c*h;t[0]=u*f,t[4]=M-m*p,t[8]=x*p+g,t[1]=p,t[5]=a*f,t[9]=-c*f,t[2]=-h*f,t[6]=g*p+x,t[10]=m-M*p}else if(e.order==="XZY"){const m=a*u,g=a*h,x=c*u,M=c*h;t[0]=u*f,t[4]=-p,t[8]=h*f,t[1]=m*p+M,t[5]=a*f,t[9]=g*p-x,t[2]=x*p-g,t[6]=c*f,t[10]=M*p+m}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(TE,e,EE)}lookAt(e,t,n){const i=this.elements;return ti.subVectors(e,t),ti.lengthSq()===0&&(ti.z=1),ti.normalize(),hr.crossVectors(n,ti),hr.lengthSq()===0&&(Math.abs(n.z)===1?ti.x+=1e-4:ti.z+=1e-4,ti.normalize(),hr.crossVectors(n,ti)),hr.normalize(),Ka.crossVectors(ti,hr),i[0]=hr.x,i[4]=Ka.x,i[8]=ti.x,i[1]=hr.y,i[5]=Ka.y,i[9]=ti.y,i[2]=hr.z,i[6]=Ka.z,i[10]=ti.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[4],u=n[8],h=n[12],f=n[1],p=n[5],m=n[9],g=n[13],x=n[2],M=n[6],v=n[10],_=n[14],A=n[3],w=n[7],b=n[11],B=n[15],U=i[0],O=i[4],H=i[8],L=i[12],P=i[1],V=i[5],ee=i[9],Q=i[13],ae=i[2],ce=i[6],J=i[10],de=i[14],re=i[3],_e=i[7],Me=i[11],Ue=i[15];return s[0]=a*U+c*P+u*ae+h*re,s[4]=a*O+c*V+u*ce+h*_e,s[8]=a*H+c*ee+u*J+h*Me,s[12]=a*L+c*Q+u*de+h*Ue,s[1]=f*U+p*P+m*ae+g*re,s[5]=f*O+p*V+m*ce+g*_e,s[9]=f*H+p*ee+m*J+g*Me,s[13]=f*L+p*Q+m*de+g*Ue,s[2]=x*U+M*P+v*ae+_*re,s[6]=x*O+M*V+v*ce+_*_e,s[10]=x*H+M*ee+v*J+_*Me,s[14]=x*L+M*Q+v*de+_*Ue,s[3]=A*U+w*P+b*ae+B*re,s[7]=A*O+w*V+b*ce+B*_e,s[11]=A*H+w*ee+b*J+B*Me,s[15]=A*L+w*Q+b*de+B*Ue,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],a=e[1],c=e[5],u=e[9],h=e[13],f=e[2],p=e[6],m=e[10],g=e[14],x=e[3],M=e[7],v=e[11],_=e[15];return x*(+s*u*p-i*h*p-s*c*m+n*h*m+i*c*g-n*u*g)+M*(+t*u*g-t*h*m+s*a*m-i*a*g+i*h*f-s*u*f)+v*(+t*h*p-t*c*g-s*a*p+n*a*g+s*c*f-n*h*f)+_*(-i*c*f-t*u*p+t*c*m+i*a*p-n*a*m+n*u*f)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=e[9],m=e[10],g=e[11],x=e[12],M=e[13],v=e[14],_=e[15],A=p*v*h-M*m*h+M*u*g-c*v*g-p*u*_+c*m*_,w=x*m*h-f*v*h-x*u*g+a*v*g+f*u*_-a*m*_,b=f*M*h-x*p*h+x*c*g-a*M*g-f*c*_+a*p*_,B=x*p*u-f*M*u-x*c*m+a*M*m+f*c*v-a*p*v,U=t*A+n*w+i*b+s*B;if(U===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const O=1/U;return e[0]=A*O,e[1]=(M*m*s-p*v*s-M*i*g+n*v*g+p*i*_-n*m*_)*O,e[2]=(c*v*s-M*u*s+M*i*h-n*v*h-c*i*_+n*u*_)*O,e[3]=(p*u*s-c*m*s-p*i*h+n*m*h+c*i*g-n*u*g)*O,e[4]=w*O,e[5]=(f*v*s-x*m*s+x*i*g-t*v*g-f*i*_+t*m*_)*O,e[6]=(x*u*s-a*v*s-x*i*h+t*v*h+a*i*_-t*u*_)*O,e[7]=(a*m*s-f*u*s+f*i*h-t*m*h-a*i*g+t*u*g)*O,e[8]=b*O,e[9]=(x*p*s-f*M*s-x*n*g+t*M*g+f*n*_-t*p*_)*O,e[10]=(a*M*s-x*c*s+x*n*h-t*M*h-a*n*_+t*c*_)*O,e[11]=(f*c*s-a*p*s-f*n*h+t*p*h+a*n*g-t*c*g)*O,e[12]=B*O,e[13]=(f*M*i-x*p*i+x*n*m-t*M*m-f*n*v+t*p*v)*O,e[14]=(x*c*i-a*M*i-x*n*u+t*M*u+a*n*v-t*c*v)*O,e[15]=(a*p*i-f*c*i+f*n*u-t*p*u-a*n*m+t*c*m)*O,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,a=e.x,c=e.y,u=e.z,h=s*a,f=s*c;return this.set(h*a+n,h*c-i*u,h*u+i*c,0,h*c+i*u,f*c+n,f*u-i*a,0,h*u-i*c,f*u+i*a,s*u*u+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,a){return this.set(1,n,s,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,a=t._y,c=t._z,u=t._w,h=s+s,f=a+a,p=c+c,m=s*h,g=s*f,x=s*p,M=a*f,v=a*p,_=c*p,A=u*h,w=u*f,b=u*p,B=n.x,U=n.y,O=n.z;return i[0]=(1-(M+_))*B,i[1]=(g+b)*B,i[2]=(x-w)*B,i[3]=0,i[4]=(g-b)*U,i[5]=(1-(m+_))*U,i[6]=(v+A)*U,i[7]=0,i[8]=(x+w)*O,i[9]=(v-A)*O,i[10]=(1-(m+M))*O,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=Cs.set(i[0],i[1],i[2]).length();const a=Cs.set(i[4],i[5],i[6]).length(),c=Cs.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],fi.copy(this);const h=1/s,f=1/a,p=1/c;return fi.elements[0]*=h,fi.elements[1]*=h,fi.elements[2]*=h,fi.elements[4]*=f,fi.elements[5]*=f,fi.elements[6]*=f,fi.elements[8]*=p,fi.elements[9]*=p,fi.elements[10]*=p,t.setFromRotationMatrix(fi),n.x=s,n.y=a,n.z=c,this}makePerspective(e,t,n,i,s,a,c=Ki){const u=this.elements,h=2*s/(t-e),f=2*s/(n-i),p=(t+e)/(t-e),m=(n+i)/(n-i);let g,x;if(c===Ki)g=-(a+s)/(a-s),x=-2*a*s/(a-s);else if(c===Oc)g=-a/(a-s),x=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+c);return u[0]=h,u[4]=0,u[8]=p,u[12]=0,u[1]=0,u[5]=f,u[9]=m,u[13]=0,u[2]=0,u[6]=0,u[10]=g,u[14]=x,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,n,i,s,a,c=Ki){const u=this.elements,h=1/(t-e),f=1/(n-i),p=1/(a-s),m=(t+e)*h,g=(n+i)*f;let x,M;if(c===Ki)x=(a+s)*p,M=-2*p;else if(c===Oc)x=s*p,M=-1*p;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+c);return u[0]=2*h,u[4]=0,u[8]=0,u[12]=-m,u[1]=0,u[5]=2*f,u[9]=0,u[13]=-g,u[2]=0,u[6]=0,u[10]=M,u[14]=-x,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Cs=new F,fi=new ot,TE=new F(0,0,0),EE=new F(1,1,1),hr=new F,Ka=new F,ti=new F,Hp=new ot,Vp=new en;class xi{constructor(e=0,t=0,n=0,i=xi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],a=i[4],c=i[8],u=i[1],h=i[5],f=i[9],p=i[2],m=i[6],g=i[10];switch(t){case"XYZ":this._y=Math.asin(wn(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-f,g),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(m,h),this._z=0);break;case"YXZ":this._x=Math.asin(-wn(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(c,g),this._z=Math.atan2(u,h)):(this._y=Math.atan2(-p,s),this._z=0);break;case"ZXY":this._x=Math.asin(wn(m,-1,1)),Math.abs(m)<.9999999?(this._y=Math.atan2(-p,g),this._z=Math.atan2(-a,h)):(this._y=0,this._z=Math.atan2(u,s));break;case"ZYX":this._y=Math.asin(-wn(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(m,g),this._z=Math.atan2(u,s)):(this._x=0,this._z=Math.atan2(-a,h));break;case"YZX":this._z=Math.asin(wn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(-f,h),this._y=Math.atan2(-p,s)):(this._x=0,this._y=Math.atan2(c,g));break;case"XZY":this._z=Math.asin(-wn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(m,h),this._y=Math.atan2(c,s)):(this._x=Math.atan2(-f,g),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Hp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Hp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Vp.setFromEuler(this),this.setFromQuaternion(Vp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}xi.DEFAULT_ORDER="XYZ";class yd{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let AE=0;const Gp=new F,Is=new en,Vi=new ot,$a=new F,No=new F,wE=new F,PE=new en,Wp=new F(1,0,0),jp=new F(0,1,0),Xp=new F(0,0,1),qp={type:"added"},RE={type:"removed"},Ls={type:"childadded",child:null},Lu={type:"childremoved",child:null};class Jt extends Tr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:AE++}),this.uuid=yi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Jt.DEFAULT_UP.clone();const e=new F,t=new xi,n=new en,i=new F(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new ot},normalMatrix:{value:new gt}}),this.matrix=new ot,this.matrixWorld=new ot,this.matrixAutoUpdate=Jt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Jt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new yd,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.multiply(Is),this}rotateOnWorldAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.premultiply(Is),this}rotateX(e){return this.rotateOnAxis(Wp,e)}rotateY(e){return this.rotateOnAxis(jp,e)}rotateZ(e){return this.rotateOnAxis(Xp,e)}translateOnAxis(e,t){return Gp.copy(e).applyQuaternion(this.quaternion),this.position.add(Gp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Wp,e)}translateY(e){return this.translateOnAxis(jp,e)}translateZ(e){return this.translateOnAxis(Xp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Vi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?$a.copy(e):$a.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),No.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Vi.lookAt(No,$a,this.up):Vi.lookAt($a,No,this.up),this.quaternion.setFromRotationMatrix(Vi),i&&(Vi.extractRotation(i.matrixWorld),Is.setFromRotationMatrix(Vi),this.quaternion.premultiply(Is.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(RE),Lu.child=e,this.dispatchEvent(Lu),Lu.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Vi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Vi.multiply(e.parent.matrixWorld)),e.applyMatrix4(Vi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,e,wE),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,PE,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(c=>({boxInitialized:c.boxInitialized,boxMin:c.box.min.toArray(),boxMax:c.box.max.toArray(),sphereInitialized:c.sphereInitialized,sphereRadius:c.sphere.radius,sphereCenter:c.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(c,u){return c[u.uuid]===void 0&&(c[u.uuid]=u.toJSON(e)),u.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const c=this.geometry.parameters;if(c!==void 0&&c.shapes!==void 0){const u=c.shapes;if(Array.isArray(u))for(let h=0,f=u.length;h<f;h++){const p=u[h];s(e.shapes,p)}else s(e.shapes,u)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const c=[];for(let u=0,h=this.material.length;u<h;u++)c.push(s(e.materials,this.material[u]));i.material=c}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let c=0;c<this.children.length;c++)i.children.push(this.children[c].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let c=0;c<this.animations.length;c++){const u=this.animations[c];i.animations.push(s(e.animations,u))}}if(t){const c=a(e.geometries),u=a(e.materials),h=a(e.textures),f=a(e.images),p=a(e.shapes),m=a(e.skeletons),g=a(e.animations),x=a(e.nodes);c.length>0&&(n.geometries=c),u.length>0&&(n.materials=u),h.length>0&&(n.textures=h),f.length>0&&(n.images=f),p.length>0&&(n.shapes=p),m.length>0&&(n.skeletons=m),g.length>0&&(n.animations=g),x.length>0&&(n.nodes=x)}return n.object=i,n;function a(c){const u=[];for(const h in c){const f=c[h];delete f.metadata,u.push(f)}return u}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}Jt.DEFAULT_UP=new F(0,1,0);Jt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Jt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const pi=new F,Gi=new F,Du=new F,Wi=new F,Ds=new F,Ns=new F,Yp=new F,Nu=new F,Ou=new F,Uu=new F,Fu=new Dt,Bu=new Dt,ku=new Dt;class _i{constructor(e=new F,t=new F,n=new F){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),pi.subVectors(e,t),i.cross(pi);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){pi.subVectors(i,t),Gi.subVectors(n,t),Du.subVectors(e,t);const a=pi.dot(pi),c=pi.dot(Gi),u=pi.dot(Du),h=Gi.dot(Gi),f=Gi.dot(Du),p=a*h-c*c;if(p===0)return s.set(0,0,0),null;const m=1/p,g=(h*u-c*f)*m,x=(a*f-c*u)*m;return s.set(1-g-x,x,g)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,Wi)===null?!1:Wi.x>=0&&Wi.y>=0&&Wi.x+Wi.y<=1}static getInterpolation(e,t,n,i,s,a,c,u){return this.getBarycoord(e,t,n,i,Wi)===null?(u.x=0,u.y=0,"z"in u&&(u.z=0),"w"in u&&(u.w=0),null):(u.setScalar(0),u.addScaledVector(s,Wi.x),u.addScaledVector(a,Wi.y),u.addScaledVector(c,Wi.z),u)}static getInterpolatedAttribute(e,t,n,i,s,a){return Fu.setScalar(0),Bu.setScalar(0),ku.setScalar(0),Fu.fromBufferAttribute(e,t),Bu.fromBufferAttribute(e,n),ku.fromBufferAttribute(e,i),a.setScalar(0),a.addScaledVector(Fu,s.x),a.addScaledVector(Bu,s.y),a.addScaledVector(ku,s.z),a}static isFrontFacing(e,t,n,i){return pi.subVectors(n,t),Gi.subVectors(e,t),pi.cross(Gi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return pi.subVectors(this.c,this.b),Gi.subVectors(this.a,this.b),pi.cross(Gi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return _i.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return _i.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return _i.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return _i.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return _i.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let a,c;Ds.subVectors(i,n),Ns.subVectors(s,n),Nu.subVectors(e,n);const u=Ds.dot(Nu),h=Ns.dot(Nu);if(u<=0&&h<=0)return t.copy(n);Ou.subVectors(e,i);const f=Ds.dot(Ou),p=Ns.dot(Ou);if(f>=0&&p<=f)return t.copy(i);const m=u*p-f*h;if(m<=0&&u>=0&&f<=0)return a=u/(u-f),t.copy(n).addScaledVector(Ds,a);Uu.subVectors(e,s);const g=Ds.dot(Uu),x=Ns.dot(Uu);if(x>=0&&g<=x)return t.copy(s);const M=g*h-u*x;if(M<=0&&h>=0&&x<=0)return c=h/(h-x),t.copy(n).addScaledVector(Ns,c);const v=f*x-g*p;if(v<=0&&p-f>=0&&g-x>=0)return Yp.subVectors(s,i),c=(p-f)/(p-f+(g-x)),t.copy(i).addScaledVector(Yp,c);const _=1/(v+M+m);return a=M*_,c=m*_,t.copy(n).addScaledVector(Ds,a).addScaledVector(Ns,c)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Ig={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},dr={h:0,s:0,l:0},Za={h:0,s:0,l:0};function zu(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class $e{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=bn){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,wt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=wt.workingColorSpace){return this.r=e,this.g=t,this.b=n,wt.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=wt.workingColorSpace){if(e=vd(e,1),t=wn(t,0,1),n=wn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=zu(a,s,e+1/3),this.g=zu(a,s,e),this.b=zu(a,s,e-1/3)}return wt.toWorkingColorSpace(this,i),this}setStyle(e,t=bn){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=i[1],c=i[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=bn){const n=Ig[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Zi(e.r),this.g=Zi(e.g),this.b=Zi(e.b),this}copyLinearToSRGB(e){return this.r=Ys(e.r),this.g=Ys(e.g),this.b=Ys(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=bn){return wt.fromWorkingColorSpace(Dn.copy(this),e),Math.round(wn(Dn.r*255,0,255))*65536+Math.round(wn(Dn.g*255,0,255))*256+Math.round(wn(Dn.b*255,0,255))}getHexString(e=bn){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=wt.workingColorSpace){wt.fromWorkingColorSpace(Dn.copy(this),t);const n=Dn.r,i=Dn.g,s=Dn.b,a=Math.max(n,i,s),c=Math.min(n,i,s);let u,h;const f=(c+a)/2;if(c===a)u=0,h=0;else{const p=a-c;switch(h=f<=.5?p/(a+c):p/(2-a-c),a){case n:u=(i-s)/p+(i<s?6:0);break;case i:u=(s-n)/p+2;break;case s:u=(n-i)/p+4;break}u/=6}return e.h=u,e.s=h,e.l=f,e}getRGB(e,t=wt.workingColorSpace){return wt.fromWorkingColorSpace(Dn.copy(this),t),e.r=Dn.r,e.g=Dn.g,e.b=Dn.b,e}getStyle(e=bn){wt.fromWorkingColorSpace(Dn.copy(this),e);const t=Dn.r,n=Dn.g,i=Dn.b;return e!==bn?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(dr),this.setHSL(dr.h+e,dr.s+t,dr.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(dr),e.getHSL(Za);const n=$o(dr.h,Za.h,t),i=$o(dr.s,Za.s,t),s=$o(dr.l,Za.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Dn=new $e;$e.NAMES=Ig;let CE=0;class Ai extends Tr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:CE++}),this.uuid=yi(),this.name="",this.blending=Xs,this.side=Ji,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=gh,this.blendDst=_h,this.blendEquation=ns,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new $e(0,0,0),this.blendAlpha=0,this.depthFunc=$s,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Ip,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Es,this.stencilZFail=Es,this.stencilZPass=Es,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Xs&&(n.blending=this.blending),this.side!==Ji&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==gh&&(n.blendSrc=this.blendSrc),this.blendDst!==_h&&(n.blendDst=this.blendDst),this.blendEquation!==ns&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==$s&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Ip&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Es&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Es&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Es&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const a=[];for(const c in s){const u=s[c];delete u.metadata,a.push(u)}return a}if(t){const s=i(e.textures),a=i(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class ui extends Ai{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new $e(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new xi,this.combine=hg,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const un=new F,Ja=new tt;class an{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=ed,this.updateRanges=[],this.gpuType=vi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Ja.fromBufferAttribute(this,t),Ja.applyMatrix3(e),this.setXY(t,Ja.x,Ja.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)un.fromBufferAttribute(this,t),un.applyMatrix3(e),this.setXYZ(t,un.x,un.y,un.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)un.fromBufferAttribute(this,t),un.applyMatrix4(e),this.setXYZ(t,un.x,un.y,un.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)un.fromBufferAttribute(this,t),un.applyNormalMatrix(e),this.setXYZ(t,un.x,un.y,un.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)un.fromBufferAttribute(this,t),un.transformDirection(e),this.setXYZ(t,un.x,un.y,un.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=gi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=kt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=gi(t,this.array)),t}setX(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=gi(t,this.array)),t}setY(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=gi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=gi(t,this.array)),t}setW(e,t){return this.normalized&&(t=kt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),i=kt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),i=kt(i,this.array),s=kt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==ed&&(e.usage=this.usage),e}}class Lg extends an{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Dg extends an{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Xt extends an{constructor(e,t,n){super(new Float32Array(e),t,n)}}let IE=0;const ai=new ot,Hu=new Jt,Os=new F,ni=new er,Oo=new er,xn=new F;class mn extends Tr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:IE++}),this.uuid=yi(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Pg(e)?Dg:Lg)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new gt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return ai.makeRotationFromQuaternion(e),this.applyMatrix4(ai),this}rotateX(e){return ai.makeRotationX(e),this.applyMatrix4(ai),this}rotateY(e){return ai.makeRotationY(e),this.applyMatrix4(ai),this}rotateZ(e){return ai.makeRotationZ(e),this.applyMatrix4(ai),this}translate(e,t,n){return ai.makeTranslation(e,t,n),this.applyMatrix4(ai),this}scale(e,t,n){return ai.makeScale(e,t,n),this.applyMatrix4(ai),this}lookAt(e){return Hu.lookAt(e),Hu.updateMatrix(),this.applyMatrix4(Hu.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Os).negate(),this.translate(Os.x,Os.y,Os.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let i=0,s=e.length;i<s;i++){const a=e[i];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new Xt(n,3))}else{for(let n=0,i=t.count;n<i;n++){const s=e[n];t.setXYZ(n,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new er);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new F(-1/0,-1/0,-1/0),new F(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];ni.setFromBufferAttribute(s),this.morphTargetsRelative?(xn.addVectors(this.boundingBox.min,ni.min),this.boundingBox.expandByPoint(xn),xn.addVectors(this.boundingBox.max,ni.max),this.boundingBox.expandByPoint(xn)):(this.boundingBox.expandByPoint(ni.min),this.boundingBox.expandByPoint(ni.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new wi);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new F,1/0);return}if(e){const n=this.boundingSphere.center;if(ni.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const c=t[s];Oo.setFromBufferAttribute(c),this.morphTargetsRelative?(xn.addVectors(ni.min,Oo.min),ni.expandByPoint(xn),xn.addVectors(ni.max,Oo.max),ni.expandByPoint(xn)):(ni.expandByPoint(Oo.min),ni.expandByPoint(Oo.max))}ni.getCenter(n);let i=0;for(let s=0,a=e.count;s<a;s++)xn.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(xn));if(t)for(let s=0,a=t.length;s<a;s++){const c=t[s],u=this.morphTargetsRelative;for(let h=0,f=c.count;h<f;h++)xn.fromBufferAttribute(c,h),u&&(Os.fromBufferAttribute(e,h),xn.add(Os)),i=Math.max(i,n.distanceToSquared(xn))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new an(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),c=[],u=[];for(let H=0;H<n.count;H++)c[H]=new F,u[H]=new F;const h=new F,f=new F,p=new F,m=new tt,g=new tt,x=new tt,M=new F,v=new F;function _(H,L,P){h.fromBufferAttribute(n,H),f.fromBufferAttribute(n,L),p.fromBufferAttribute(n,P),m.fromBufferAttribute(s,H),g.fromBufferAttribute(s,L),x.fromBufferAttribute(s,P),f.sub(h),p.sub(h),g.sub(m),x.sub(m);const V=1/(g.x*x.y-x.x*g.y);isFinite(V)&&(M.copy(f).multiplyScalar(x.y).addScaledVector(p,-g.y).multiplyScalar(V),v.copy(p).multiplyScalar(g.x).addScaledVector(f,-x.x).multiplyScalar(V),c[H].add(M),c[L].add(M),c[P].add(M),u[H].add(v),u[L].add(v),u[P].add(v))}let A=this.groups;A.length===0&&(A=[{start:0,count:e.count}]);for(let H=0,L=A.length;H<L;++H){const P=A[H],V=P.start,ee=P.count;for(let Q=V,ae=V+ee;Q<ae;Q+=3)_(e.getX(Q+0),e.getX(Q+1),e.getX(Q+2))}const w=new F,b=new F,B=new F,U=new F;function O(H){B.fromBufferAttribute(i,H),U.copy(B);const L=c[H];w.copy(L),w.sub(B.multiplyScalar(B.dot(L))).normalize(),b.crossVectors(U,L);const V=b.dot(u[H])<0?-1:1;a.setXYZW(H,w.x,w.y,w.z,V)}for(let H=0,L=A.length;H<L;++H){const P=A[H],V=P.start,ee=P.count;for(let Q=V,ae=V+ee;Q<ae;Q+=3)O(e.getX(Q+0)),O(e.getX(Q+1)),O(e.getX(Q+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new an(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let m=0,g=n.count;m<g;m++)n.setXYZ(m,0,0,0);const i=new F,s=new F,a=new F,c=new F,u=new F,h=new F,f=new F,p=new F;if(e)for(let m=0,g=e.count;m<g;m+=3){const x=e.getX(m+0),M=e.getX(m+1),v=e.getX(m+2);i.fromBufferAttribute(t,x),s.fromBufferAttribute(t,M),a.fromBufferAttribute(t,v),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),c.fromBufferAttribute(n,x),u.fromBufferAttribute(n,M),h.fromBufferAttribute(n,v),c.add(f),u.add(f),h.add(f),n.setXYZ(x,c.x,c.y,c.z),n.setXYZ(M,u.x,u.y,u.z),n.setXYZ(v,h.x,h.y,h.z)}else for(let m=0,g=t.count;m<g;m+=3)i.fromBufferAttribute(t,m+0),s.fromBufferAttribute(t,m+1),a.fromBufferAttribute(t,m+2),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),n.setXYZ(m+0,f.x,f.y,f.z),n.setXYZ(m+1,f.x,f.y,f.z),n.setXYZ(m+2,f.x,f.y,f.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)xn.fromBufferAttribute(e,t),xn.normalize(),e.setXYZ(t,xn.x,xn.y,xn.z)}toNonIndexed(){function e(c,u){const h=c.array,f=c.itemSize,p=c.normalized,m=new h.constructor(u.length*f);let g=0,x=0;for(let M=0,v=u.length;M<v;M++){c.isInterleavedBufferAttribute?g=u[M]*c.data.stride+c.offset:g=u[M]*f;for(let _=0;_<f;_++)m[x++]=h[g++]}return new an(m,f,p)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new mn,n=this.index.array,i=this.attributes;for(const c in i){const u=i[c],h=e(u,n);t.setAttribute(c,h)}const s=this.morphAttributes;for(const c in s){const u=[],h=s[c];for(let f=0,p=h.length;f<p;f++){const m=h[f],g=e(m,n);u.push(g)}t.morphAttributes[c]=u}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];t.addGroup(h.start,h.count,h.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const u=this.parameters;for(const h in u)u[h]!==void 0&&(e[h]=u[h]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const u in n){const h=n[u];e.data.attributes[u]=h.toJSON(e.data)}const i={};let s=!1;for(const u in this.morphAttributes){const h=this.morphAttributes[u],f=[];for(let p=0,m=h.length;p<m;p++){const g=h[p];f.push(g.toJSON(e.data))}f.length>0&&(i[u]=f,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const c=this.boundingSphere;return c!==null&&(e.data.boundingSphere={center:c.center.toArray(),radius:c.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const h in i){const f=i[h];this.setAttribute(h,f.clone(t))}const s=e.morphAttributes;for(const h in s){const f=[],p=s[h];for(let m=0,g=p.length;m<g;m++)f.push(p[m].clone(t));this.morphAttributes[h]=f}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let h=0,f=a.length;h<f;h++){const p=a[h];this.addGroup(p.start,p.count,p.materialIndex)}const c=e.boundingBox;c!==null&&(this.boundingBox=c.clone());const u=e.boundingSphere;return u!==null&&(this.boundingSphere=u.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Kp=new ot,Yr=new oo,Qa=new wi,$p=new F,ec=new F,tc=new F,nc=new F,Vu=new F,ic=new F,Zp=new F,rc=new F;class Ee extends Jt{constructor(e=new mn,t=new ui){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const c=this.morphTargetInfluences;if(s&&c){ic.set(0,0,0);for(let u=0,h=s.length;u<h;u++){const f=c[u],p=s[u];f!==0&&(Vu.fromBufferAttribute(p,e),a?ic.addScaledVector(Vu,f):ic.addScaledVector(Vu.sub(t),f))}t.add(ic)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Qa.copy(n.boundingSphere),Qa.applyMatrix4(s),Yr.copy(e.ray).recast(e.near),!(Qa.containsPoint(Yr.origin)===!1&&(Yr.intersectSphere(Qa,$p)===null||Yr.origin.distanceToSquared($p)>(e.far-e.near)**2))&&(Kp.copy(s).invert(),Yr.copy(e.ray).applyMatrix4(Kp),!(n.boundingBox!==null&&Yr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Yr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,a=this.material,c=s.index,u=s.attributes.position,h=s.attributes.uv,f=s.attributes.uv1,p=s.attributes.normal,m=s.groups,g=s.drawRange;if(c!==null)if(Array.isArray(a))for(let x=0,M=m.length;x<M;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),w=Math.min(c.count,Math.min(v.start+v.count,g.start+g.count));for(let b=A,B=w;b<B;b+=3){const U=c.getX(b),O=c.getX(b+1),H=c.getX(b+2);i=sc(this,_,e,n,h,f,p,U,O,H),i&&(i.faceIndex=Math.floor(b/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),M=Math.min(c.count,g.start+g.count);for(let v=x,_=M;v<_;v+=3){const A=c.getX(v),w=c.getX(v+1),b=c.getX(v+2);i=sc(this,a,e,n,h,f,p,A,w,b),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}else if(u!==void 0)if(Array.isArray(a))for(let x=0,M=m.length;x<M;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),w=Math.min(u.count,Math.min(v.start+v.count,g.start+g.count));for(let b=A,B=w;b<B;b+=3){const U=b,O=b+1,H=b+2;i=sc(this,_,e,n,h,f,p,U,O,H),i&&(i.faceIndex=Math.floor(b/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),M=Math.min(u.count,g.start+g.count);for(let v=x,_=M;v<_;v+=3){const A=v,w=v+1,b=v+2;i=sc(this,a,e,n,h,f,p,A,w,b),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}}}function LE(r,e,t,n,i,s,a,c){let u;if(e.side===qn?u=n.intersectTriangle(a,s,i,!0,c):u=n.intersectTriangle(i,s,a,e.side===Ji,c),u===null)return null;rc.copy(c),rc.applyMatrix4(r.matrixWorld);const h=t.ray.origin.distanceTo(rc);return h<t.near||h>t.far?null:{distance:h,point:rc.clone(),object:r}}function sc(r,e,t,n,i,s,a,c,u,h){r.getVertexPosition(c,ec),r.getVertexPosition(u,tc),r.getVertexPosition(h,nc);const f=LE(r,e,t,n,ec,tc,nc,Zp);if(f){const p=new F;_i.getBarycoord(Zp,ec,tc,nc,p),i&&(f.uv=_i.getInterpolatedAttribute(i,c,u,h,p,new tt)),s&&(f.uv1=_i.getInterpolatedAttribute(s,c,u,h,p,new tt)),a&&(f.normal=_i.getInterpolatedAttribute(a,c,u,h,p,new F),f.normal.dot(n.direction)>0&&f.normal.multiplyScalar(-1));const m={a:c,b:u,c:h,normal:new F,materialIndex:0};_i.getNormal(ec,tc,nc,m.normal),f.face=m,f.barycoord=p}return f}class sn extends mn{constructor(e=1,t=1,n=1,i=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:a};const c=this;i=Math.floor(i),s=Math.floor(s),a=Math.floor(a);const u=[],h=[],f=[],p=[];let m=0,g=0;x("z","y","x",-1,-1,n,t,e,a,s,0),x("z","y","x",1,-1,n,t,-e,a,s,1),x("x","z","y",1,1,e,n,t,i,a,2),x("x","z","y",1,-1,e,n,-t,i,a,3),x("x","y","z",1,-1,e,t,n,i,s,4),x("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(u),this.setAttribute("position",new Xt(h,3)),this.setAttribute("normal",new Xt(f,3)),this.setAttribute("uv",new Xt(p,2));function x(M,v,_,A,w,b,B,U,O,H,L){const P=b/O,V=B/H,ee=b/2,Q=B/2,ae=U/2,ce=O+1,J=H+1;let de=0,re=0;const _e=new F;for(let Me=0;Me<J;Me++){const Ue=Me*V-Q;for(let Je=0;Je<ce;Je++){const pt=Je*P-ee;_e[M]=pt*A,_e[v]=Ue*w,_e[_]=ae,h.push(_e.x,_e.y,_e.z),_e[M]=0,_e[v]=0,_e[_]=U>0?1:-1,f.push(_e.x,_e.y,_e.z),p.push(Je/O),p.push(1-Me/H),de+=1}}for(let Me=0;Me<H;Me++)for(let Ue=0;Ue<O;Ue++){const Je=m+Ue+ce*Me,pt=m+Ue+ce*(Me+1),le=m+(Ue+1)+ce*(Me+1),pe=m+(Ue+1)+ce*Me;u.push(Je,pt,pe),u.push(pt,le,pe),re+=6}c.addGroup(g,re,L),g+=re,m+=de}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new sn(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function io(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Bn(r){const e={};for(let t=0;t<r.length;t++){const n=io(r[t]);for(const i in n)e[i]=n[i]}return e}function DE(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function Ng(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:wt.workingColorSpace}const NE={clone:io,merge:Bn};var OE=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,UE=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Mr extends Ai{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=OE,this.fragmentShader=UE,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=io(e.uniforms),this.uniformsGroups=DE(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Og extends Jt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new ot,this.projectionMatrix=new ot,this.projectionMatrixInverse=new ot,this.coordinateSystem=Ki}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const fr=new F,Jp=new tt,Qp=new tt;class kn extends Og{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=no*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Ko*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return no*2*Math.atan(Math.tan(Ko*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){fr.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(fr.x,fr.y).multiplyScalar(-e/fr.z),fr.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(fr.x,fr.y).multiplyScalar(-e/fr.z)}getViewSize(e,t){return this.getViewBounds(e,Jp,Qp),t.subVectors(Qp,Jp)}setViewOffset(e,t,n,i,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Ko*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const u=a.fullWidth,h=a.fullHeight;s+=a.offsetX*i/u,t-=a.offsetY*n/h,i*=a.width/u,n*=a.height/h}const c=this.filmOffset;c!==0&&(s+=e*c/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Us=-90,Fs=1;class FE extends Jt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new kn(Us,Fs,e,t);i.layers=this.layers,this.add(i);const s=new kn(Us,Fs,e,t);s.layers=this.layers,this.add(s);const a=new kn(Us,Fs,e,t);a.layers=this.layers,this.add(a);const c=new kn(Us,Fs,e,t);c.layers=this.layers,this.add(c);const u=new kn(Us,Fs,e,t);u.layers=this.layers,this.add(u);const h=new kn(Us,Fs,e,t);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,a,c,u]=t;for(const h of t)this.remove(h);if(e===Ki)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),c.up.set(0,1,0),c.lookAt(0,0,1),u.up.set(0,1,0),u.lookAt(0,0,-1);else if(e===Oc)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),c.up.set(0,-1,0),c.lookAt(0,0,1),u.up.set(0,-1,0),u.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const h of t)this.add(h),h.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,c,u,h,f]=this.children,p=e.getRenderTarget(),m=e.getActiveCubeFace(),g=e.getActiveMipmapLevel(),x=e.xr.enabled;e.xr.enabled=!1;const M=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,c),e.setRenderTarget(n,3,i),e.render(t,u),e.setRenderTarget(n,4,i),e.render(t,h),n.texture.generateMipmaps=M,e.setRenderTarget(n,5,i),e.render(t,f),e.setRenderTarget(p,m,g),e.xr.enabled=x,n.texture.needsPMREMUpdate=!0}}class Ug extends Sn{constructor(e,t,n,i,s,a,c,u,h,f){e=e!==void 0?e:[],t=t!==void 0?t:Zs,super(e,t,n,i,s,a,c,u,h,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class BE extends os{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Ug(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ii}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},i=new sn(5,5,5),s=new Mr({name:"CubemapFromEquirect",uniforms:io(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:qn,blending:br});s.uniforms.tEquirect.value=t;const a=new Ee(i,s),c=t.minFilter;return t.minFilter===Yi&&(t.minFilter=ii),new FE(1,10,this).update(e,a),t.minFilter=c,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(s)}}const Gu=new F,kE=new F,zE=new gt;class _r{constructor(e=new F(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=Gu.subVectors(n,t).cross(kE.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Gu),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||zE.getNormalMatrix(e),i=this.coplanarPoint(Gu).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Kr=new wi,oc=new F;class xd{constructor(e=new _r,t=new _r,n=new _r,i=new _r,s=new _r,a=new _r){this.planes=[e,t,n,i,s,a]}set(e,t,n,i,s,a){const c=this.planes;return c[0].copy(e),c[1].copy(t),c[2].copy(n),c[3].copy(i),c[4].copy(s),c[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Ki){const n=this.planes,i=e.elements,s=i[0],a=i[1],c=i[2],u=i[3],h=i[4],f=i[5],p=i[6],m=i[7],g=i[8],x=i[9],M=i[10],v=i[11],_=i[12],A=i[13],w=i[14],b=i[15];if(n[0].setComponents(u-s,m-h,v-g,b-_).normalize(),n[1].setComponents(u+s,m+h,v+g,b+_).normalize(),n[2].setComponents(u+a,m+f,v+x,b+A).normalize(),n[3].setComponents(u-a,m-f,v-x,b-A).normalize(),n[4].setComponents(u-c,m-p,v-M,b-w).normalize(),t===Ki)n[5].setComponents(u+c,m+p,v+M,b+w).normalize();else if(t===Oc)n[5].setComponents(c,p,M,w).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Kr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Kr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Kr)}intersectsSprite(e){return Kr.center.set(0,0,0),Kr.radius=.7071067811865476,Kr.applyMatrix4(e.matrixWorld),this.intersectsSphere(Kr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(oc.x=i.normal.x>0?e.max.x:e.min.x,oc.y=i.normal.y>0?e.max.y:e.min.y,oc.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(oc)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Fg(){let r=null,e=!1,t=null,n=null;function i(s,a){t(s,a),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function HE(r){const e=new WeakMap;function t(c,u){const h=c.array,f=c.usage,p=h.byteLength,m=r.createBuffer();r.bindBuffer(u,m),r.bufferData(u,h,f),c.onUploadCallback();let g;if(h instanceof Float32Array)g=r.FLOAT;else if(h instanceof Uint16Array)c.isFloat16BufferAttribute?g=r.HALF_FLOAT:g=r.UNSIGNED_SHORT;else if(h instanceof Int16Array)g=r.SHORT;else if(h instanceof Uint32Array)g=r.UNSIGNED_INT;else if(h instanceof Int32Array)g=r.INT;else if(h instanceof Int8Array)g=r.BYTE;else if(h instanceof Uint8Array)g=r.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)g=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:m,type:g,bytesPerElement:h.BYTES_PER_ELEMENT,version:c.version,size:p}}function n(c,u,h){const f=u.array,p=u.updateRanges;if(r.bindBuffer(h,c),p.length===0)r.bufferSubData(h,0,f);else{p.sort((g,x)=>g.start-x.start);let m=0;for(let g=1;g<p.length;g++){const x=p[m],M=p[g];M.start<=x.start+x.count+1?x.count=Math.max(x.count,M.start+M.count-x.start):(++m,p[m]=M)}p.length=m+1;for(let g=0,x=p.length;g<x;g++){const M=p[g];r.bufferSubData(h,M.start*f.BYTES_PER_ELEMENT,f,M.start,M.count)}u.clearUpdateRanges()}u.onUploadCallback()}function i(c){return c.isInterleavedBufferAttribute&&(c=c.data),e.get(c)}function s(c){c.isInterleavedBufferAttribute&&(c=c.data);const u=e.get(c);u&&(r.deleteBuffer(u.buffer),e.delete(c))}function a(c,u){if(c.isInterleavedBufferAttribute&&(c=c.data),c.isGLBufferAttribute){const f=e.get(c);(!f||f.version<c.version)&&e.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}const h=e.get(c);if(h===void 0)e.set(c,t(c,u));else if(h.version<c.version){if(h.size!==c.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(h.buffer,c,u),h.version=c.version}}return{get:i,remove:s,update:a}}class ao extends mn{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,a=t/2,c=Math.floor(n),u=Math.floor(i),h=c+1,f=u+1,p=e/c,m=t/u,g=[],x=[],M=[],v=[];for(let _=0;_<f;_++){const A=_*m-a;for(let w=0;w<h;w++){const b=w*p-s;x.push(b,-A,0),M.push(0,0,1),v.push(w/c),v.push(1-_/u)}}for(let _=0;_<u;_++)for(let A=0;A<c;A++){const w=A+h*_,b=A+h*(_+1),B=A+1+h*(_+1),U=A+1+h*_;g.push(w,b,U),g.push(b,B,U)}this.setIndex(g),this.setAttribute("position",new Xt(x,3)),this.setAttribute("normal",new Xt(M,3)),this.setAttribute("uv",new Xt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ao(e.width,e.height,e.widthSegments,e.heightSegments)}}var VE=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,GE=`#ifdef USE_ALPHAHASH
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
#endif`,WE=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,jE=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,XE=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,qE=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,YE=`#ifdef USE_AOMAP
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
#endif`,KE=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,$E=`#ifdef USE_BATCHING
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
#endif`,JE=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,QE=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,eA=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,tA=`#ifdef USE_IRIDESCENCE
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
#endif`,nA=`#ifdef USE_BUMPMAP
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
#endif`,iA=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,rA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,sA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,oA=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,aA=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,cA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,lA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,uA=`#if defined( USE_COLOR_ALPHA )
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
#endif`,hA=`#define PI 3.141592653589793
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
} // validated`,dA=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,fA=`vec3 transformedNormal = objectNormal;
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
#endif`,pA=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,mA=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,gA=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,_A=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,vA="gl_FragColor = linearToOutputTexel( gl_FragColor );",yA=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,xA=`#ifdef USE_ENVMAP
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
#endif`,bA=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,SA=`#ifdef USE_ENVMAP
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
#endif`,MA=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,TA=`#ifdef USE_ENVMAP
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
#endif`,EA=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,AA=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,wA=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,PA=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,RA=`#ifdef USE_GRADIENTMAP
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
}`,CA=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,IA=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,LA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,DA=`uniform bool receiveShadow;
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
#endif`,NA=`#ifdef USE_ENVMAP
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
#endif`,OA=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,UA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,FA=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,BA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,kA=`PhysicalMaterial material;
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
#endif`,zA=`struct PhysicalMaterial {
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
}`,HA=`
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
#endif`,VA=`#if defined( RE_IndirectDiffuse )
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
#endif`,GA=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,WA=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,jA=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,XA=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,qA=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,YA=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,KA=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,$A=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,JA=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,QA=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,ew=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,tw=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,nw=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,iw=`#ifdef USE_MORPHTARGETS
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
#endif`,rw=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,sw=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,ow=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,aw=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,cw=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,lw=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,uw=`#ifdef USE_NORMALMAP
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
#endif`,hw=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,dw=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,fw=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,pw=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,mw=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,gw=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,_w=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,vw=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,yw=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,xw=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,bw=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,Sw=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,Mw=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Tw=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Ew=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,Aw=`float getShadowMask() {
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
}`,ww=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,Pw=`#ifdef USE_SKINNING
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
#endif`,Rw=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,Cw=`#ifdef USE_SKINNING
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
#endif`,Iw=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,Lw=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Dw=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,Nw=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,Ow=`#ifdef USE_TRANSMISSION
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
#endif`,Uw=`#ifdef USE_TRANSMISSION
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
#endif`,Fw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Bw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,kw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,zw=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const Hw=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,Vw=`uniform sampler2D t2D;
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
}`,Gw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Ww=`#ifdef ENVMAP_TYPE_CUBE
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
}`,jw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Xw=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,qw=`#include <common>
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
}`,Yw=`#if DEPTH_PACKING == 3200
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
}`,Kw=`#define DISTANCE
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
}`,$w=`#define DISTANCE
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
}`,Jw=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Qw=`uniform float scale;
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
}`,e1=`uniform vec3 diffuse;
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
}`,t1=`#include <common>
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
}`,n1=`uniform vec3 diffuse;
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
}`,i1=`#define LAMBERT
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
}`,r1=`#define LAMBERT
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
}`,s1=`#define MATCAP
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
}`,o1=`#define MATCAP
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
}`,a1=`#define NORMAL
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
}`,l1=`#define PHONG
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
}`,u1=`#define PHONG
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
}`,h1=`#define STANDARD
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
}`,d1=`#define STANDARD
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
}`,f1=`#define TOON
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
}`,p1=`#define TOON
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
}`,m1=`uniform float size;
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
}`,g1=`uniform vec3 diffuse;
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
}`,_1=`#include <common>
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
}`,v1=`uniform vec3 color;
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
}`,y1=`uniform float rotation;
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
}`,x1=`uniform vec3 diffuse;
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
}`,vt={alphahash_fragment:VE,alphahash_pars_fragment:GE,alphamap_fragment:WE,alphamap_pars_fragment:jE,alphatest_fragment:XE,alphatest_pars_fragment:qE,aomap_fragment:YE,aomap_pars_fragment:KE,batching_pars_vertex:$E,batching_vertex:ZE,begin_vertex:JE,beginnormal_vertex:QE,bsdfs:eA,iridescence_fragment:tA,bumpmap_pars_fragment:nA,clipping_planes_fragment:iA,clipping_planes_pars_fragment:rA,clipping_planes_pars_vertex:sA,clipping_planes_vertex:oA,color_fragment:aA,color_pars_fragment:cA,color_pars_vertex:lA,color_vertex:uA,common:hA,cube_uv_reflection_fragment:dA,defaultnormal_vertex:fA,displacementmap_pars_vertex:pA,displacementmap_vertex:mA,emissivemap_fragment:gA,emissivemap_pars_fragment:_A,colorspace_fragment:vA,colorspace_pars_fragment:yA,envmap_fragment:xA,envmap_common_pars_fragment:bA,envmap_pars_fragment:SA,envmap_pars_vertex:MA,envmap_physical_pars_fragment:NA,envmap_vertex:TA,fog_vertex:EA,fog_pars_vertex:AA,fog_fragment:wA,fog_pars_fragment:PA,gradientmap_pars_fragment:RA,lightmap_pars_fragment:CA,lights_lambert_fragment:IA,lights_lambert_pars_fragment:LA,lights_pars_begin:DA,lights_toon_fragment:OA,lights_toon_pars_fragment:UA,lights_phong_fragment:FA,lights_phong_pars_fragment:BA,lights_physical_fragment:kA,lights_physical_pars_fragment:zA,lights_fragment_begin:HA,lights_fragment_maps:VA,lights_fragment_end:GA,logdepthbuf_fragment:WA,logdepthbuf_pars_fragment:jA,logdepthbuf_pars_vertex:XA,logdepthbuf_vertex:qA,map_fragment:YA,map_pars_fragment:KA,map_particle_fragment:$A,map_particle_pars_fragment:ZA,metalnessmap_fragment:JA,metalnessmap_pars_fragment:QA,morphinstance_vertex:ew,morphcolor_vertex:tw,morphnormal_vertex:nw,morphtarget_pars_vertex:iw,morphtarget_vertex:rw,normal_fragment_begin:sw,normal_fragment_maps:ow,normal_pars_fragment:aw,normal_pars_vertex:cw,normal_vertex:lw,normalmap_pars_fragment:uw,clearcoat_normal_fragment_begin:hw,clearcoat_normal_fragment_maps:dw,clearcoat_pars_fragment:fw,iridescence_pars_fragment:pw,opaque_fragment:mw,packing:gw,premultiplied_alpha_fragment:_w,project_vertex:vw,dithering_fragment:yw,dithering_pars_fragment:xw,roughnessmap_fragment:bw,roughnessmap_pars_fragment:Sw,shadowmap_pars_fragment:Mw,shadowmap_pars_vertex:Tw,shadowmap_vertex:Ew,shadowmask_pars_fragment:Aw,skinbase_vertex:ww,skinning_pars_vertex:Pw,skinning_vertex:Rw,skinnormal_vertex:Cw,specularmap_fragment:Iw,specularmap_pars_fragment:Lw,tonemapping_fragment:Dw,tonemapping_pars_fragment:Nw,transmission_fragment:Ow,transmission_pars_fragment:Uw,uv_pars_fragment:Fw,uv_pars_vertex:Bw,uv_vertex:kw,worldpos_vertex:zw,background_vert:Hw,background_frag:Vw,backgroundCube_vert:Gw,backgroundCube_frag:Ww,cube_vert:jw,cube_frag:Xw,depth_vert:qw,depth_frag:Yw,distanceRGBA_vert:Kw,distanceRGBA_frag:$w,equirect_vert:Zw,equirect_frag:Jw,linedashed_vert:Qw,linedashed_frag:e1,meshbasic_vert:t1,meshbasic_frag:n1,meshlambert_vert:i1,meshlambert_frag:r1,meshmatcap_vert:s1,meshmatcap_frag:o1,meshnormal_vert:a1,meshnormal_frag:c1,meshphong_vert:l1,meshphong_frag:u1,meshphysical_vert:h1,meshphysical_frag:d1,meshtoon_vert:f1,meshtoon_frag:p1,points_vert:m1,points_frag:g1,shadow_vert:_1,shadow_frag:v1,sprite_vert:y1,sprite_frag:x1},Re={common:{diffuse:{value:new $e(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new gt},alphaMap:{value:null},alphaMapTransform:{value:new gt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new gt}},envmap:{envMap:{value:null},envMapRotation:{value:new gt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new gt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new gt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new gt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new gt},normalScale:{value:new tt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new gt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new gt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new gt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new gt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new $e(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new $e(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new gt},alphaTest:{value:0},uvTransform:{value:new gt}},sprite:{diffuse:{value:new $e(16777215)},opacity:{value:1},center:{value:new tt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new gt},alphaMap:{value:null},alphaMapTransform:{value:new gt},alphaTest:{value:0}}},Ti={basic:{uniforms:Bn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.fog]),vertexShader:vt.meshbasic_vert,fragmentShader:vt.meshbasic_frag},lambert:{uniforms:Bn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new $e(0)}}]),vertexShader:vt.meshlambert_vert,fragmentShader:vt.meshlambert_frag},phong:{uniforms:Bn([Re.common,Re.specularmap,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,Re.lights,{emissive:{value:new $e(0)},specular:{value:new $e(1118481)},shininess:{value:30}}]),vertexShader:vt.meshphong_vert,fragmentShader:vt.meshphong_frag},standard:{uniforms:Bn([Re.common,Re.envmap,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.roughnessmap,Re.metalnessmap,Re.fog,Re.lights,{emissive:{value:new $e(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:vt.meshphysical_vert,fragmentShader:vt.meshphysical_frag},toon:{uniforms:Bn([Re.common,Re.aomap,Re.lightmap,Re.emissivemap,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.gradientmap,Re.fog,Re.lights,{emissive:{value:new $e(0)}}]),vertexShader:vt.meshtoon_vert,fragmentShader:vt.meshtoon_frag},matcap:{uniforms:Bn([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,Re.fog,{matcap:{value:null}}]),vertexShader:vt.meshmatcap_vert,fragmentShader:vt.meshmatcap_frag},points:{uniforms:Bn([Re.points,Re.fog]),vertexShader:vt.points_vert,fragmentShader:vt.points_frag},dashed:{uniforms:Bn([Re.common,Re.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:vt.linedashed_vert,fragmentShader:vt.linedashed_frag},depth:{uniforms:Bn([Re.common,Re.displacementmap]),vertexShader:vt.depth_vert,fragmentShader:vt.depth_frag},normal:{uniforms:Bn([Re.common,Re.bumpmap,Re.normalmap,Re.displacementmap,{opacity:{value:1}}]),vertexShader:vt.meshnormal_vert,fragmentShader:vt.meshnormal_frag},sprite:{uniforms:Bn([Re.sprite,Re.fog]),vertexShader:vt.sprite_vert,fragmentShader:vt.sprite_frag},background:{uniforms:{uvTransform:{value:new gt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:vt.background_vert,fragmentShader:vt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new gt}},vertexShader:vt.backgroundCube_vert,fragmentShader:vt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:vt.cube_vert,fragmentShader:vt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:vt.equirect_vert,fragmentShader:vt.equirect_frag},distanceRGBA:{uniforms:Bn([Re.common,Re.displacementmap,{referencePosition:{value:new F},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:vt.distanceRGBA_vert,fragmentShader:vt.distanceRGBA_frag},shadow:{uniforms:Bn([Re.lights,Re.fog,{color:{value:new $e(0)},opacity:{value:1}}]),vertexShader:vt.shadow_vert,fragmentShader:vt.shadow_frag}};Ti.physical={uniforms:Bn([Ti.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new gt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new gt},clearcoatNormalScale:{value:new tt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new gt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new gt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new gt},sheen:{value:0},sheenColor:{value:new $e(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new gt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new gt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new gt},transmissionSamplerSize:{value:new tt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new gt},attenuationDistance:{value:0},attenuationColor:{value:new $e(0)},specularColor:{value:new $e(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new gt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new gt},anisotropyVector:{value:new tt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new gt}}]),vertexShader:vt.meshphysical_vert,fragmentShader:vt.meshphysical_frag};const ac={r:0,b:0,g:0},$r=new xi,b1=new ot;function S1(r,e,t,n,i,s,a){const c=new $e(0);let u=s===!0?0:1,h,f,p=null,m=0,g=null;function x(A){let w=A.isScene===!0?A.background:null;return w&&w.isTexture&&(w=(A.backgroundBlurriness>0?t:e).get(w)),w}function M(A){let w=!1;const b=x(A);b===null?_(c,u):b&&b.isColor&&(_(b,1),w=!0);const B=r.xr.getEnvironmentBlendMode();B==="additive"?n.buffers.color.setClear(0,0,0,1,a):B==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(r.autoClear||w)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function v(A,w){const b=x(w);b&&(b.isCubeTexture||b.mapping===kc)?(f===void 0&&(f=new Ee(new sn(1,1,1),new Mr({name:"BackgroundCubeMaterial",uniforms:io(Ti.backgroundCube.uniforms),vertexShader:Ti.backgroundCube.vertexShader,fragmentShader:Ti.backgroundCube.fragmentShader,side:qn,depthTest:!1,depthWrite:!1,fog:!1})),f.geometry.deleteAttribute("normal"),f.geometry.deleteAttribute("uv"),f.onBeforeRender=function(B,U,O){this.matrixWorld.copyPosition(O.matrixWorld)},Object.defineProperty(f.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(f)),$r.copy(w.backgroundRotation),$r.x*=-1,$r.y*=-1,$r.z*=-1,b.isCubeTexture&&b.isRenderTargetTexture===!1&&($r.y*=-1,$r.z*=-1),f.material.uniforms.envMap.value=b,f.material.uniforms.flipEnvMap.value=b.isCubeTexture&&b.isRenderTargetTexture===!1?-1:1,f.material.uniforms.backgroundBlurriness.value=w.backgroundBlurriness,f.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,f.material.uniforms.backgroundRotation.value.setFromMatrix4(b1.makeRotationFromEuler($r)),f.material.toneMapped=wt.getTransfer(b.colorSpace)!==Ht,(p!==b||m!==b.version||g!==r.toneMapping)&&(f.material.needsUpdate=!0,p=b,m=b.version,g=r.toneMapping),f.layers.enableAll(),A.unshift(f,f.geometry,f.material,0,0,null)):b&&b.isTexture&&(h===void 0&&(h=new Ee(new ao(2,2),new Mr({name:"BackgroundMaterial",uniforms:io(Ti.background.uniforms),vertexShader:Ti.background.vertexShader,fragmentShader:Ti.background.fragmentShader,side:Ji,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),Object.defineProperty(h.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(h)),h.material.uniforms.t2D.value=b,h.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,h.material.toneMapped=wt.getTransfer(b.colorSpace)!==Ht,b.matrixAutoUpdate===!0&&b.updateMatrix(),h.material.uniforms.uvTransform.value.copy(b.matrix),(p!==b||m!==b.version||g!==r.toneMapping)&&(h.material.needsUpdate=!0,p=b,m=b.version,g=r.toneMapping),h.layers.enableAll(),A.unshift(h,h.geometry,h.material,0,0,null))}function _(A,w){A.getRGB(ac,Ng(r)),n.buffers.color.setClear(ac.r,ac.g,ac.b,w,a)}return{getClearColor:function(){return c},setClearColor:function(A,w=1){c.set(A),u=w,_(c,u)},getClearAlpha:function(){return u},setClearAlpha:function(A){u=A,_(c,u)},render:M,addToRenderList:v}}function M1(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=m(null);let s=i,a=!1;function c(P,V,ee,Q,ae){let ce=!1;const J=p(Q,ee,V);s!==J&&(s=J,h(s.object)),ce=g(P,Q,ee,ae),ce&&x(P,Q,ee,ae),ae!==null&&e.update(ae,r.ELEMENT_ARRAY_BUFFER),(ce||a)&&(a=!1,b(P,V,ee,Q),ae!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(ae).buffer))}function u(){return r.createVertexArray()}function h(P){return r.bindVertexArray(P)}function f(P){return r.deleteVertexArray(P)}function p(P,V,ee){const Q=ee.wireframe===!0;let ae=n[P.id];ae===void 0&&(ae={},n[P.id]=ae);let ce=ae[V.id];ce===void 0&&(ce={},ae[V.id]=ce);let J=ce[Q];return J===void 0&&(J=m(u()),ce[Q]=J),J}function m(P){const V=[],ee=[],Q=[];for(let ae=0;ae<t;ae++)V[ae]=0,ee[ae]=0,Q[ae]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:V,enabledAttributes:ee,attributeDivisors:Q,object:P,attributes:{},index:null}}function g(P,V,ee,Q){const ae=s.attributes,ce=V.attributes;let J=0;const de=ee.getAttributes();for(const re in de)if(de[re].location>=0){const Me=ae[re];let Ue=ce[re];if(Ue===void 0&&(re==="instanceMatrix"&&P.instanceMatrix&&(Ue=P.instanceMatrix),re==="instanceColor"&&P.instanceColor&&(Ue=P.instanceColor)),Me===void 0||Me.attribute!==Ue||Ue&&Me.data!==Ue.data)return!0;J++}return s.attributesNum!==J||s.index!==Q}function x(P,V,ee,Q){const ae={},ce=V.attributes;let J=0;const de=ee.getAttributes();for(const re in de)if(de[re].location>=0){let Me=ce[re];Me===void 0&&(re==="instanceMatrix"&&P.instanceMatrix&&(Me=P.instanceMatrix),re==="instanceColor"&&P.instanceColor&&(Me=P.instanceColor));const Ue={};Ue.attribute=Me,Me&&Me.data&&(Ue.data=Me.data),ae[re]=Ue,J++}s.attributes=ae,s.attributesNum=J,s.index=Q}function M(){const P=s.newAttributes;for(let V=0,ee=P.length;V<ee;V++)P[V]=0}function v(P){_(P,0)}function _(P,V){const ee=s.newAttributes,Q=s.enabledAttributes,ae=s.attributeDivisors;ee[P]=1,Q[P]===0&&(r.enableVertexAttribArray(P),Q[P]=1),ae[P]!==V&&(r.vertexAttribDivisor(P,V),ae[P]=V)}function A(){const P=s.newAttributes,V=s.enabledAttributes;for(let ee=0,Q=V.length;ee<Q;ee++)V[ee]!==P[ee]&&(r.disableVertexAttribArray(ee),V[ee]=0)}function w(P,V,ee,Q,ae,ce,J){J===!0?r.vertexAttribIPointer(P,V,ee,ae,ce):r.vertexAttribPointer(P,V,ee,Q,ae,ce)}function b(P,V,ee,Q){M();const ae=Q.attributes,ce=ee.getAttributes(),J=V.defaultAttributeValues;for(const de in ce){const re=ce[de];if(re.location>=0){let _e=ae[de];if(_e===void 0&&(de==="instanceMatrix"&&P.instanceMatrix&&(_e=P.instanceMatrix),de==="instanceColor"&&P.instanceColor&&(_e=P.instanceColor)),_e!==void 0){const Me=_e.normalized,Ue=_e.itemSize,Je=e.get(_e);if(Je===void 0)continue;const pt=Je.buffer,le=Je.type,pe=Je.bytesPerElement,Fe=le===r.INT||le===r.UNSIGNED_INT||_e.gpuType===ld;if(_e.isInterleavedBufferAttribute){const Se=_e.data,qe=Se.stride,it=_e.offset;if(Se.isInstancedInterleavedBuffer){for(let at=0;at<re.locationSize;at++)_(re.location+at,Se.meshPerAttribute);P.isInstancedMesh!==!0&&Q._maxInstanceCount===void 0&&(Q._maxInstanceCount=Se.meshPerAttribute*Se.count)}else for(let at=0;at<re.locationSize;at++)v(re.location+at);r.bindBuffer(r.ARRAY_BUFFER,pt);for(let at=0;at<re.locationSize;at++)w(re.location+at,Ue/re.locationSize,le,Me,qe*pe,(it+Ue/re.locationSize*at)*pe,Fe)}else{if(_e.isInstancedBufferAttribute){for(let Se=0;Se<re.locationSize;Se++)_(re.location+Se,_e.meshPerAttribute);P.isInstancedMesh!==!0&&Q._maxInstanceCount===void 0&&(Q._maxInstanceCount=_e.meshPerAttribute*_e.count)}else for(let Se=0;Se<re.locationSize;Se++)v(re.location+Se);r.bindBuffer(r.ARRAY_BUFFER,pt);for(let Se=0;Se<re.locationSize;Se++)w(re.location+Se,Ue/re.locationSize,le,Me,Ue*pe,Ue/re.locationSize*Se*pe,Fe)}}else if(J!==void 0){const Me=J[de];if(Me!==void 0)switch(Me.length){case 2:r.vertexAttrib2fv(re.location,Me);break;case 3:r.vertexAttrib3fv(re.location,Me);break;case 4:r.vertexAttrib4fv(re.location,Me);break;default:r.vertexAttrib1fv(re.location,Me)}}}}A()}function B(){H();for(const P in n){const V=n[P];for(const ee in V){const Q=V[ee];for(const ae in Q)f(Q[ae].object),delete Q[ae];delete V[ee]}delete n[P]}}function U(P){if(n[P.id]===void 0)return;const V=n[P.id];for(const ee in V){const Q=V[ee];for(const ae in Q)f(Q[ae].object),delete Q[ae];delete V[ee]}delete n[P.id]}function O(P){for(const V in n){const ee=n[V];if(ee[P.id]===void 0)continue;const Q=ee[P.id];for(const ae in Q)f(Q[ae].object),delete Q[ae];delete ee[P.id]}}function H(){L(),a=!0,s!==i&&(s=i,h(s.object))}function L(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:c,reset:H,resetDefaultState:L,dispose:B,releaseStatesOfGeometry:U,releaseStatesOfProgram:O,initAttributes:M,enableAttribute:v,disableUnusedAttributes:A}}function T1(r,e,t){let n;function i(h){n=h}function s(h,f){r.drawArrays(n,h,f),t.update(f,n,1)}function a(h,f,p){p!==0&&(r.drawArraysInstanced(n,h,f,p),t.update(f,n,p))}function c(h,f,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,h,0,f,0,p);let g=0;for(let x=0;x<p;x++)g+=f[x];t.update(g,n,1)}function u(h,f,p,m){if(p===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let x=0;x<h.length;x++)a(h[x],f[x],m[x]);else{g.multiDrawArraysInstancedWEBGL(n,h,0,f,0,m,0,p);let x=0;for(let M=0;M<p;M++)x+=f[M]*m[M];t.update(x,n,1)}}this.setMode=i,this.render=s,this.renderInstances=a,this.renderMultiDraw=c,this.renderMultiDrawInstances=u}function E1(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const O=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(O.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(O){return!(O!==li&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function c(O){const H=O===na&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(O!==Qi&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&O!==vi&&!H)}function u(O){if(O==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";O="mediump"}return O==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=t.precision!==void 0?t.precision:"highp";const f=u(h);f!==h&&(console.warn("THREE.WebGLRenderer:",h,"not supported, using",f,"instead."),h=f);const p=t.logarithmicDepthBuffer===!0,m=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),g=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),x=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),M=r.getParameter(r.MAX_TEXTURE_SIZE),v=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),_=r.getParameter(r.MAX_VERTEX_ATTRIBS),A=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),w=r.getParameter(r.MAX_VARYING_VECTORS),b=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),B=x>0,U=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:u,textureFormatReadable:a,textureTypeReadable:c,precision:h,logarithmicDepthBuffer:p,reverseDepthBuffer:m,maxTextures:g,maxVertexTextures:x,maxTextureSize:M,maxCubemapSize:v,maxAttributes:_,maxVertexUniforms:A,maxVaryings:w,maxFragmentUniforms:b,vertexTextures:B,maxSamples:U}}function A1(r){const e=this;let t=null,n=0,i=!1,s=!1;const a=new _r,c=new gt,u={value:null,needsUpdate:!1};this.uniform=u,this.numPlanes=0,this.numIntersection=0,this.init=function(p,m){const g=p.length!==0||m||n!==0||i;return i=m,n=p.length,g},this.beginShadows=function(){s=!0,f(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(p,m){t=f(p,m,0)},this.setState=function(p,m,g){const x=p.clippingPlanes,M=p.clipIntersection,v=p.clipShadows,_=r.get(p);if(!i||x===null||x.length===0||s&&!v)s?f(null):h();else{const A=s?0:n,w=A*4;let b=_.clippingState||null;u.value=b,b=f(x,m,w,g);for(let B=0;B!==w;++B)b[B]=t[B];_.clippingState=b,this.numIntersection=M?this.numPlanes:0,this.numPlanes+=A}};function h(){u.value!==t&&(u.value=t,u.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function f(p,m,g,x){const M=p!==null?p.length:0;let v=null;if(M!==0){if(v=u.value,x!==!0||v===null){const _=g+M*4,A=m.matrixWorldInverse;c.getNormalMatrix(A),(v===null||v.length<_)&&(v=new Float32Array(_));for(let w=0,b=g;w!==M;++w,b+=4)a.copy(p[w]).applyMatrix4(A,c),a.normal.toArray(v,b),v[b+3]=a.constant}u.value=v,u.needsUpdate=!0}return e.numPlanes=M,e.numIntersection=0,v}}function w1(r){let e=new WeakMap;function t(a,c){return c===Eh?a.mapping=Zs:c===Ah&&(a.mapping=Js),a}function n(a){if(a&&a.isTexture){const c=a.mapping;if(c===Eh||c===Ah)if(e.has(a)){const u=e.get(a).texture;return t(u,a.mapping)}else{const u=a.image;if(u&&u.height>0){const h=new BE(u.height);return h.fromEquirectangularTexture(r,a),e.set(a,h),a.addEventListener("dispose",i),t(h.texture,a.mapping)}else return null}}return a}function i(a){const c=a.target;c.removeEventListener("dispose",i);const u=e.get(c);u!==void 0&&(e.delete(c),u.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class bd extends Og{constructor(e=-1,t=1,n=1,i=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,a=n+e,c=i+t,u=i-t;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=h*this.view.offsetX,a=s+h*this.view.width,c-=f*this.view.offsetY,u=c-f*this.view.height}this.projectionMatrix.makeOrthographic(s,a,c,u,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Gs=4,em=[.125,.215,.35,.446,.526,.582],is=20,Wu=new bd,tm=new $e;let ju=null,Xu=0,qu=0,Yu=!1;const es=(1+Math.sqrt(5))/2,Bs=1/es,nm=[new F(-es,Bs,0),new F(es,Bs,0),new F(-Bs,0,es),new F(Bs,0,es),new F(0,es,-Bs),new F(0,es,Bs),new F(-1,1,-1),new F(1,1,-1),new F(-1,1,1),new F(1,1,1)];class im{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=om(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=sm(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(ju,Xu,qu),this._renderer.xr.enabled=Yu,e.scissorTest=!1,cc(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Zs||e.mapping===Js?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ii,minFilter:ii,generateMipmaps:!1,type:na,format:li,colorSpace:Hn,depthBuffer:!1},i=rm(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=rm(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=P1(s)),this._blurMaterial=R1(s,e,t)}return i}_compileMaterial(e){const t=new Ee(this._lodPlanes[0],e);this._renderer.compile(t,Wu)}_sceneToCubeUV(e,t,n,i){const c=new kn(90,1,t,n),u=[1,-1,1,1,1,1],h=[1,1,1,-1,-1,-1],f=this._renderer,p=f.autoClear,m=f.toneMapping;f.getClearColor(tm),f.toneMapping=Sr,f.autoClear=!1;const g=new ui({name:"PMREM.Background",side:qn,depthWrite:!1,depthTest:!1}),x=new Ee(new sn,g);let M=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,M=!0):(g.color.copy(tm),M=!0);for(let _=0;_<6;_++){const A=_%3;A===0?(c.up.set(0,u[_],0),c.lookAt(h[_],0,0)):A===1?(c.up.set(0,0,u[_]),c.lookAt(0,h[_],0)):(c.up.set(0,u[_],0),c.lookAt(0,0,h[_]));const w=this._cubeSize;cc(i,A*w,_>2?w:0,w,w),f.setRenderTarget(i),M&&f.render(x,c),f.render(e,c)}x.geometry.dispose(),x.material.dispose(),f.toneMapping=m,f.autoClear=p,e.background=v}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===Zs||e.mapping===Js;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=om()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=sm());const s=i?this._cubemapMaterial:this._equirectMaterial,a=new Ee(this._lodPlanes[0],s),c=s.uniforms;c.envMap.value=e;const u=this._cubeSize;cc(t,0,0,3*u,2*u),n.setRenderTarget(t),n.render(a,Wu)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),c=nm[(i-s-1)%nm.length];this._blur(e,s-1,s,a,c)}t.autoClear=n}_blur(e,t,n,i,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",s),this._halfBlur(a,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,a,c){const u=this._renderer,h=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const f=3,p=new Ee(this._lodPlanes[i],h),m=h.uniforms,g=this._sizeLods[n]-1,x=isFinite(s)?Math.PI/(2*g):2*Math.PI/(2*is-1),M=s/x,v=isFinite(s)?1+Math.floor(f*M):is;v>is&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${is}`);const _=[];let A=0;for(let O=0;O<is;++O){const H=O/M,L=Math.exp(-H*H/2);_.push(L),O===0?A+=L:O<v&&(A+=2*L)}for(let O=0;O<_.length;O++)_[O]=_[O]/A;m.envMap.value=e.texture,m.samples.value=v,m.weights.value=_,m.latitudinal.value=a==="latitudinal",c&&(m.poleAxis.value=c);const{_lodMax:w}=this;m.dTheta.value=x,m.mipInt.value=w-n;const b=this._sizeLods[i],B=3*b*(i>w-Gs?i-w+Gs:0),U=4*(this._cubeSize-b);cc(t,B,U,3*b,2*b),u.setRenderTarget(t),u.render(p,Wu)}}function P1(r){const e=[],t=[],n=[];let i=r;const s=r-Gs+1+em.length;for(let a=0;a<s;a++){const c=Math.pow(2,i);t.push(c);let u=1/c;a>r-Gs?u=em[a-r+Gs-1]:a===0&&(u=0),n.push(u);const h=1/(c-2),f=-h,p=1+h,m=[f,f,p,f,p,p,f,f,p,p,f,p],g=6,x=6,M=3,v=2,_=1,A=new Float32Array(M*x*g),w=new Float32Array(v*x*g),b=new Float32Array(_*x*g);for(let U=0;U<g;U++){const O=U%3*2/3-1,H=U>2?0:-1,L=[O,H,0,O+2/3,H,0,O+2/3,H+1,0,O,H,0,O+2/3,H+1,0,O,H+1,0];A.set(L,M*x*U),w.set(m,v*x*U);const P=[U,U,U,U,U,U];b.set(P,_*x*U)}const B=new mn;B.setAttribute("position",new an(A,M)),B.setAttribute("uv",new an(w,v)),B.setAttribute("faceIndex",new an(b,_)),e.push(B),i>Gs&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function rm(r,e,t){const n=new os(r,e,t);return n.texture.mapping=kc,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function cc(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function R1(r,e,t){const n=new Float32Array(is),i=new F(0,1,0);return new Mr({name:"SphericalGaussianBlur",defines:{n:is,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Sd(),fragmentShader:`

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
		`,blending:br,depthTest:!1,depthWrite:!1})}function sm(){return new Mr({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Sd(),fragmentShader:`

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
		`,blending:br,depthTest:!1,depthWrite:!1})}function om(){return new Mr({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Sd(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:br,depthTest:!1,depthWrite:!1})}function Sd(){return`

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
	`}function C1(r){let e=new WeakMap,t=null;function n(c){if(c&&c.isTexture){const u=c.mapping,h=u===Eh||u===Ah,f=u===Zs||u===Js;if(h||f){let p=e.get(c);const m=p!==void 0?p.texture.pmremVersion:0;if(c.isRenderTargetTexture&&c.pmremVersion!==m)return t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c,p):t.fromCubemap(c,p),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),p.texture;if(p!==void 0)return p.texture;{const g=c.image;return h&&g&&g.height>0||f&&g&&i(g)?(t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c):t.fromCubemap(c),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),c.addEventListener("dispose",s),p.texture):null}}}return c}function i(c){let u=0;const h=6;for(let f=0;f<h;f++)c[f]!==void 0&&u++;return u===h}function s(c){const u=c.target;u.removeEventListener("dispose",s);const h=e.get(u);h!==void 0&&(e.delete(u),h.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function I1(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&Wo("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function L1(r,e,t,n){const i={},s=new WeakMap;function a(p){const m=p.target;m.index!==null&&e.remove(m.index);for(const x in m.attributes)e.remove(m.attributes[x]);for(const x in m.morphAttributes){const M=m.morphAttributes[x];for(let v=0,_=M.length;v<_;v++)e.remove(M[v])}m.removeEventListener("dispose",a),delete i[m.id];const g=s.get(m);g&&(e.remove(g),s.delete(m)),n.releaseStatesOfGeometry(m),m.isInstancedBufferGeometry===!0&&delete m._maxInstanceCount,t.memory.geometries--}function c(p,m){return i[m.id]===!0||(m.addEventListener("dispose",a),i[m.id]=!0,t.memory.geometries++),m}function u(p){const m=p.attributes;for(const x in m)e.update(m[x],r.ARRAY_BUFFER);const g=p.morphAttributes;for(const x in g){const M=g[x];for(let v=0,_=M.length;v<_;v++)e.update(M[v],r.ARRAY_BUFFER)}}function h(p){const m=[],g=p.index,x=p.attributes.position;let M=0;if(g!==null){const A=g.array;M=g.version;for(let w=0,b=A.length;w<b;w+=3){const B=A[w+0],U=A[w+1],O=A[w+2];m.push(B,U,U,O,O,B)}}else if(x!==void 0){const A=x.array;M=x.version;for(let w=0,b=A.length/3-1;w<b;w+=3){const B=w+0,U=w+1,O=w+2;m.push(B,U,U,O,O,B)}}else return;const v=new(Pg(m)?Dg:Lg)(m,1);v.version=M;const _=s.get(p);_&&e.remove(_),s.set(p,v)}function f(p){const m=s.get(p);if(m){const g=p.index;g!==null&&m.version<g.version&&h(p)}else h(p);return s.get(p)}return{get:c,update:u,getWireframeAttribute:f}}function D1(r,e,t){let n;function i(m){n=m}let s,a;function c(m){s=m.type,a=m.bytesPerElement}function u(m,g){r.drawElements(n,g,s,m*a),t.update(g,n,1)}function h(m,g,x){x!==0&&(r.drawElementsInstanced(n,g,s,m*a,x),t.update(g,n,x))}function f(m,g,x){if(x===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,g,0,s,m,0,x);let v=0;for(let _=0;_<x;_++)v+=g[_];t.update(v,n,1)}function p(m,g,x,M){if(x===0)return;const v=e.get("WEBGL_multi_draw");if(v===null)for(let _=0;_<m.length;_++)h(m[_]/a,g[_],M[_]);else{v.multiDrawElementsInstancedWEBGL(n,g,0,s,m,0,M,0,x);let _=0;for(let A=0;A<x;A++)_+=g[A]*M[A];t.update(_,n,1)}}this.setMode=i,this.setIndex=c,this.render=u,this.renderInstances=h,this.renderMultiDraw=f,this.renderMultiDrawInstances=p}function N1(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,c){switch(t.calls++,a){case r.TRIANGLES:t.triangles+=c*(s/3);break;case r.LINES:t.lines+=c*(s/2);break;case r.LINE_STRIP:t.lines+=c*(s-1);break;case r.LINE_LOOP:t.lines+=c*s;break;case r.POINTS:t.points+=c*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function O1(r,e,t){const n=new WeakMap,i=new Dt;function s(a,c,u){const h=a.morphTargetInfluences,f=c.morphAttributes.position||c.morphAttributes.normal||c.morphAttributes.color,p=f!==void 0?f.length:0;let m=n.get(c);if(m===void 0||m.count!==p){let P=function(){H.dispose(),n.delete(c),c.removeEventListener("dispose",P)};var g=P;m!==void 0&&m.texture.dispose();const x=c.morphAttributes.position!==void 0,M=c.morphAttributes.normal!==void 0,v=c.morphAttributes.color!==void 0,_=c.morphAttributes.position||[],A=c.morphAttributes.normal||[],w=c.morphAttributes.color||[];let b=0;x===!0&&(b=1),M===!0&&(b=2),v===!0&&(b=3);let B=c.attributes.position.count*b,U=1;B>e.maxTextureSize&&(U=Math.ceil(B/e.maxTextureSize),B=e.maxTextureSize);const O=new Float32Array(B*U*4*p),H=new Cg(O,B,U,p);H.type=vi,H.needsUpdate=!0;const L=b*4;for(let V=0;V<p;V++){const ee=_[V],Q=A[V],ae=w[V],ce=B*U*4*V;for(let J=0;J<ee.count;J++){const de=J*L;x===!0&&(i.fromBufferAttribute(ee,J),O[ce+de+0]=i.x,O[ce+de+1]=i.y,O[ce+de+2]=i.z,O[ce+de+3]=0),M===!0&&(i.fromBufferAttribute(Q,J),O[ce+de+4]=i.x,O[ce+de+5]=i.y,O[ce+de+6]=i.z,O[ce+de+7]=0),v===!0&&(i.fromBufferAttribute(ae,J),O[ce+de+8]=i.x,O[ce+de+9]=i.y,O[ce+de+10]=i.z,O[ce+de+11]=ae.itemSize===4?i.w:1)}}m={count:p,texture:H,size:new tt(B,U)},n.set(c,m),c.addEventListener("dispose",P)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)u.getUniforms().setValue(r,"morphTexture",a.morphTexture,t);else{let x=0;for(let v=0;v<h.length;v++)x+=h[v];const M=c.morphTargetsRelative?1:1-x;u.getUniforms().setValue(r,"morphTargetBaseInfluence",M),u.getUniforms().setValue(r,"morphTargetInfluences",h)}u.getUniforms().setValue(r,"morphTargetsTexture",m.texture,t),u.getUniforms().setValue(r,"morphTargetsTextureSize",m.size)}return{update:s}}function U1(r,e,t,n){let i=new WeakMap;function s(u){const h=n.render.frame,f=u.geometry,p=e.get(u,f);if(i.get(p)!==h&&(e.update(p),i.set(p,h)),u.isInstancedMesh&&(u.hasEventListener("dispose",c)===!1&&u.addEventListener("dispose",c),i.get(u)!==h&&(t.update(u.instanceMatrix,r.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,r.ARRAY_BUFFER),i.set(u,h))),u.isSkinnedMesh){const m=u.skeleton;i.get(m)!==h&&(m.update(),i.set(m,h))}return p}function a(){i=new WeakMap}function c(u){const h=u.target;h.removeEventListener("dispose",c),t.remove(h.instanceMatrix),h.instanceColor!==null&&t.remove(h.instanceColor)}return{update:s,dispose:a}}class Bg extends Sn{constructor(e,t,n,i,s,a,c,u,h,f=qs){if(f!==qs&&f!==to)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&f===qs&&(n=ss),n===void 0&&f===to&&(n=eo),super(null,i,s,a,c,u,f,n,h),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=c!==void 0?c:zn,this.minFilter=u!==void 0?u:zn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const kg=new Sn,am=new Bg(1,1),zg=new Cg,Hg=new SE,Vg=new Ug,cm=[],lm=[],um=new Float32Array(16),hm=new Float32Array(9),dm=new Float32Array(4);function co(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=cm[i];if(s===void 0&&(s=new Float32Array(i),cm[i]=s),e!==0){n.toArray(s,0);for(let a=1,c=0;a!==e;++a)c+=t,r[a].toArray(s,c)}return s}function gn(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function _n(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function Hc(r,e){let t=lm[e];t===void 0&&(t=new Int32Array(e),lm[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function F1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function B1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(gn(t,e))return;r.uniform2fv(this.addr,e),_n(t,e)}}function k1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(gn(t,e))return;r.uniform3fv(this.addr,e),_n(t,e)}}function z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(gn(t,e))return;r.uniform4fv(this.addr,e),_n(t,e)}}function H1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(gn(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),_n(t,e)}else{if(gn(t,n))return;dm.set(n),r.uniformMatrix2fv(this.addr,!1,dm),_n(t,n)}}function V1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(gn(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),_n(t,e)}else{if(gn(t,n))return;hm.set(n),r.uniformMatrix3fv(this.addr,!1,hm),_n(t,n)}}function G1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(gn(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),_n(t,e)}else{if(gn(t,n))return;um.set(n),r.uniformMatrix4fv(this.addr,!1,um),_n(t,n)}}function W1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function j1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(gn(t,e))return;r.uniform2iv(this.addr,e),_n(t,e)}}function X1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(gn(t,e))return;r.uniform3iv(this.addr,e),_n(t,e)}}function q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(gn(t,e))return;r.uniform4iv(this.addr,e),_n(t,e)}}function Y1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function K1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(gn(t,e))return;r.uniform2uiv(this.addr,e),_n(t,e)}}function $1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(gn(t,e))return;r.uniform3uiv(this.addr,e),_n(t,e)}}function Z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(gn(t,e))return;r.uniform4uiv(this.addr,e),_n(t,e)}}function J1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(am.compareFunction=Ag,s=am):s=kg,t.setTexture2D(e||s,i)}function Q1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Hg,i)}function eP(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Vg,i)}function tP(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||zg,i)}function nP(r){switch(r){case 5126:return F1;case 35664:return B1;case 35665:return k1;case 35666:return z1;case 35674:return H1;case 35675:return V1;case 35676:return G1;case 5124:case 35670:return W1;case 35667:case 35671:return j1;case 35668:case 35672:return X1;case 35669:case 35673:return q1;case 5125:return Y1;case 36294:return K1;case 36295:return $1;case 36296:return Z1;case 35678:case 36198:case 36298:case 36306:case 35682:return J1;case 35679:case 36299:case 36307:return Q1;case 35680:case 36300:case 36308:case 36293:return eP;case 36289:case 36303:case 36311:case 36292:return tP}}function iP(r,e){r.uniform1fv(this.addr,e)}function rP(r,e){const t=co(e,this.size,2);r.uniform2fv(this.addr,t)}function sP(r,e){const t=co(e,this.size,3);r.uniform3fv(this.addr,t)}function oP(r,e){const t=co(e,this.size,4);r.uniform4fv(this.addr,t)}function aP(r,e){const t=co(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function cP(r,e){const t=co(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function lP(r,e){const t=co(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function uP(r,e){r.uniform1iv(this.addr,e)}function hP(r,e){r.uniform2iv(this.addr,e)}function dP(r,e){r.uniform3iv(this.addr,e)}function fP(r,e){r.uniform4iv(this.addr,e)}function pP(r,e){r.uniform1uiv(this.addr,e)}function mP(r,e){r.uniform2uiv(this.addr,e)}function gP(r,e){r.uniform3uiv(this.addr,e)}function _P(r,e){r.uniform4uiv(this.addr,e)}function vP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);gn(n,s)||(r.uniform1iv(this.addr,s),_n(n,s));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||kg,s[a])}function yP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);gn(n,s)||(r.uniform1iv(this.addr,s),_n(n,s));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Hg,s[a])}function xP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);gn(n,s)||(r.uniform1iv(this.addr,s),_n(n,s));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Vg,s[a])}function bP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);gn(n,s)||(r.uniform1iv(this.addr,s),_n(n,s));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||zg,s[a])}function SP(r){switch(r){case 5126:return iP;case 35664:return rP;case 35665:return sP;case 35666:return oP;case 35674:return aP;case 35675:return cP;case 35676:return lP;case 5124:case 35670:return uP;case 35667:case 35671:return hP;case 35668:case 35672:return dP;case 35669:case 35673:return fP;case 5125:return pP;case 36294:return mP;case 36295:return gP;case 36296:return _P;case 35678:case 36198:case 36298:case 36306:case 35682:return vP;case 35679:case 36299:case 36307:return yP;case 35680:case 36300:case 36308:case 36293:return xP;case 36289:case 36303:case 36311:case 36292:return bP}}class MP{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=nP(t.type)}}class TP{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=SP(t.type)}}class EP{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,a=i.length;s!==a;++s){const c=i[s];c.setValue(e,t[c.id],n)}}}const Ku=/(\w+)(\])?(\[|\.)?/g;function fm(r,e){r.seq.push(e),r.map[e.id]=e}function AP(r,e,t){const n=r.name,i=n.length;for(Ku.lastIndex=0;;){const s=Ku.exec(n),a=Ku.lastIndex;let c=s[1];const u=s[2]==="]",h=s[3];if(u&&(c=c|0),h===void 0||h==="["&&a+2===i){fm(t,h===void 0?new MP(c,r,e):new TP(c,r,e));break}else{let p=t.map[c];p===void 0&&(p=new EP(c),fm(t,p)),t=p}}}class Rc{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),a=e.getUniformLocation(t,s.name);AP(s,a,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,a=t.length;s!==a;++s){const c=t[s],u=n[c.id];u.needsUpdate!==!1&&c.setValue(e,u.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function pm(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const wP=37297;let PP=0;function RP(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=i;a<s;a++){const c=a+1;n.push(`${c===e?">":" "} ${c}: ${t[a]}`)}return n.join(`
`)}const mm=new gt;function CP(r){wt._getMatrix(mm,wt.workingColorSpace,r);const e=`mat3( ${mm.elements.map(t=>t.toFixed(4))} )`;switch(wt.getTransfer(r)){case zc:return[e,"LinearTransferOETF"];case Ht:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[e,"LinearTransferOETF"]}}function gm(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+RP(r.getShaderSource(e),a)}else return i}function IP(r,e){const t=CP(e);return[`vec4 ${r}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function LP(r,e){let t;switch(e){case IT:t="Linear";break;case LT:t="Reinhard";break;case DT:t="Cineon";break;case dg:t="ACESFilmic";break;case OT:t="AgX";break;case UT:t="Neutral";break;case NT:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const lc=new F;function DP(){wt.getLuminanceCoefficients(lc);const r=lc.x.toFixed(4),e=lc.y.toFixed(4),t=lc.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function NP(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(jo).join(`
`)}function OP(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function UP(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),a=s.name;let c=1;s.type===r.FLOAT_MAT2&&(c=2),s.type===r.FLOAT_MAT3&&(c=3),s.type===r.FLOAT_MAT4&&(c=4),t[a]={type:s.type,location:r.getAttribLocation(e,a),locationSize:c}}return t}function jo(r){return r!==""}function _m(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function vm(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const FP=/^[ \t]*#include +<([\w\d./]+)>/gm;function td(r){return r.replace(FP,kP)}const BP=new Map;function kP(r,e){let t=vt[e];if(t===void 0){const n=BP.get(e);if(n!==void 0)t=vt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return td(t)}const zP=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ym(r){return r.replace(zP,HP)}function HP(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function xm(r){let e=`precision ${r.precision} float;
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
#define LOW_PRECISION`),e}function VP(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===ug?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===uT?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===Xi&&(e="SHADOWMAP_TYPE_VSM"),e}function GP(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case Zs:case Js:e="ENVMAP_TYPE_CUBE";break;case kc:e="ENVMAP_TYPE_CUBE_UV";break}return e}function WP(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Js:e="ENVMAP_MODE_REFRACTION";break}return e}function jP(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case hg:e="ENVMAP_BLENDING_MULTIPLY";break;case RT:e="ENVMAP_BLENDING_MIX";break;case CT:e="ENVMAP_BLENDING_ADD";break}return e}function XP(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function qP(r,e,t,n){const i=r.getContext(),s=t.defines;let a=t.vertexShader,c=t.fragmentShader;const u=VP(t),h=GP(t),f=WP(t),p=jP(t),m=XP(t),g=NP(t),x=OP(s),M=i.createProgram();let v,_,A=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(jo).join(`
`),v.length>0&&(v+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(jo).join(`
`),_.length>0&&(_+=`
`)):(v=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(jo).join(`
`),_=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.envMap?"#define "+f:"",t.envMap?"#define "+p:"",m?"#define CUBEUV_TEXEL_WIDTH "+m.texelWidth:"",m?"#define CUBEUV_TEXEL_HEIGHT "+m.texelHeight:"",m?"#define CUBEUV_MAX_MIP "+m.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Sr?"#define TONE_MAPPING":"",t.toneMapping!==Sr?vt.tonemapping_pars_fragment:"",t.toneMapping!==Sr?LP("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",vt.colorspace_pars_fragment,IP("linearToOutputTexel",t.outputColorSpace),DP(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(jo).join(`
`)),a=td(a),a=_m(a,t),a=vm(a,t),c=td(c),c=_m(c,t),c=vm(c,t),a=ym(a),c=ym(c),t.isRawShaderMaterial!==!0&&(A=`#version 300 es
`,v=[g,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,_=["#define varying in",t.glslVersion===Lp?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Lp?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const w=A+v+a,b=A+_+c,B=pm(i,i.VERTEX_SHADER,w),U=pm(i,i.FRAGMENT_SHADER,b);i.attachShader(M,B),i.attachShader(M,U),t.index0AttributeName!==void 0?i.bindAttribLocation(M,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(M,0,"position"),i.linkProgram(M);function O(V){if(r.debug.checkShaderErrors){const ee=i.getProgramInfoLog(M).trim(),Q=i.getShaderInfoLog(B).trim(),ae=i.getShaderInfoLog(U).trim();let ce=!0,J=!0;if(i.getProgramParameter(M,i.LINK_STATUS)===!1)if(ce=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,M,B,U);else{const de=gm(i,B,"vertex"),re=gm(i,U,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(M,i.VALIDATE_STATUS)+`

Material Name: `+V.name+`
Material Type: `+V.type+`

Program Info Log: `+ee+`
`+de+`
`+re)}else ee!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ee):(Q===""||ae==="")&&(J=!1);J&&(V.diagnostics={runnable:ce,programLog:ee,vertexShader:{log:Q,prefix:v},fragmentShader:{log:ae,prefix:_}})}i.deleteShader(B),i.deleteShader(U),H=new Rc(i,M),L=UP(i,M)}let H;this.getUniforms=function(){return H===void 0&&O(this),H};let L;this.getAttributes=function(){return L===void 0&&O(this),L};let P=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return P===!1&&(P=i.getProgramParameter(M,wP)),P},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(M),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=PP++,this.cacheKey=e,this.usedTimes=1,this.program=M,this.vertexShader=B,this.fragmentShader=U,this}let YP=0;class KP{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new $P(e),t.set(e,n)),n}}class $P{constructor(e){this.id=YP++,this.code=e,this.usedTimes=0}}function ZP(r,e,t,n,i,s,a){const c=new yd,u=new KP,h=new Set,f=[],p=i.logarithmicDepthBuffer,m=i.vertexTextures;let g=i.precision;const x={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function M(L){return h.add(L),L===0?"uv":`uv${L}`}function v(L,P,V,ee,Q){const ae=ee.fog,ce=Q.geometry,J=L.isMeshStandardMaterial?ee.environment:null,de=(L.isMeshStandardMaterial?t:e).get(L.envMap||J),re=de&&de.mapping===kc?de.image.height:null,_e=x[L.type];L.precision!==null&&(g=i.getMaxPrecision(L.precision),g!==L.precision&&console.warn("THREE.WebGLProgram.getParameters:",L.precision,"not supported, using",g,"instead."));const Me=ce.morphAttributes.position||ce.morphAttributes.normal||ce.morphAttributes.color,Ue=Me!==void 0?Me.length:0;let Je=0;ce.morphAttributes.position!==void 0&&(Je=1),ce.morphAttributes.normal!==void 0&&(Je=2),ce.morphAttributes.color!==void 0&&(Je=3);let pt,le,pe,Fe;if(_e){const Ie=Ti[_e];pt=Ie.vertexShader,le=Ie.fragmentShader}else pt=L.vertexShader,le=L.fragmentShader,u.update(L),pe=u.getVertexShaderID(L),Fe=u.getFragmentShaderID(L);const Se=r.getRenderTarget(),qe=r.state.buffers.depth.getReversed(),it=Q.isInstancedMesh===!0,at=Q.isBatchedMesh===!0,Pt=!!L.map,lt=!!L.matcap,zt=!!de,X=!!L.aoMap,rn=!!L.lightMap,ut=!!L.bumpMap,mt=!!L.normalMap,We=!!L.displacementMap,Tt=!!L.emissiveMap,ke=!!L.metalnessMap,N=!!L.roughnessMap,E=L.anisotropy>0,Z=L.clearcoat>0,ue=L.dispersion>0,fe=L.iridescence>0,he=L.sheen>0,Oe=L.transmission>0,Ae=E&&!!L.anisotropyMap,Le=Z&&!!L.clearcoatMap,ht=Z&&!!L.clearcoatNormalMap,me=Z&&!!L.clearcoatRoughnessMap,De=fe&&!!L.iridescenceMap,Be=fe&&!!L.iridescenceThicknessMap,Ze=he&&!!L.sheenColorMap,Ne=he&&!!L.sheenRoughnessMap,_t=!!L.specularMap,st=!!L.specularColorMap,Ct=!!L.specularIntensityMap,W=Oe&&!!L.transmissionMap,Te=Oe&&!!L.thicknessMap,R=!!L.gradientMap,z=!!L.alphaMap,K=L.alphaTest>0,ie=!!L.alphaHash,ye=!!L.extensions;let xe=Sr;L.toneMapped&&(Se===null||Se.isXRRenderTarget===!0)&&(xe=r.toneMapping);const we={shaderID:_e,shaderType:L.type,shaderName:L.name,vertexShader:pt,fragmentShader:le,defines:L.defines,customVertexShaderID:pe,customFragmentShaderID:Fe,isRawShaderMaterial:L.isRawShaderMaterial===!0,glslVersion:L.glslVersion,precision:g,batching:at,batchingColor:at&&Q._colorsTexture!==null,instancing:it,instancingColor:it&&Q.instanceColor!==null,instancingMorph:it&&Q.morphTexture!==null,supportsVertexTextures:m,outputColorSpace:Se===null?r.outputColorSpace:Se.isXRRenderTarget===!0?Se.texture.colorSpace:Hn,alphaToCoverage:!!L.alphaToCoverage,map:Pt,matcap:lt,envMap:zt,envMapMode:zt&&de.mapping,envMapCubeUVHeight:re,aoMap:X,lightMap:rn,bumpMap:ut,normalMap:mt,displacementMap:m&&We,emissiveMap:Tt,normalMapObjectSpace:mt&&L.normalMapType===WT,normalMapTangentSpace:mt&&L.normalMapType===Eg,metalnessMap:ke,roughnessMap:N,anisotropy:E,anisotropyMap:Ae,clearcoat:Z,clearcoatMap:Le,clearcoatNormalMap:ht,clearcoatRoughnessMap:me,dispersion:ue,iridescence:fe,iridescenceMap:De,iridescenceThicknessMap:Be,sheen:he,sheenColorMap:Ze,sheenRoughnessMap:Ne,specularMap:_t,specularColorMap:st,specularIntensityMap:Ct,transmission:Oe,transmissionMap:W,thicknessMap:Te,gradientMap:R,opaque:L.transparent===!1&&L.blending===Xs&&L.alphaToCoverage===!1,alphaMap:z,alphaTest:K,alphaHash:ie,combine:L.combine,mapUv:Pt&&M(L.map.channel),aoMapUv:X&&M(L.aoMap.channel),lightMapUv:rn&&M(L.lightMap.channel),bumpMapUv:ut&&M(L.bumpMap.channel),normalMapUv:mt&&M(L.normalMap.channel),displacementMapUv:We&&M(L.displacementMap.channel),emissiveMapUv:Tt&&M(L.emissiveMap.channel),metalnessMapUv:ke&&M(L.metalnessMap.channel),roughnessMapUv:N&&M(L.roughnessMap.channel),anisotropyMapUv:Ae&&M(L.anisotropyMap.channel),clearcoatMapUv:Le&&M(L.clearcoatMap.channel),clearcoatNormalMapUv:ht&&M(L.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:me&&M(L.clearcoatRoughnessMap.channel),iridescenceMapUv:De&&M(L.iridescenceMap.channel),iridescenceThicknessMapUv:Be&&M(L.iridescenceThicknessMap.channel),sheenColorMapUv:Ze&&M(L.sheenColorMap.channel),sheenRoughnessMapUv:Ne&&M(L.sheenRoughnessMap.channel),specularMapUv:_t&&M(L.specularMap.channel),specularColorMapUv:st&&M(L.specularColorMap.channel),specularIntensityMapUv:Ct&&M(L.specularIntensityMap.channel),transmissionMapUv:W&&M(L.transmissionMap.channel),thicknessMapUv:Te&&M(L.thicknessMap.channel),alphaMapUv:z&&M(L.alphaMap.channel),vertexTangents:!!ce.attributes.tangent&&(mt||E),vertexColors:L.vertexColors,vertexAlphas:L.vertexColors===!0&&!!ce.attributes.color&&ce.attributes.color.itemSize===4,pointsUvs:Q.isPoints===!0&&!!ce.attributes.uv&&(Pt||z),fog:!!ae,useFog:L.fog===!0,fogExp2:!!ae&&ae.isFogExp2,flatShading:L.flatShading===!0,sizeAttenuation:L.sizeAttenuation===!0,logarithmicDepthBuffer:p,reverseDepthBuffer:qe,skinning:Q.isSkinnedMesh===!0,morphTargets:ce.morphAttributes.position!==void 0,morphNormals:ce.morphAttributes.normal!==void 0,morphColors:ce.morphAttributes.color!==void 0,morphTargetsCount:Ue,morphTextureStride:Je,numDirLights:P.directional.length,numPointLights:P.point.length,numSpotLights:P.spot.length,numSpotLightMaps:P.spotLightMap.length,numRectAreaLights:P.rectArea.length,numHemiLights:P.hemi.length,numDirLightShadows:P.directionalShadowMap.length,numPointLightShadows:P.pointShadowMap.length,numSpotLightShadows:P.spotShadowMap.length,numSpotLightShadowsWithMaps:P.numSpotLightShadowsWithMaps,numLightProbes:P.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:L.dithering,shadowMapEnabled:r.shadowMap.enabled&&V.length>0,shadowMapType:r.shadowMap.type,toneMapping:xe,decodeVideoTexture:Pt&&L.map.isVideoTexture===!0&&wt.getTransfer(L.map.colorSpace)===Ht,decodeVideoTextureEmissive:Tt&&L.emissiveMap.isVideoTexture===!0&&wt.getTransfer(L.emissiveMap.colorSpace)===Ht,premultipliedAlpha:L.premultipliedAlpha,doubleSided:L.side===Xn,flipSided:L.side===qn,useDepthPacking:L.depthPacking>=0,depthPacking:L.depthPacking||0,index0AttributeName:L.index0AttributeName,extensionClipCullDistance:ye&&L.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ye&&L.extensions.multiDraw===!0||at)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:L.customProgramCacheKey()};return we.vertexUv1s=h.has(1),we.vertexUv2s=h.has(2),we.vertexUv3s=h.has(3),h.clear(),we}function _(L){const P=[];if(L.shaderID?P.push(L.shaderID):(P.push(L.customVertexShaderID),P.push(L.customFragmentShaderID)),L.defines!==void 0)for(const V in L.defines)P.push(V),P.push(L.defines[V]);return L.isRawShaderMaterial===!1&&(A(P,L),w(P,L),P.push(r.outputColorSpace)),P.push(L.customProgramCacheKey),P.join()}function A(L,P){L.push(P.precision),L.push(P.outputColorSpace),L.push(P.envMapMode),L.push(P.envMapCubeUVHeight),L.push(P.mapUv),L.push(P.alphaMapUv),L.push(P.lightMapUv),L.push(P.aoMapUv),L.push(P.bumpMapUv),L.push(P.normalMapUv),L.push(P.displacementMapUv),L.push(P.emissiveMapUv),L.push(P.metalnessMapUv),L.push(P.roughnessMapUv),L.push(P.anisotropyMapUv),L.push(P.clearcoatMapUv),L.push(P.clearcoatNormalMapUv),L.push(P.clearcoatRoughnessMapUv),L.push(P.iridescenceMapUv),L.push(P.iridescenceThicknessMapUv),L.push(P.sheenColorMapUv),L.push(P.sheenRoughnessMapUv),L.push(P.specularMapUv),L.push(P.specularColorMapUv),L.push(P.specularIntensityMapUv),L.push(P.transmissionMapUv),L.push(P.thicknessMapUv),L.push(P.combine),L.push(P.fogExp2),L.push(P.sizeAttenuation),L.push(P.morphTargetsCount),L.push(P.morphAttributeCount),L.push(P.numDirLights),L.push(P.numPointLights),L.push(P.numSpotLights),L.push(P.numSpotLightMaps),L.push(P.numHemiLights),L.push(P.numRectAreaLights),L.push(P.numDirLightShadows),L.push(P.numPointLightShadows),L.push(P.numSpotLightShadows),L.push(P.numSpotLightShadowsWithMaps),L.push(P.numLightProbes),L.push(P.shadowMapType),L.push(P.toneMapping),L.push(P.numClippingPlanes),L.push(P.numClipIntersection),L.push(P.depthPacking)}function w(L,P){c.disableAll(),P.supportsVertexTextures&&c.enable(0),P.instancing&&c.enable(1),P.instancingColor&&c.enable(2),P.instancingMorph&&c.enable(3),P.matcap&&c.enable(4),P.envMap&&c.enable(5),P.normalMapObjectSpace&&c.enable(6),P.normalMapTangentSpace&&c.enable(7),P.clearcoat&&c.enable(8),P.iridescence&&c.enable(9),P.alphaTest&&c.enable(10),P.vertexColors&&c.enable(11),P.vertexAlphas&&c.enable(12),P.vertexUv1s&&c.enable(13),P.vertexUv2s&&c.enable(14),P.vertexUv3s&&c.enable(15),P.vertexTangents&&c.enable(16),P.anisotropy&&c.enable(17),P.alphaHash&&c.enable(18),P.batching&&c.enable(19),P.dispersion&&c.enable(20),P.batchingColor&&c.enable(21),L.push(c.mask),c.disableAll(),P.fog&&c.enable(0),P.useFog&&c.enable(1),P.flatShading&&c.enable(2),P.logarithmicDepthBuffer&&c.enable(3),P.reverseDepthBuffer&&c.enable(4),P.skinning&&c.enable(5),P.morphTargets&&c.enable(6),P.morphNormals&&c.enable(7),P.morphColors&&c.enable(8),P.premultipliedAlpha&&c.enable(9),P.shadowMapEnabled&&c.enable(10),P.doubleSided&&c.enable(11),P.flipSided&&c.enable(12),P.useDepthPacking&&c.enable(13),P.dithering&&c.enable(14),P.transmission&&c.enable(15),P.sheen&&c.enable(16),P.opaque&&c.enable(17),P.pointsUvs&&c.enable(18),P.decodeVideoTexture&&c.enable(19),P.decodeVideoTextureEmissive&&c.enable(20),P.alphaToCoverage&&c.enable(21),L.push(c.mask)}function b(L){const P=x[L.type];let V;if(P){const ee=Ti[P];V=NE.clone(ee.uniforms)}else V=L.uniforms;return V}function B(L,P){let V;for(let ee=0,Q=f.length;ee<Q;ee++){const ae=f[ee];if(ae.cacheKey===P){V=ae,++V.usedTimes;break}}return V===void 0&&(V=new qP(r,P,L,s),f.push(V)),V}function U(L){if(--L.usedTimes===0){const P=f.indexOf(L);f[P]=f[f.length-1],f.pop(),L.destroy()}}function O(L){u.remove(L)}function H(){u.dispose()}return{getParameters:v,getProgramCacheKey:_,getUniforms:b,acquireProgram:B,releaseProgram:U,releaseShaderCache:O,programs:f,dispose:H}}function JP(){let r=new WeakMap;function e(a){return r.has(a)}function t(a){let c=r.get(a);return c===void 0&&(c={},r.set(a,c)),c}function n(a){r.delete(a)}function i(a,c,u){r.get(a)[c]=u}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function QP(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function bm(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function Sm(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function a(p,m,g,x,M,v){let _=r[e];return _===void 0?(_={id:p.id,object:p,geometry:m,material:g,groupOrder:x,renderOrder:p.renderOrder,z:M,group:v},r[e]=_):(_.id=p.id,_.object=p,_.geometry=m,_.material=g,_.groupOrder=x,_.renderOrder=p.renderOrder,_.z=M,_.group=v),e++,_}function c(p,m,g,x,M,v){const _=a(p,m,g,x,M,v);g.transmission>0?n.push(_):g.transparent===!0?i.push(_):t.push(_)}function u(p,m,g,x,M,v){const _=a(p,m,g,x,M,v);g.transmission>0?n.unshift(_):g.transparent===!0?i.unshift(_):t.unshift(_)}function h(p,m){t.length>1&&t.sort(p||QP),n.length>1&&n.sort(m||bm),i.length>1&&i.sort(m||bm)}function f(){for(let p=e,m=r.length;p<m;p++){const g=r[p];if(g.id===null)break;g.id=null,g.object=null,g.geometry=null,g.material=null,g.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:c,unshift:u,finish:f,sort:h}}function eR(){let r=new WeakMap;function e(n,i){const s=r.get(n);let a;return s===void 0?(a=new Sm,r.set(n,[a])):i>=s.length?(a=new Sm,s.push(a)):a=s[i],a}function t(){r=new WeakMap}return{get:e,dispose:t}}function tR(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new F,color:new $e};break;case"SpotLight":t={position:new F,direction:new F,color:new $e,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new F,color:new $e,distance:0,decay:0};break;case"HemisphereLight":t={direction:new F,skyColor:new $e,groundColor:new $e};break;case"RectAreaLight":t={color:new $e,position:new F,halfWidth:new F,halfHeight:new F};break}return r[e.id]=t,t}}}function nR(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new tt};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new tt};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new tt,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let iR=0;function rR(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function sR(r){const e=new tR,t=nR(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)n.probe.push(new F);const i=new F,s=new ot,a=new ot;function c(h){let f=0,p=0,m=0;for(let L=0;L<9;L++)n.probe[L].set(0,0,0);let g=0,x=0,M=0,v=0,_=0,A=0,w=0,b=0,B=0,U=0,O=0;h.sort(rR);for(let L=0,P=h.length;L<P;L++){const V=h[L],ee=V.color,Q=V.intensity,ae=V.distance,ce=V.shadow&&V.shadow.map?V.shadow.map.texture:null;if(V.isAmbientLight)f+=ee.r*Q,p+=ee.g*Q,m+=ee.b*Q;else if(V.isLightProbe){for(let J=0;J<9;J++)n.probe[J].addScaledVector(V.sh.coefficients[J],Q);O++}else if(V.isDirectionalLight){const J=e.get(V);if(J.color.copy(V.color).multiplyScalar(V.intensity),V.castShadow){const de=V.shadow,re=t.get(V);re.shadowIntensity=de.intensity,re.shadowBias=de.bias,re.shadowNormalBias=de.normalBias,re.shadowRadius=de.radius,re.shadowMapSize=de.mapSize,n.directionalShadow[g]=re,n.directionalShadowMap[g]=ce,n.directionalShadowMatrix[g]=V.shadow.matrix,A++}n.directional[g]=J,g++}else if(V.isSpotLight){const J=e.get(V);J.position.setFromMatrixPosition(V.matrixWorld),J.color.copy(ee).multiplyScalar(Q),J.distance=ae,J.coneCos=Math.cos(V.angle),J.penumbraCos=Math.cos(V.angle*(1-V.penumbra)),J.decay=V.decay,n.spot[M]=J;const de=V.shadow;if(V.map&&(n.spotLightMap[B]=V.map,B++,de.updateMatrices(V),V.castShadow&&U++),n.spotLightMatrix[M]=de.matrix,V.castShadow){const re=t.get(V);re.shadowIntensity=de.intensity,re.shadowBias=de.bias,re.shadowNormalBias=de.normalBias,re.shadowRadius=de.radius,re.shadowMapSize=de.mapSize,n.spotShadow[M]=re,n.spotShadowMap[M]=ce,b++}M++}else if(V.isRectAreaLight){const J=e.get(V);J.color.copy(ee).multiplyScalar(Q),J.halfWidth.set(V.width*.5,0,0),J.halfHeight.set(0,V.height*.5,0),n.rectArea[v]=J,v++}else if(V.isPointLight){const J=e.get(V);if(J.color.copy(V.color).multiplyScalar(V.intensity),J.distance=V.distance,J.decay=V.decay,V.castShadow){const de=V.shadow,re=t.get(V);re.shadowIntensity=de.intensity,re.shadowBias=de.bias,re.shadowNormalBias=de.normalBias,re.shadowRadius=de.radius,re.shadowMapSize=de.mapSize,re.shadowCameraNear=de.camera.near,re.shadowCameraFar=de.camera.far,n.pointShadow[x]=re,n.pointShadowMap[x]=ce,n.pointShadowMatrix[x]=V.shadow.matrix,w++}n.point[x]=J,x++}else if(V.isHemisphereLight){const J=e.get(V);J.skyColor.copy(V.color).multiplyScalar(Q),J.groundColor.copy(V.groundColor).multiplyScalar(Q),n.hemi[_]=J,_++}}v>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Re.LTC_FLOAT_1,n.rectAreaLTC2=Re.LTC_FLOAT_2):(n.rectAreaLTC1=Re.LTC_HALF_1,n.rectAreaLTC2=Re.LTC_HALF_2)),n.ambient[0]=f,n.ambient[1]=p,n.ambient[2]=m;const H=n.hash;(H.directionalLength!==g||H.pointLength!==x||H.spotLength!==M||H.rectAreaLength!==v||H.hemiLength!==_||H.numDirectionalShadows!==A||H.numPointShadows!==w||H.numSpotShadows!==b||H.numSpotMaps!==B||H.numLightProbes!==O)&&(n.directional.length=g,n.spot.length=M,n.rectArea.length=v,n.point.length=x,n.hemi.length=_,n.directionalShadow.length=A,n.directionalShadowMap.length=A,n.pointShadow.length=w,n.pointShadowMap.length=w,n.spotShadow.length=b,n.spotShadowMap.length=b,n.directionalShadowMatrix.length=A,n.pointShadowMatrix.length=w,n.spotLightMatrix.length=b+B-U,n.spotLightMap.length=B,n.numSpotLightShadowsWithMaps=U,n.numLightProbes=O,H.directionalLength=g,H.pointLength=x,H.spotLength=M,H.rectAreaLength=v,H.hemiLength=_,H.numDirectionalShadows=A,H.numPointShadows=w,H.numSpotShadows=b,H.numSpotMaps=B,H.numLightProbes=O,n.version=iR++)}function u(h,f){let p=0,m=0,g=0,x=0,M=0;const v=f.matrixWorldInverse;for(let _=0,A=h.length;_<A;_++){const w=h[_];if(w.isDirectionalLight){const b=n.directional[p];b.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),b.direction.sub(i),b.direction.transformDirection(v),p++}else if(w.isSpotLight){const b=n.spot[g];b.position.setFromMatrixPosition(w.matrixWorld),b.position.applyMatrix4(v),b.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),b.direction.sub(i),b.direction.transformDirection(v),g++}else if(w.isRectAreaLight){const b=n.rectArea[x];b.position.setFromMatrixPosition(w.matrixWorld),b.position.applyMatrix4(v),a.identity(),s.copy(w.matrixWorld),s.premultiply(v),a.extractRotation(s),b.halfWidth.set(w.width*.5,0,0),b.halfHeight.set(0,w.height*.5,0),b.halfWidth.applyMatrix4(a),b.halfHeight.applyMatrix4(a),x++}else if(w.isPointLight){const b=n.point[m];b.position.setFromMatrixPosition(w.matrixWorld),b.position.applyMatrix4(v),m++}else if(w.isHemisphereLight){const b=n.hemi[M];b.direction.setFromMatrixPosition(w.matrixWorld),b.direction.transformDirection(v),M++}}}return{setup:c,setupView:u,state:n}}function Mm(r){const e=new sR(r),t=[],n=[];function i(f){h.camera=f,t.length=0,n.length=0}function s(f){t.push(f)}function a(f){n.push(f)}function c(){e.setup(t)}function u(f){e.setupView(t,f)}const h={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:h,setupLights:c,setupLightsView:u,pushLight:s,pushShadow:a}}function oR(r){let e=new WeakMap;function t(i,s=0){const a=e.get(i);let c;return a===void 0?(c=new Mm(r),e.set(i,[c])):s>=a.length?(c=new Mm(r),a.push(c)):c=a[s],c}function n(){e=new WeakMap}return{get:t,dispose:n}}class aR extends Ai{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=VT,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class cR extends Ai{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const lR=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,uR=`uniform sampler2D shadow_pass;
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
}`;function hR(r,e,t){let n=new xd;const i=new tt,s=new tt,a=new Dt,c=new aR({depthPacking:GT}),u=new cR,h={},f=t.maxTextureSize,p={[Ji]:qn,[qn]:Ji,[Xn]:Xn},m=new Mr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new tt},radius:{value:4}},vertexShader:lR,fragmentShader:uR}),g=m.clone();g.defines.HORIZONTAL_PASS=1;const x=new mn;x.setAttribute("position",new an(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const M=new Ee(x,m),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=ug;let _=this.type;this.render=function(U,O,H){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||U.length===0)return;const L=r.getRenderTarget(),P=r.getActiveCubeFace(),V=r.getActiveMipmapLevel(),ee=r.state;ee.setBlending(br),ee.buffers.color.setClear(1,1,1,1),ee.buffers.depth.setTest(!0),ee.setScissorTest(!1);const Q=_!==Xi&&this.type===Xi,ae=_===Xi&&this.type!==Xi;for(let ce=0,J=U.length;ce<J;ce++){const de=U[ce],re=de.shadow;if(re===void 0){console.warn("THREE.WebGLShadowMap:",de,"has no shadow.");continue}if(re.autoUpdate===!1&&re.needsUpdate===!1)continue;i.copy(re.mapSize);const _e=re.getFrameExtents();if(i.multiply(_e),s.copy(re.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(s.x=Math.floor(f/_e.x),i.x=s.x*_e.x,re.mapSize.x=s.x),i.y>f&&(s.y=Math.floor(f/_e.y),i.y=s.y*_e.y,re.mapSize.y=s.y)),re.map===null||Q===!0||ae===!0){const Ue=this.type!==Xi?{minFilter:zn,magFilter:zn}:{};re.map!==null&&re.map.dispose(),re.map=new os(i.x,i.y,Ue),re.map.texture.name=de.name+".shadowMap",re.camera.updateProjectionMatrix()}r.setRenderTarget(re.map),r.clear();const Me=re.getViewportCount();for(let Ue=0;Ue<Me;Ue++){const Je=re.getViewport(Ue);a.set(s.x*Je.x,s.y*Je.y,s.x*Je.z,s.y*Je.w),ee.viewport(a),re.updateMatrices(de,Ue),n=re.getFrustum(),b(O,H,re.camera,de,this.type)}re.isPointLightShadow!==!0&&this.type===Xi&&A(re,H),re.needsUpdate=!1}_=this.type,v.needsUpdate=!1,r.setRenderTarget(L,P,V)};function A(U,O){const H=e.update(M);m.defines.VSM_SAMPLES!==U.blurSamples&&(m.defines.VSM_SAMPLES=U.blurSamples,g.defines.VSM_SAMPLES=U.blurSamples,m.needsUpdate=!0,g.needsUpdate=!0),U.mapPass===null&&(U.mapPass=new os(i.x,i.y)),m.uniforms.shadow_pass.value=U.map.texture,m.uniforms.resolution.value=U.mapSize,m.uniforms.radius.value=U.radius,r.setRenderTarget(U.mapPass),r.clear(),r.renderBufferDirect(O,null,H,m,M,null),g.uniforms.shadow_pass.value=U.mapPass.texture,g.uniforms.resolution.value=U.mapSize,g.uniforms.radius.value=U.radius,r.setRenderTarget(U.map),r.clear(),r.renderBufferDirect(O,null,H,g,M,null)}function w(U,O,H,L){let P=null;const V=H.isPointLight===!0?U.customDistanceMaterial:U.customDepthMaterial;if(V!==void 0)P=V;else if(P=H.isPointLight===!0?u:c,r.localClippingEnabled&&O.clipShadows===!0&&Array.isArray(O.clippingPlanes)&&O.clippingPlanes.length!==0||O.displacementMap&&O.displacementScale!==0||O.alphaMap&&O.alphaTest>0||O.map&&O.alphaTest>0){const ee=P.uuid,Q=O.uuid;let ae=h[ee];ae===void 0&&(ae={},h[ee]=ae);let ce=ae[Q];ce===void 0&&(ce=P.clone(),ae[Q]=ce,O.addEventListener("dispose",B)),P=ce}if(P.visible=O.visible,P.wireframe=O.wireframe,L===Xi?P.side=O.shadowSide!==null?O.shadowSide:O.side:P.side=O.shadowSide!==null?O.shadowSide:p[O.side],P.alphaMap=O.alphaMap,P.alphaTest=O.alphaTest,P.map=O.map,P.clipShadows=O.clipShadows,P.clippingPlanes=O.clippingPlanes,P.clipIntersection=O.clipIntersection,P.displacementMap=O.displacementMap,P.displacementScale=O.displacementScale,P.displacementBias=O.displacementBias,P.wireframeLinewidth=O.wireframeLinewidth,P.linewidth=O.linewidth,H.isPointLight===!0&&P.isMeshDistanceMaterial===!0){const ee=r.properties.get(P);ee.light=H}return P}function b(U,O,H,L,P){if(U.visible===!1)return;if(U.layers.test(O.layers)&&(U.isMesh||U.isLine||U.isPoints)&&(U.castShadow||U.receiveShadow&&P===Xi)&&(!U.frustumCulled||n.intersectsObject(U))){U.modelViewMatrix.multiplyMatrices(H.matrixWorldInverse,U.matrixWorld);const Q=e.update(U),ae=U.material;if(Array.isArray(ae)){const ce=Q.groups;for(let J=0,de=ce.length;J<de;J++){const re=ce[J],_e=ae[re.materialIndex];if(_e&&_e.visible){const Me=w(U,_e,L,P);U.onBeforeShadow(r,U,O,H,Q,Me,re),r.renderBufferDirect(H,null,Q,Me,U,re),U.onAfterShadow(r,U,O,H,Q,Me,re)}}}else if(ae.visible){const ce=w(U,ae,L,P);U.onBeforeShadow(r,U,O,H,Q,ce,null),r.renderBufferDirect(H,null,Q,ce,U,null),U.onAfterShadow(r,U,O,H,Q,ce,null)}}const ee=U.children;for(let Q=0,ae=ee.length;Q<ae;Q++)b(ee[Q],O,H,L,P)}function B(U){U.target.removeEventListener("dispose",B);for(const H in h){const L=h[H],P=U.target.uuid;P in L&&(L[P].dispose(),delete L[P])}}}const dR={[vh]:yh,[xh]:Mh,[bh]:Th,[$s]:Sh,[yh]:vh,[Mh]:xh,[Th]:bh,[Sh]:$s};function fR(r,e){function t(){let W=!1;const Te=new Dt;let R=null;const z=new Dt(0,0,0,0);return{setMask:function(K){R!==K&&!W&&(r.colorMask(K,K,K,K),R=K)},setLocked:function(K){W=K},setClear:function(K,ie,ye,xe,we){we===!0&&(K*=xe,ie*=xe,ye*=xe),Te.set(K,ie,ye,xe),z.equals(Te)===!1&&(r.clearColor(K,ie,ye,xe),z.copy(Te))},reset:function(){W=!1,R=null,z.set(-1,0,0,0)}}}function n(){let W=!1,Te=!1,R=null,z=null,K=null;return{setReversed:function(ie){if(Te!==ie){const ye=e.get("EXT_clip_control");Te?ye.clipControlEXT(ye.LOWER_LEFT_EXT,ye.ZERO_TO_ONE_EXT):ye.clipControlEXT(ye.LOWER_LEFT_EXT,ye.NEGATIVE_ONE_TO_ONE_EXT);const xe=K;K=null,this.setClear(xe)}Te=ie},getReversed:function(){return Te},setTest:function(ie){ie?Se(r.DEPTH_TEST):qe(r.DEPTH_TEST)},setMask:function(ie){R!==ie&&!W&&(r.depthMask(ie),R=ie)},setFunc:function(ie){if(Te&&(ie=dR[ie]),z!==ie){switch(ie){case vh:r.depthFunc(r.NEVER);break;case yh:r.depthFunc(r.ALWAYS);break;case xh:r.depthFunc(r.LESS);break;case $s:r.depthFunc(r.LEQUAL);break;case bh:r.depthFunc(r.EQUAL);break;case Sh:r.depthFunc(r.GEQUAL);break;case Mh:r.depthFunc(r.GREATER);break;case Th:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}z=ie}},setLocked:function(ie){W=ie},setClear:function(ie){K!==ie&&(Te&&(ie=1-ie),r.clearDepth(ie),K=ie)},reset:function(){W=!1,R=null,z=null,K=null,Te=!1}}}function i(){let W=!1,Te=null,R=null,z=null,K=null,ie=null,ye=null,xe=null,we=null;return{setTest:function(Ie){W||(Ie?Se(r.STENCIL_TEST):qe(r.STENCIL_TEST))},setMask:function(Ie){Te!==Ie&&!W&&(r.stencilMask(Ie),Te=Ie)},setFunc:function(Ie,nt,Et){(R!==Ie||z!==nt||K!==Et)&&(r.stencilFunc(Ie,nt,Et),R=Ie,z=nt,K=Et)},setOp:function(Ie,nt,Et){(ie!==Ie||ye!==nt||xe!==Et)&&(r.stencilOp(Ie,nt,Et),ie=Ie,ye=nt,xe=Et)},setLocked:function(Ie){W=Ie},setClear:function(Ie){we!==Ie&&(r.clearStencil(Ie),we=Ie)},reset:function(){W=!1,Te=null,R=null,z=null,K=null,ie=null,ye=null,xe=null,we=null}}}const s=new t,a=new n,c=new i,u=new WeakMap,h=new WeakMap;let f={},p={},m=new WeakMap,g=[],x=null,M=!1,v=null,_=null,A=null,w=null,b=null,B=null,U=null,O=new $e(0,0,0),H=0,L=!1,P=null,V=null,ee=null,Q=null,ae=null;const ce=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let J=!1,de=0;const re=r.getParameter(r.VERSION);re.indexOf("WebGL")!==-1?(de=parseFloat(/^WebGL (\d)/.exec(re)[1]),J=de>=1):re.indexOf("OpenGL ES")!==-1&&(de=parseFloat(/^OpenGL ES (\d)/.exec(re)[1]),J=de>=2);let _e=null,Me={};const Ue=r.getParameter(r.SCISSOR_BOX),Je=r.getParameter(r.VIEWPORT),pt=new Dt().fromArray(Ue),le=new Dt().fromArray(Je);function pe(W,Te,R,z){const K=new Uint8Array(4),ie=r.createTexture();r.bindTexture(W,ie),r.texParameteri(W,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(W,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let ye=0;ye<R;ye++)W===r.TEXTURE_3D||W===r.TEXTURE_2D_ARRAY?r.texImage3D(Te,0,r.RGBA,1,1,z,0,r.RGBA,r.UNSIGNED_BYTE,K):r.texImage2D(Te+ye,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,K);return ie}const Fe={};Fe[r.TEXTURE_2D]=pe(r.TEXTURE_2D,r.TEXTURE_2D,1),Fe[r.TEXTURE_CUBE_MAP]=pe(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Fe[r.TEXTURE_2D_ARRAY]=pe(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Fe[r.TEXTURE_3D]=pe(r.TEXTURE_3D,r.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),c.setClear(0),Se(r.DEPTH_TEST),a.setFunc($s),ut(!1),mt(Ap),Se(r.CULL_FACE),X(br);function Se(W){f[W]!==!0&&(r.enable(W),f[W]=!0)}function qe(W){f[W]!==!1&&(r.disable(W),f[W]=!1)}function it(W,Te){return p[W]!==Te?(r.bindFramebuffer(W,Te),p[W]=Te,W===r.DRAW_FRAMEBUFFER&&(p[r.FRAMEBUFFER]=Te),W===r.FRAMEBUFFER&&(p[r.DRAW_FRAMEBUFFER]=Te),!0):!1}function at(W,Te){let R=g,z=!1;if(W){R=m.get(Te),R===void 0&&(R=[],m.set(Te,R));const K=W.textures;if(R.length!==K.length||R[0]!==r.COLOR_ATTACHMENT0){for(let ie=0,ye=K.length;ie<ye;ie++)R[ie]=r.COLOR_ATTACHMENT0+ie;R.length=K.length,z=!0}}else R[0]!==r.BACK&&(R[0]=r.BACK,z=!0);z&&r.drawBuffers(R)}function Pt(W){return x!==W?(r.useProgram(W),x=W,!0):!1}const lt={[ns]:r.FUNC_ADD,[dT]:r.FUNC_SUBTRACT,[fT]:r.FUNC_REVERSE_SUBTRACT};lt[pT]=r.MIN,lt[mT]=r.MAX;const zt={[gT]:r.ZERO,[_T]:r.ONE,[vT]:r.SRC_COLOR,[gh]:r.SRC_ALPHA,[TT]:r.SRC_ALPHA_SATURATE,[ST]:r.DST_COLOR,[xT]:r.DST_ALPHA,[yT]:r.ONE_MINUS_SRC_COLOR,[_h]:r.ONE_MINUS_SRC_ALPHA,[MT]:r.ONE_MINUS_DST_COLOR,[bT]:r.ONE_MINUS_DST_ALPHA,[ET]:r.CONSTANT_COLOR,[AT]:r.ONE_MINUS_CONSTANT_COLOR,[wT]:r.CONSTANT_ALPHA,[PT]:r.ONE_MINUS_CONSTANT_ALPHA};function X(W,Te,R,z,K,ie,ye,xe,we,Ie){if(W===br){M===!0&&(qe(r.BLEND),M=!1);return}if(M===!1&&(Se(r.BLEND),M=!0),W!==hT){if(W!==v||Ie!==L){if((_!==ns||b!==ns)&&(r.blendEquation(r.FUNC_ADD),_=ns,b=ns),Ie)switch(W){case Xs:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case wp:r.blendFunc(r.ONE,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Rp:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",W);break}else switch(W){case Xs:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case wp:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Rp:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",W);break}A=null,w=null,B=null,U=null,O.set(0,0,0),H=0,v=W,L=Ie}return}K=K||Te,ie=ie||R,ye=ye||z,(Te!==_||K!==b)&&(r.blendEquationSeparate(lt[Te],lt[K]),_=Te,b=K),(R!==A||z!==w||ie!==B||ye!==U)&&(r.blendFuncSeparate(zt[R],zt[z],zt[ie],zt[ye]),A=R,w=z,B=ie,U=ye),(xe.equals(O)===!1||we!==H)&&(r.blendColor(xe.r,xe.g,xe.b,we),O.copy(xe),H=we),v=W,L=!1}function rn(W,Te){W.side===Xn?qe(r.CULL_FACE):Se(r.CULL_FACE);let R=W.side===qn;Te&&(R=!R),ut(R),W.blending===Xs&&W.transparent===!1?X(br):X(W.blending,W.blendEquation,W.blendSrc,W.blendDst,W.blendEquationAlpha,W.blendSrcAlpha,W.blendDstAlpha,W.blendColor,W.blendAlpha,W.premultipliedAlpha),a.setFunc(W.depthFunc),a.setTest(W.depthTest),a.setMask(W.depthWrite),s.setMask(W.colorWrite);const z=W.stencilWrite;c.setTest(z),z&&(c.setMask(W.stencilWriteMask),c.setFunc(W.stencilFunc,W.stencilRef,W.stencilFuncMask),c.setOp(W.stencilFail,W.stencilZFail,W.stencilZPass)),Tt(W.polygonOffset,W.polygonOffsetFactor,W.polygonOffsetUnits),W.alphaToCoverage===!0?Se(r.SAMPLE_ALPHA_TO_COVERAGE):qe(r.SAMPLE_ALPHA_TO_COVERAGE)}function ut(W){P!==W&&(W?r.frontFace(r.CW):r.frontFace(r.CCW),P=W)}function mt(W){W!==cT?(Se(r.CULL_FACE),W!==V&&(W===Ap?r.cullFace(r.BACK):W===lT?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):qe(r.CULL_FACE),V=W}function We(W){W!==ee&&(J&&r.lineWidth(W),ee=W)}function Tt(W,Te,R){W?(Se(r.POLYGON_OFFSET_FILL),(Q!==Te||ae!==R)&&(r.polygonOffset(Te,R),Q=Te,ae=R)):qe(r.POLYGON_OFFSET_FILL)}function ke(W){W?Se(r.SCISSOR_TEST):qe(r.SCISSOR_TEST)}function N(W){W===void 0&&(W=r.TEXTURE0+ce-1),_e!==W&&(r.activeTexture(W),_e=W)}function E(W,Te,R){R===void 0&&(_e===null?R=r.TEXTURE0+ce-1:R=_e);let z=Me[R];z===void 0&&(z={type:void 0,texture:void 0},Me[R]=z),(z.type!==W||z.texture!==Te)&&(_e!==R&&(r.activeTexture(R),_e=R),r.bindTexture(W,Te||Fe[W]),z.type=W,z.texture=Te)}function Z(){const W=Me[_e];W!==void 0&&W.type!==void 0&&(r.bindTexture(W.type,null),W.type=void 0,W.texture=void 0)}function ue(){try{r.compressedTexImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function fe(){try{r.compressedTexImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function he(){try{r.texSubImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Oe(){try{r.texSubImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Ae(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Le(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function ht(){try{r.texStorage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function me(){try{r.texStorage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function De(){try{r.texImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Be(){try{r.texImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Ze(W){pt.equals(W)===!1&&(r.scissor(W.x,W.y,W.z,W.w),pt.copy(W))}function Ne(W){le.equals(W)===!1&&(r.viewport(W.x,W.y,W.z,W.w),le.copy(W))}function _t(W,Te){let R=h.get(Te);R===void 0&&(R=new WeakMap,h.set(Te,R));let z=R.get(W);z===void 0&&(z=r.getUniformBlockIndex(Te,W.name),R.set(W,z))}function st(W,Te){const z=h.get(Te).get(W);u.get(Te)!==z&&(r.uniformBlockBinding(Te,z,W.__bindingPointIndex),u.set(Te,z))}function Ct(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),a.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),f={},_e=null,Me={},p={},m=new WeakMap,g=[],x=null,M=!1,v=null,_=null,A=null,w=null,b=null,B=null,U=null,O=new $e(0,0,0),H=0,L=!1,P=null,V=null,ee=null,Q=null,ae=null,pt.set(0,0,r.canvas.width,r.canvas.height),le.set(0,0,r.canvas.width,r.canvas.height),s.reset(),a.reset(),c.reset()}return{buffers:{color:s,depth:a,stencil:c},enable:Se,disable:qe,bindFramebuffer:it,drawBuffers:at,useProgram:Pt,setBlending:X,setMaterial:rn,setFlipSided:ut,setCullFace:mt,setLineWidth:We,setPolygonOffset:Tt,setScissorTest:ke,activeTexture:N,bindTexture:E,unbindTexture:Z,compressedTexImage2D:ue,compressedTexImage3D:fe,texImage2D:De,texImage3D:Be,updateUBOMapping:_t,uniformBlockBinding:st,texStorage2D:ht,texStorage3D:me,texSubImage2D:he,texSubImage3D:Oe,compressedTexSubImage2D:Ae,compressedTexSubImage3D:Le,scissor:Ze,viewport:Ne,reset:Ct}}function Tm(r,e,t,n){const i=pR(n);switch(t){case vg:return r*e;case xg:return r*e;case bg:return r*e*2;case dd:return r*e/i.components*i.byteLength;case fd:return r*e/i.components*i.byteLength;case Sg:return r*e*2/i.components*i.byteLength;case pd:return r*e*2/i.components*i.byteLength;case yg:return r*e*3/i.components*i.byteLength;case li:return r*e*4/i.components*i.byteLength;case md:return r*e*4/i.components*i.byteLength;case Tc:case Ec:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ac:case wc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Ph:case Ch:return Math.max(r,16)*Math.max(e,8)/4;case wh:case Rh:return Math.max(r,8)*Math.max(e,8)/2;case Ih:case Lh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Dh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Nh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Oh:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case Uh:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case Fh:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case Bh:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case kh:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case zh:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case Hh:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case Vh:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case Gh:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case Wh:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case jh:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case Xh:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case qh:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case Pc:case Yh:case Kh:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Mg:case $h:return Math.ceil(r/4)*Math.ceil(e/4)*8;case Zh:case Jh:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function pR(r){switch(r){case Qi:case mg:return{byteLength:1,components:1};case Jo:case gg:case na:return{byteLength:2,components:1};case ud:case hd:return{byteLength:2,components:4};case ss:case ld:case vi:return{byteLength:4,components:1};case _g:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function mR(r,e,t,n,i,s,a){const c=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,u=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new tt,f=new WeakMap;let p;const m=new WeakMap;let g=!1;try{g=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function x(N,E){return g?new OffscreenCanvas(N,E):ta("canvas")}function M(N,E,Z){let ue=1;const fe=ke(N);if((fe.width>Z||fe.height>Z)&&(ue=Z/Math.max(fe.width,fe.height)),ue<1)if(typeof HTMLImageElement<"u"&&N instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&N instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&N instanceof ImageBitmap||typeof VideoFrame<"u"&&N instanceof VideoFrame){const he=Math.floor(ue*fe.width),Oe=Math.floor(ue*fe.height);p===void 0&&(p=x(he,Oe));const Ae=E?x(he,Oe):p;return Ae.width=he,Ae.height=Oe,Ae.getContext("2d").drawImage(N,0,0,he,Oe),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+fe.width+"x"+fe.height+") to ("+he+"x"+Oe+")."),Ae}else return"data"in N&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+fe.width+"x"+fe.height+")."),N;return N}function v(N){return N.generateMipmaps}function _(N){r.generateMipmap(N)}function A(N){return N.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:N.isWebGL3DRenderTarget?r.TEXTURE_3D:N.isWebGLArrayRenderTarget||N.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function w(N,E,Z,ue,fe=!1){if(N!==null){if(r[N]!==void 0)return r[N];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+N+"'")}let he=E;if(E===r.RED&&(Z===r.FLOAT&&(he=r.R32F),Z===r.HALF_FLOAT&&(he=r.R16F),Z===r.UNSIGNED_BYTE&&(he=r.R8)),E===r.RED_INTEGER&&(Z===r.UNSIGNED_BYTE&&(he=r.R8UI),Z===r.UNSIGNED_SHORT&&(he=r.R16UI),Z===r.UNSIGNED_INT&&(he=r.R32UI),Z===r.BYTE&&(he=r.R8I),Z===r.SHORT&&(he=r.R16I),Z===r.INT&&(he=r.R32I)),E===r.RG&&(Z===r.FLOAT&&(he=r.RG32F),Z===r.HALF_FLOAT&&(he=r.RG16F),Z===r.UNSIGNED_BYTE&&(he=r.RG8)),E===r.RG_INTEGER&&(Z===r.UNSIGNED_BYTE&&(he=r.RG8UI),Z===r.UNSIGNED_SHORT&&(he=r.RG16UI),Z===r.UNSIGNED_INT&&(he=r.RG32UI),Z===r.BYTE&&(he=r.RG8I),Z===r.SHORT&&(he=r.RG16I),Z===r.INT&&(he=r.RG32I)),E===r.RGB_INTEGER&&(Z===r.UNSIGNED_BYTE&&(he=r.RGB8UI),Z===r.UNSIGNED_SHORT&&(he=r.RGB16UI),Z===r.UNSIGNED_INT&&(he=r.RGB32UI),Z===r.BYTE&&(he=r.RGB8I),Z===r.SHORT&&(he=r.RGB16I),Z===r.INT&&(he=r.RGB32I)),E===r.RGBA_INTEGER&&(Z===r.UNSIGNED_BYTE&&(he=r.RGBA8UI),Z===r.UNSIGNED_SHORT&&(he=r.RGBA16UI),Z===r.UNSIGNED_INT&&(he=r.RGBA32UI),Z===r.BYTE&&(he=r.RGBA8I),Z===r.SHORT&&(he=r.RGBA16I),Z===r.INT&&(he=r.RGBA32I)),E===r.RGB&&Z===r.UNSIGNED_INT_5_9_9_9_REV&&(he=r.RGB9_E5),E===r.RGBA){const Oe=fe?zc:wt.getTransfer(ue);Z===r.FLOAT&&(he=r.RGBA32F),Z===r.HALF_FLOAT&&(he=r.RGBA16F),Z===r.UNSIGNED_BYTE&&(he=Oe===Ht?r.SRGB8_ALPHA8:r.RGBA8),Z===r.UNSIGNED_SHORT_4_4_4_4&&(he=r.RGBA4),Z===r.UNSIGNED_SHORT_5_5_5_1&&(he=r.RGB5_A1)}return(he===r.R16F||he===r.R32F||he===r.RG16F||he===r.RG32F||he===r.RGBA16F||he===r.RGBA32F)&&e.get("EXT_color_buffer_float"),he}function b(N,E){let Z;return N?E===null||E===ss||E===eo?Z=r.DEPTH24_STENCIL8:E===vi?Z=r.DEPTH32F_STENCIL8:E===Jo&&(Z=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===ss||E===eo?Z=r.DEPTH_COMPONENT24:E===vi?Z=r.DEPTH_COMPONENT32F:E===Jo&&(Z=r.DEPTH_COMPONENT16),Z}function B(N,E){return v(N)===!0||N.isFramebufferTexture&&N.minFilter!==zn&&N.minFilter!==ii?Math.log2(Math.max(E.width,E.height))+1:N.mipmaps!==void 0&&N.mipmaps.length>0?N.mipmaps.length:N.isCompressedTexture&&Array.isArray(N.image)?E.mipmaps.length:1}function U(N){const E=N.target;E.removeEventListener("dispose",U),H(E),E.isVideoTexture&&f.delete(E)}function O(N){const E=N.target;E.removeEventListener("dispose",O),P(E)}function H(N){const E=n.get(N);if(E.__webglInit===void 0)return;const Z=N.source,ue=m.get(Z);if(ue){const fe=ue[E.__cacheKey];fe.usedTimes--,fe.usedTimes===0&&L(N),Object.keys(ue).length===0&&m.delete(Z)}n.remove(N)}function L(N){const E=n.get(N);r.deleteTexture(E.__webglTexture);const Z=N.source,ue=m.get(Z);delete ue[E.__cacheKey],a.memory.textures--}function P(N){const E=n.get(N);if(N.depthTexture&&(N.depthTexture.dispose(),n.remove(N.depthTexture)),N.isWebGLCubeRenderTarget)for(let ue=0;ue<6;ue++){if(Array.isArray(E.__webglFramebuffer[ue]))for(let fe=0;fe<E.__webglFramebuffer[ue].length;fe++)r.deleteFramebuffer(E.__webglFramebuffer[ue][fe]);else r.deleteFramebuffer(E.__webglFramebuffer[ue]);E.__webglDepthbuffer&&r.deleteRenderbuffer(E.__webglDepthbuffer[ue])}else{if(Array.isArray(E.__webglFramebuffer))for(let ue=0;ue<E.__webglFramebuffer.length;ue++)r.deleteFramebuffer(E.__webglFramebuffer[ue]);else r.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&r.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&r.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let ue=0;ue<E.__webglColorRenderbuffer.length;ue++)E.__webglColorRenderbuffer[ue]&&r.deleteRenderbuffer(E.__webglColorRenderbuffer[ue]);E.__webglDepthRenderbuffer&&r.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const Z=N.textures;for(let ue=0,fe=Z.length;ue<fe;ue++){const he=n.get(Z[ue]);he.__webglTexture&&(r.deleteTexture(he.__webglTexture),a.memory.textures--),n.remove(Z[ue])}n.remove(N)}let V=0;function ee(){V=0}function Q(){const N=V;return N>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+N+" texture units while this GPU supports only "+i.maxTextures),V+=1,N}function ae(N){const E=[];return E.push(N.wrapS),E.push(N.wrapT),E.push(N.wrapR||0),E.push(N.magFilter),E.push(N.minFilter),E.push(N.anisotropy),E.push(N.internalFormat),E.push(N.format),E.push(N.type),E.push(N.generateMipmaps),E.push(N.premultiplyAlpha),E.push(N.flipY),E.push(N.unpackAlignment),E.push(N.colorSpace),E.join()}function ce(N,E){const Z=n.get(N);if(N.isVideoTexture&&We(N),N.isRenderTargetTexture===!1&&N.version>0&&Z.__version!==N.version){const ue=N.image;if(ue===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ue.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{le(Z,N,E);return}}t.bindTexture(r.TEXTURE_2D,Z.__webglTexture,r.TEXTURE0+E)}function J(N,E){const Z=n.get(N);if(N.version>0&&Z.__version!==N.version){le(Z,N,E);return}t.bindTexture(r.TEXTURE_2D_ARRAY,Z.__webglTexture,r.TEXTURE0+E)}function de(N,E){const Z=n.get(N);if(N.version>0&&Z.__version!==N.version){le(Z,N,E);return}t.bindTexture(r.TEXTURE_3D,Z.__webglTexture,r.TEXTURE0+E)}function re(N,E){const Z=n.get(N);if(N.version>0&&Z.__version!==N.version){pe(Z,N,E);return}t.bindTexture(r.TEXTURE_CUBE_MAP,Z.__webglTexture,r.TEXTURE0+E)}const _e={[Qs]:r.REPEAT,[yr]:r.CLAMP_TO_EDGE,[Dc]:r.MIRRORED_REPEAT},Me={[zn]:r.NEAREST,[pg]:r.NEAREST_MIPMAP_NEAREST,[Go]:r.NEAREST_MIPMAP_LINEAR,[ii]:r.LINEAR,[Mc]:r.LINEAR_MIPMAP_NEAREST,[Yi]:r.LINEAR_MIPMAP_LINEAR},Ue={[jT]:r.NEVER,[ZT]:r.ALWAYS,[XT]:r.LESS,[Ag]:r.LEQUAL,[qT]:r.EQUAL,[$T]:r.GEQUAL,[YT]:r.GREATER,[KT]:r.NOTEQUAL};function Je(N,E){if(E.type===vi&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===ii||E.magFilter===Mc||E.magFilter===Go||E.magFilter===Yi||E.minFilter===ii||E.minFilter===Mc||E.minFilter===Go||E.minFilter===Yi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(N,r.TEXTURE_WRAP_S,_e[E.wrapS]),r.texParameteri(N,r.TEXTURE_WRAP_T,_e[E.wrapT]),(N===r.TEXTURE_3D||N===r.TEXTURE_2D_ARRAY)&&r.texParameteri(N,r.TEXTURE_WRAP_R,_e[E.wrapR]),r.texParameteri(N,r.TEXTURE_MAG_FILTER,Me[E.magFilter]),r.texParameteri(N,r.TEXTURE_MIN_FILTER,Me[E.minFilter]),E.compareFunction&&(r.texParameteri(N,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(N,r.TEXTURE_COMPARE_FUNC,Ue[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===zn||E.minFilter!==Go&&E.minFilter!==Yi||E.type===vi&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");r.texParameterf(N,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,i.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function pt(N,E){let Z=!1;N.__webglInit===void 0&&(N.__webglInit=!0,E.addEventListener("dispose",U));const ue=E.source;let fe=m.get(ue);fe===void 0&&(fe={},m.set(ue,fe));const he=ae(E);if(he!==N.__cacheKey){fe[he]===void 0&&(fe[he]={texture:r.createTexture(),usedTimes:0},a.memory.textures++,Z=!0),fe[he].usedTimes++;const Oe=fe[N.__cacheKey];Oe!==void 0&&(fe[N.__cacheKey].usedTimes--,Oe.usedTimes===0&&L(E)),N.__cacheKey=he,N.__webglTexture=fe[he].texture}return Z}function le(N,E,Z){let ue=r.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(ue=r.TEXTURE_2D_ARRAY),E.isData3DTexture&&(ue=r.TEXTURE_3D);const fe=pt(N,E),he=E.source;t.bindTexture(ue,N.__webglTexture,r.TEXTURE0+Z);const Oe=n.get(he);if(he.version!==Oe.__version||fe===!0){t.activeTexture(r.TEXTURE0+Z);const Ae=wt.getPrimaries(wt.workingColorSpace),Le=E.colorSpace===vr?null:wt.getPrimaries(E.colorSpace),ht=E.colorSpace===vr||Ae===Le?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,E.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,E.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,ht);let me=M(E.image,!1,i.maxTextureSize);me=Tt(E,me);const De=s.convert(E.format,E.colorSpace),Be=s.convert(E.type);let Ze=w(E.internalFormat,De,Be,E.colorSpace,E.isVideoTexture);Je(ue,E);let Ne;const _t=E.mipmaps,st=E.isVideoTexture!==!0,Ct=Oe.__version===void 0||fe===!0,W=he.dataReady,Te=B(E,me);if(E.isDepthTexture)Ze=b(E.format===to,E.type),Ct&&(st?t.texStorage2D(r.TEXTURE_2D,1,Ze,me.width,me.height):t.texImage2D(r.TEXTURE_2D,0,Ze,me.width,me.height,0,De,Be,null));else if(E.isDataTexture)if(_t.length>0){st&&Ct&&t.texStorage2D(r.TEXTURE_2D,Te,Ze,_t[0].width,_t[0].height);for(let R=0,z=_t.length;R<z;R++)Ne=_t[R],st?W&&t.texSubImage2D(r.TEXTURE_2D,R,0,0,Ne.width,Ne.height,De,Be,Ne.data):t.texImage2D(r.TEXTURE_2D,R,Ze,Ne.width,Ne.height,0,De,Be,Ne.data);E.generateMipmaps=!1}else st?(Ct&&t.texStorage2D(r.TEXTURE_2D,Te,Ze,me.width,me.height),W&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,me.width,me.height,De,Be,me.data)):t.texImage2D(r.TEXTURE_2D,0,Ze,me.width,me.height,0,De,Be,me.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){st&&Ct&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Te,Ze,_t[0].width,_t[0].height,me.depth);for(let R=0,z=_t.length;R<z;R++)if(Ne=_t[R],E.format!==li)if(De!==null)if(st){if(W)if(E.layerUpdates.size>0){const K=Tm(Ne.width,Ne.height,E.format,E.type);for(const ie of E.layerUpdates){const ye=Ne.data.subarray(ie*K/Ne.data.BYTES_PER_ELEMENT,(ie+1)*K/Ne.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,R,0,0,ie,Ne.width,Ne.height,1,De,ye)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,R,0,0,0,Ne.width,Ne.height,me.depth,De,Ne.data)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,R,Ze,Ne.width,Ne.height,me.depth,0,Ne.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else st?W&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,R,0,0,0,Ne.width,Ne.height,me.depth,De,Be,Ne.data):t.texImage3D(r.TEXTURE_2D_ARRAY,R,Ze,Ne.width,Ne.height,me.depth,0,De,Be,Ne.data)}else{st&&Ct&&t.texStorage2D(r.TEXTURE_2D,Te,Ze,_t[0].width,_t[0].height);for(let R=0,z=_t.length;R<z;R++)Ne=_t[R],E.format!==li?De!==null?st?W&&t.compressedTexSubImage2D(r.TEXTURE_2D,R,0,0,Ne.width,Ne.height,De,Ne.data):t.compressedTexImage2D(r.TEXTURE_2D,R,Ze,Ne.width,Ne.height,0,Ne.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):st?W&&t.texSubImage2D(r.TEXTURE_2D,R,0,0,Ne.width,Ne.height,De,Be,Ne.data):t.texImage2D(r.TEXTURE_2D,R,Ze,Ne.width,Ne.height,0,De,Be,Ne.data)}else if(E.isDataArrayTexture)if(st){if(Ct&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Te,Ze,me.width,me.height,me.depth),W)if(E.layerUpdates.size>0){const R=Tm(me.width,me.height,E.format,E.type);for(const z of E.layerUpdates){const K=me.data.subarray(z*R/me.data.BYTES_PER_ELEMENT,(z+1)*R/me.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,z,me.width,me.height,1,De,Be,K)}E.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,me.width,me.height,me.depth,De,Be,me.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,Ze,me.width,me.height,me.depth,0,De,Be,me.data);else if(E.isData3DTexture)st?(Ct&&t.texStorage3D(r.TEXTURE_3D,Te,Ze,me.width,me.height,me.depth),W&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,me.width,me.height,me.depth,De,Be,me.data)):t.texImage3D(r.TEXTURE_3D,0,Ze,me.width,me.height,me.depth,0,De,Be,me.data);else if(E.isFramebufferTexture){if(Ct)if(st)t.texStorage2D(r.TEXTURE_2D,Te,Ze,me.width,me.height);else{let R=me.width,z=me.height;for(let K=0;K<Te;K++)t.texImage2D(r.TEXTURE_2D,K,Ze,R,z,0,De,Be,null),R>>=1,z>>=1}}else if(_t.length>0){if(st&&Ct){const R=ke(_t[0]);t.texStorage2D(r.TEXTURE_2D,Te,Ze,R.width,R.height)}for(let R=0,z=_t.length;R<z;R++)Ne=_t[R],st?W&&t.texSubImage2D(r.TEXTURE_2D,R,0,0,De,Be,Ne):t.texImage2D(r.TEXTURE_2D,R,Ze,De,Be,Ne);E.generateMipmaps=!1}else if(st){if(Ct){const R=ke(me);t.texStorage2D(r.TEXTURE_2D,Te,Ze,R.width,R.height)}W&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,De,Be,me)}else t.texImage2D(r.TEXTURE_2D,0,Ze,De,Be,me);v(E)&&_(ue),Oe.__version=he.version,E.onUpdate&&E.onUpdate(E)}N.__version=E.version}function pe(N,E,Z){if(E.image.length!==6)return;const ue=pt(N,E),fe=E.source;t.bindTexture(r.TEXTURE_CUBE_MAP,N.__webglTexture,r.TEXTURE0+Z);const he=n.get(fe);if(fe.version!==he.__version||ue===!0){t.activeTexture(r.TEXTURE0+Z);const Oe=wt.getPrimaries(wt.workingColorSpace),Ae=E.colorSpace===vr?null:wt.getPrimaries(E.colorSpace),Le=E.colorSpace===vr||Oe===Ae?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,E.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,E.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,Le);const ht=E.isCompressedTexture||E.image[0].isCompressedTexture,me=E.image[0]&&E.image[0].isDataTexture,De=[];for(let z=0;z<6;z++)!ht&&!me?De[z]=M(E.image[z],!0,i.maxCubemapSize):De[z]=me?E.image[z].image:E.image[z],De[z]=Tt(E,De[z]);const Be=De[0],Ze=s.convert(E.format,E.colorSpace),Ne=s.convert(E.type),_t=w(E.internalFormat,Ze,Ne,E.colorSpace),st=E.isVideoTexture!==!0,Ct=he.__version===void 0||ue===!0,W=fe.dataReady;let Te=B(E,Be);Je(r.TEXTURE_CUBE_MAP,E);let R;if(ht){st&&Ct&&t.texStorage2D(r.TEXTURE_CUBE_MAP,Te,_t,Be.width,Be.height);for(let z=0;z<6;z++){R=De[z].mipmaps;for(let K=0;K<R.length;K++){const ie=R[K];E.format!==li?Ze!==null?st?W&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K,0,0,ie.width,ie.height,Ze,ie.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K,_t,ie.width,ie.height,0,ie.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):st?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K,0,0,ie.width,ie.height,Ze,Ne,ie.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K,_t,ie.width,ie.height,0,Ze,Ne,ie.data)}}}else{if(R=E.mipmaps,st&&Ct){R.length>0&&Te++;const z=ke(De[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,Te,_t,z.width,z.height)}for(let z=0;z<6;z++)if(me){st?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,0,0,0,De[z].width,De[z].height,Ze,Ne,De[z].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,0,_t,De[z].width,De[z].height,0,Ze,Ne,De[z].data);for(let K=0;K<R.length;K++){const ye=R[K].image[z].image;st?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K+1,0,0,ye.width,ye.height,Ze,Ne,ye.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K+1,_t,ye.width,ye.height,0,Ze,Ne,ye.data)}}else{st?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,0,0,0,Ze,Ne,De[z]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,0,_t,Ze,Ne,De[z]);for(let K=0;K<R.length;K++){const ie=R[K];st?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K+1,0,0,Ze,Ne,ie.image[z]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+z,K+1,_t,Ze,Ne,ie.image[z])}}}v(E)&&_(r.TEXTURE_CUBE_MAP),he.__version=fe.version,E.onUpdate&&E.onUpdate(E)}N.__version=E.version}function Fe(N,E,Z,ue,fe,he){const Oe=s.convert(Z.format,Z.colorSpace),Ae=s.convert(Z.type),Le=w(Z.internalFormat,Oe,Ae,Z.colorSpace),ht=n.get(E),me=n.get(Z);if(me.__renderTarget=E,!ht.__hasExternalTextures){const De=Math.max(1,E.width>>he),Be=Math.max(1,E.height>>he);fe===r.TEXTURE_3D||fe===r.TEXTURE_2D_ARRAY?t.texImage3D(fe,he,Le,De,Be,E.depth,0,Oe,Ae,null):t.texImage2D(fe,he,Le,De,Be,0,Oe,Ae,null)}t.bindFramebuffer(r.FRAMEBUFFER,N),mt(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,ue,fe,me.__webglTexture,0,ut(E)):(fe===r.TEXTURE_2D||fe>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&fe<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,ue,fe,me.__webglTexture,he),t.bindFramebuffer(r.FRAMEBUFFER,null)}function Se(N,E,Z){if(r.bindRenderbuffer(r.RENDERBUFFER,N),E.depthBuffer){const ue=E.depthTexture,fe=ue&&ue.isDepthTexture?ue.type:null,he=b(E.stencilBuffer,fe),Oe=E.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Ae=ut(E);mt(E)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Ae,he,E.width,E.height):Z?r.renderbufferStorageMultisample(r.RENDERBUFFER,Ae,he,E.width,E.height):r.renderbufferStorage(r.RENDERBUFFER,he,E.width,E.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,Oe,r.RENDERBUFFER,N)}else{const ue=E.textures;for(let fe=0;fe<ue.length;fe++){const he=ue[fe],Oe=s.convert(he.format,he.colorSpace),Ae=s.convert(he.type),Le=w(he.internalFormat,Oe,Ae,he.colorSpace),ht=ut(E);Z&&mt(E)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,ht,Le,E.width,E.height):mt(E)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,ht,Le,E.width,E.height):r.renderbufferStorage(r.RENDERBUFFER,Le,E.width,E.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function qe(N,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,N),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const ue=n.get(E.depthTexture);ue.__renderTarget=E,(!ue.__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),ce(E.depthTexture,0);const fe=ue.__webglTexture,he=ut(E);if(E.depthTexture.format===qs)mt(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,fe,0,he):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,fe,0);else if(E.depthTexture.format===to)mt(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,fe,0,he):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,fe,0);else throw new Error("Unknown depthTexture format")}function it(N){const E=n.get(N),Z=N.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==N.depthTexture){const ue=N.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),ue){const fe=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,ue.removeEventListener("dispose",fe)};ue.addEventListener("dispose",fe),E.__depthDisposeCallback=fe}E.__boundDepthTexture=ue}if(N.depthTexture&&!E.__autoAllocateDepthBuffer){if(Z)throw new Error("target.depthTexture not supported in Cube render targets");qe(E.__webglFramebuffer,N)}else if(Z){E.__webglDepthbuffer=[];for(let ue=0;ue<6;ue++)if(t.bindFramebuffer(r.FRAMEBUFFER,E.__webglFramebuffer[ue]),E.__webglDepthbuffer[ue]===void 0)E.__webglDepthbuffer[ue]=r.createRenderbuffer(),Se(E.__webglDepthbuffer[ue],N,!1);else{const fe=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,he=E.__webglDepthbuffer[ue];r.bindRenderbuffer(r.RENDERBUFFER,he),r.framebufferRenderbuffer(r.FRAMEBUFFER,fe,r.RENDERBUFFER,he)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=r.createRenderbuffer(),Se(E.__webglDepthbuffer,N,!1);else{const ue=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,fe=E.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,fe),r.framebufferRenderbuffer(r.FRAMEBUFFER,ue,r.RENDERBUFFER,fe)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function at(N,E,Z){const ue=n.get(N);E!==void 0&&Fe(ue.__webglFramebuffer,N,N.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),Z!==void 0&&it(N)}function Pt(N){const E=N.texture,Z=n.get(N),ue=n.get(E);N.addEventListener("dispose",O);const fe=N.textures,he=N.isWebGLCubeRenderTarget===!0,Oe=fe.length>1;if(Oe||(ue.__webglTexture===void 0&&(ue.__webglTexture=r.createTexture()),ue.__version=E.version,a.memory.textures++),he){Z.__webglFramebuffer=[];for(let Ae=0;Ae<6;Ae++)if(E.mipmaps&&E.mipmaps.length>0){Z.__webglFramebuffer[Ae]=[];for(let Le=0;Le<E.mipmaps.length;Le++)Z.__webglFramebuffer[Ae][Le]=r.createFramebuffer()}else Z.__webglFramebuffer[Ae]=r.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){Z.__webglFramebuffer=[];for(let Ae=0;Ae<E.mipmaps.length;Ae++)Z.__webglFramebuffer[Ae]=r.createFramebuffer()}else Z.__webglFramebuffer=r.createFramebuffer();if(Oe)for(let Ae=0,Le=fe.length;Ae<Le;Ae++){const ht=n.get(fe[Ae]);ht.__webglTexture===void 0&&(ht.__webglTexture=r.createTexture(),a.memory.textures++)}if(N.samples>0&&mt(N)===!1){Z.__webglMultisampledFramebuffer=r.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let Ae=0;Ae<fe.length;Ae++){const Le=fe[Ae];Z.__webglColorRenderbuffer[Ae]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,Z.__webglColorRenderbuffer[Ae]);const ht=s.convert(Le.format,Le.colorSpace),me=s.convert(Le.type),De=w(Le.internalFormat,ht,me,Le.colorSpace,N.isXRRenderTarget===!0),Be=ut(N);r.renderbufferStorageMultisample(r.RENDERBUFFER,Be,De,N.width,N.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Ae,r.RENDERBUFFER,Z.__webglColorRenderbuffer[Ae])}r.bindRenderbuffer(r.RENDERBUFFER,null),N.depthBuffer&&(Z.__webglDepthRenderbuffer=r.createRenderbuffer(),Se(Z.__webglDepthRenderbuffer,N,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(he){t.bindTexture(r.TEXTURE_CUBE_MAP,ue.__webglTexture),Je(r.TEXTURE_CUBE_MAP,E);for(let Ae=0;Ae<6;Ae++)if(E.mipmaps&&E.mipmaps.length>0)for(let Le=0;Le<E.mipmaps.length;Le++)Fe(Z.__webglFramebuffer[Ae][Le],N,E,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Ae,Le);else Fe(Z.__webglFramebuffer[Ae],N,E,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Ae,0);v(E)&&_(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Oe){for(let Ae=0,Le=fe.length;Ae<Le;Ae++){const ht=fe[Ae],me=n.get(ht);t.bindTexture(r.TEXTURE_2D,me.__webglTexture),Je(r.TEXTURE_2D,ht),Fe(Z.__webglFramebuffer,N,ht,r.COLOR_ATTACHMENT0+Ae,r.TEXTURE_2D,0),v(ht)&&_(r.TEXTURE_2D)}t.unbindTexture()}else{let Ae=r.TEXTURE_2D;if((N.isWebGL3DRenderTarget||N.isWebGLArrayRenderTarget)&&(Ae=N.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(Ae,ue.__webglTexture),Je(Ae,E),E.mipmaps&&E.mipmaps.length>0)for(let Le=0;Le<E.mipmaps.length;Le++)Fe(Z.__webglFramebuffer[Le],N,E,r.COLOR_ATTACHMENT0,Ae,Le);else Fe(Z.__webglFramebuffer,N,E,r.COLOR_ATTACHMENT0,Ae,0);v(E)&&_(Ae),t.unbindTexture()}N.depthBuffer&&it(N)}function lt(N){const E=N.textures;for(let Z=0,ue=E.length;Z<ue;Z++){const fe=E[Z];if(v(fe)){const he=A(N),Oe=n.get(fe).__webglTexture;t.bindTexture(he,Oe),_(he),t.unbindTexture()}}}const zt=[],X=[];function rn(N){if(N.samples>0){if(mt(N)===!1){const E=N.textures,Z=N.width,ue=N.height;let fe=r.COLOR_BUFFER_BIT;const he=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Oe=n.get(N),Ae=E.length>1;if(Ae)for(let Le=0;Le<E.length;Le++)t.bindFramebuffer(r.FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Le,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,Oe.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Le,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Oe.__webglFramebuffer);for(let Le=0;Le<E.length;Le++){if(N.resolveDepthBuffer&&(N.depthBuffer&&(fe|=r.DEPTH_BUFFER_BIT),N.stencilBuffer&&N.resolveStencilBuffer&&(fe|=r.STENCIL_BUFFER_BIT)),Ae){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,Oe.__webglColorRenderbuffer[Le]);const ht=n.get(E[Le]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,ht,0)}r.blitFramebuffer(0,0,Z,ue,0,0,Z,ue,fe,r.NEAREST),u===!0&&(zt.length=0,X.length=0,zt.push(r.COLOR_ATTACHMENT0+Le),N.depthBuffer&&N.resolveDepthBuffer===!1&&(zt.push(he),X.push(he),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,X)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,zt))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),Ae)for(let Le=0;Le<E.length;Le++){t.bindFramebuffer(r.FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Le,r.RENDERBUFFER,Oe.__webglColorRenderbuffer[Le]);const ht=n.get(E[Le]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,Oe.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Le,r.TEXTURE_2D,ht,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Oe.__webglMultisampledFramebuffer)}else if(N.depthBuffer&&N.resolveDepthBuffer===!1&&u){const E=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[E])}}}function ut(N){return Math.min(i.maxSamples,N.samples)}function mt(N){const E=n.get(N);return N.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function We(N){const E=a.render.frame;f.get(N)!==E&&(f.set(N,E),N.update())}function Tt(N,E){const Z=N.colorSpace,ue=N.format,fe=N.type;return N.isCompressedTexture===!0||N.isVideoTexture===!0||Z!==Hn&&Z!==vr&&(wt.getTransfer(Z)===Ht?(ue!==li||fe!==Qi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Z)),E}function ke(N){return typeof HTMLImageElement<"u"&&N instanceof HTMLImageElement?(h.width=N.naturalWidth||N.width,h.height=N.naturalHeight||N.height):typeof VideoFrame<"u"&&N instanceof VideoFrame?(h.width=N.displayWidth,h.height=N.displayHeight):(h.width=N.width,h.height=N.height),h}this.allocateTextureUnit=Q,this.resetTextureUnits=ee,this.setTexture2D=ce,this.setTexture2DArray=J,this.setTexture3D=de,this.setTextureCube=re,this.rebindTextures=at,this.setupRenderTarget=Pt,this.updateRenderTargetMipmap=lt,this.updateMultisampleRenderTarget=rn,this.setupDepthRenderbuffer=it,this.setupFrameBufferTexture=Fe,this.useMultisampledRTT=mt}function gR(r,e){function t(n,i=vr){let s;const a=wt.getTransfer(i);if(n===Qi)return r.UNSIGNED_BYTE;if(n===ud)return r.UNSIGNED_SHORT_4_4_4_4;if(n===hd)return r.UNSIGNED_SHORT_5_5_5_1;if(n===_g)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===mg)return r.BYTE;if(n===gg)return r.SHORT;if(n===Jo)return r.UNSIGNED_SHORT;if(n===ld)return r.INT;if(n===ss)return r.UNSIGNED_INT;if(n===vi)return r.FLOAT;if(n===na)return r.HALF_FLOAT;if(n===vg)return r.ALPHA;if(n===yg)return r.RGB;if(n===li)return r.RGBA;if(n===xg)return r.LUMINANCE;if(n===bg)return r.LUMINANCE_ALPHA;if(n===qs)return r.DEPTH_COMPONENT;if(n===to)return r.DEPTH_STENCIL;if(n===dd)return r.RED;if(n===fd)return r.RED_INTEGER;if(n===Sg)return r.RG;if(n===pd)return r.RG_INTEGER;if(n===md)return r.RGBA_INTEGER;if(n===Tc||n===Ec||n===Ac||n===wc)if(a===Ht)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===Tc)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Ec)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===wc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===Tc)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Ec)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===wc)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===wh||n===Ph||n===Rh||n===Ch)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===wh)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ph)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Rh)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Ch)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Ih||n===Lh||n===Dh)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Ih||n===Lh)return a===Ht?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Dh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Nh||n===Oh||n===Uh||n===Fh||n===Bh||n===kh||n===zh||n===Hh||n===Vh||n===Gh||n===Wh||n===jh||n===Xh||n===qh)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Nh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Oh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Uh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Fh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Bh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===kh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===zh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Hh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Vh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Gh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Wh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===jh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Xh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===qh)return a===Ht?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Pc||n===Yh||n===Kh)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===Pc)return a===Ht?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Yh)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Kh)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Mg||n===$h||n===Zh||n===Jh)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===Pc)return s.COMPRESSED_RED_RGTC1_EXT;if(n===$h)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Zh)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Jh)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===eo?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class _R extends kn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class $i extends Jt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const vR={type:"move"};class $u{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new $i,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new $i,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new F,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new F),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new $i,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new F,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new F),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,a=null;const c=this._targetRay,u=this._grip,h=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(h&&e.hand){a=!0;for(const M of e.hand.values()){const v=t.getJointPose(M,n),_=this._getHandJoint(h,M);v!==null&&(_.matrix.fromArray(v.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=v.radius),_.visible=v!==null}const f=h.joints["index-finger-tip"],p=h.joints["thumb-tip"],m=f.position.distanceTo(p.position),g=.02,x=.005;h.inputState.pinching&&m>g+x?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!h.inputState.pinching&&m<=g-x&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else u!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(u.matrix.fromArray(s.transform.matrix),u.matrix.decompose(u.position,u.rotation,u.scale),u.matrixWorldNeedsUpdate=!0,s.linearVelocity?(u.hasLinearVelocity=!0,u.linearVelocity.copy(s.linearVelocity)):u.hasLinearVelocity=!1,s.angularVelocity?(u.hasAngularVelocity=!0,u.angularVelocity.copy(s.angularVelocity)):u.hasAngularVelocity=!1));c!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(c.matrix.fromArray(i.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,i.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(i.linearVelocity)):c.hasLinearVelocity=!1,i.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(i.angularVelocity)):c.hasAngularVelocity=!1,this.dispatchEvent(vR)))}return c!==null&&(c.visible=i!==null),u!==null&&(u.visible=s!==null),h!==null&&(h.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new $i;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const yR=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,xR=`
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

}`;class bR{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new Sn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Mr({vertexShader:yR,fragmentShader:xR,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Ee(new ao(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class SR extends Tr{constructor(e,t){super();const n=this;let i=null,s=1,a=null,c="local-floor",u=1,h=null,f=null,p=null,m=null,g=null,x=null;const M=new bR,v=t.getContextAttributes();let _=null,A=null;const w=[],b=[],B=new tt;let U=null;const O=new kn;O.viewport=new Dt;const H=new kn;H.viewport=new Dt;const L=[O,H],P=new _R;let V=null,ee=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(le){let pe=w[le];return pe===void 0&&(pe=new $u,w[le]=pe),pe.getTargetRaySpace()},this.getControllerGrip=function(le){let pe=w[le];return pe===void 0&&(pe=new $u,w[le]=pe),pe.getGripSpace()},this.getHand=function(le){let pe=w[le];return pe===void 0&&(pe=new $u,w[le]=pe),pe.getHandSpace()};function Q(le){const pe=b.indexOf(le.inputSource);if(pe===-1)return;const Fe=w[pe];Fe!==void 0&&(Fe.update(le.inputSource,le.frame,h||a),Fe.dispatchEvent({type:le.type,data:le.inputSource}))}function ae(){i.removeEventListener("select",Q),i.removeEventListener("selectstart",Q),i.removeEventListener("selectend",Q),i.removeEventListener("squeeze",Q),i.removeEventListener("squeezestart",Q),i.removeEventListener("squeezeend",Q),i.removeEventListener("end",ae),i.removeEventListener("inputsourceschange",ce);for(let le=0;le<w.length;le++){const pe=b[le];pe!==null&&(b[le]=null,w[le].disconnect(pe))}V=null,ee=null,M.reset(),e.setRenderTarget(_),g=null,m=null,p=null,i=null,A=null,pt.stop(),n.isPresenting=!1,e.setPixelRatio(U),e.setSize(B.width,B.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(le){s=le,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(le){c=le,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||a},this.setReferenceSpace=function(le){h=le},this.getBaseLayer=function(){return m!==null?m:g},this.getBinding=function(){return p},this.getFrame=function(){return x},this.getSession=function(){return i},this.setSession=async function(le){if(i=le,i!==null){if(_=e.getRenderTarget(),i.addEventListener("select",Q),i.addEventListener("selectstart",Q),i.addEventListener("selectend",Q),i.addEventListener("squeeze",Q),i.addEventListener("squeezestart",Q),i.addEventListener("squeezeend",Q),i.addEventListener("end",ae),i.addEventListener("inputsourceschange",ce),v.xrCompatible!==!0&&await t.makeXRCompatible(),U=e.getPixelRatio(),e.getSize(B),i.renderState.layers===void 0){const pe={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};g=new XRWebGLLayer(i,t,pe),i.updateRenderState({baseLayer:g}),e.setPixelRatio(1),e.setSize(g.framebufferWidth,g.framebufferHeight,!1),A=new os(g.framebufferWidth,g.framebufferHeight,{format:li,type:Qi,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil})}else{let pe=null,Fe=null,Se=null;v.depth&&(Se=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,pe=v.stencil?to:qs,Fe=v.stencil?eo:ss);const qe={colorFormat:t.RGBA8,depthFormat:Se,scaleFactor:s};p=new XRWebGLBinding(i,t),m=p.createProjectionLayer(qe),i.updateRenderState({layers:[m]}),e.setPixelRatio(1),e.setSize(m.textureWidth,m.textureHeight,!1),A=new os(m.textureWidth,m.textureHeight,{format:li,type:Qi,depthTexture:new Bg(m.textureWidth,m.textureHeight,Fe,void 0,void 0,void 0,void 0,void 0,void 0,pe),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:m.ignoreDepthValues===!1})}A.isXRRenderTarget=!0,this.setFoveation(u),h=null,a=await i.requestReferenceSpace(c),pt.setContext(i),pt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return M.getDepthTexture()};function ce(le){for(let pe=0;pe<le.removed.length;pe++){const Fe=le.removed[pe],Se=b.indexOf(Fe);Se>=0&&(b[Se]=null,w[Se].disconnect(Fe))}for(let pe=0;pe<le.added.length;pe++){const Fe=le.added[pe];let Se=b.indexOf(Fe);if(Se===-1){for(let it=0;it<w.length;it++)if(it>=b.length){b.push(Fe),Se=it;break}else if(b[it]===null){b[it]=Fe,Se=it;break}if(Se===-1)break}const qe=w[Se];qe&&qe.connect(Fe)}}const J=new F,de=new F;function re(le,pe,Fe){J.setFromMatrixPosition(pe.matrixWorld),de.setFromMatrixPosition(Fe.matrixWorld);const Se=J.distanceTo(de),qe=pe.projectionMatrix.elements,it=Fe.projectionMatrix.elements,at=qe[14]/(qe[10]-1),Pt=qe[14]/(qe[10]+1),lt=(qe[9]+1)/qe[5],zt=(qe[9]-1)/qe[5],X=(qe[8]-1)/qe[0],rn=(it[8]+1)/it[0],ut=at*X,mt=at*rn,We=Se/(-X+rn),Tt=We*-X;if(pe.matrixWorld.decompose(le.position,le.quaternion,le.scale),le.translateX(Tt),le.translateZ(We),le.matrixWorld.compose(le.position,le.quaternion,le.scale),le.matrixWorldInverse.copy(le.matrixWorld).invert(),qe[10]===-1)le.projectionMatrix.copy(pe.projectionMatrix),le.projectionMatrixInverse.copy(pe.projectionMatrixInverse);else{const ke=at+We,N=Pt+We,E=ut-Tt,Z=mt+(Se-Tt),ue=lt*Pt/N*ke,fe=zt*Pt/N*ke;le.projectionMatrix.makePerspective(E,Z,ue,fe,ke,N),le.projectionMatrixInverse.copy(le.projectionMatrix).invert()}}function _e(le,pe){pe===null?le.matrixWorld.copy(le.matrix):le.matrixWorld.multiplyMatrices(pe.matrixWorld,le.matrix),le.matrixWorldInverse.copy(le.matrixWorld).invert()}this.updateCamera=function(le){if(i===null)return;let pe=le.near,Fe=le.far;M.texture!==null&&(M.depthNear>0&&(pe=M.depthNear),M.depthFar>0&&(Fe=M.depthFar)),P.near=H.near=O.near=pe,P.far=H.far=O.far=Fe,(V!==P.near||ee!==P.far)&&(i.updateRenderState({depthNear:P.near,depthFar:P.far}),V=P.near,ee=P.far),O.layers.mask=le.layers.mask|2,H.layers.mask=le.layers.mask|4,P.layers.mask=O.layers.mask|H.layers.mask;const Se=le.parent,qe=P.cameras;_e(P,Se);for(let it=0;it<qe.length;it++)_e(qe[it],Se);qe.length===2?re(P,O,H):P.projectionMatrix.copy(O.projectionMatrix),Me(le,P,Se)};function Me(le,pe,Fe){Fe===null?le.matrix.copy(pe.matrixWorld):(le.matrix.copy(Fe.matrixWorld),le.matrix.invert(),le.matrix.multiply(pe.matrixWorld)),le.matrix.decompose(le.position,le.quaternion,le.scale),le.updateMatrixWorld(!0),le.projectionMatrix.copy(pe.projectionMatrix),le.projectionMatrixInverse.copy(pe.projectionMatrixInverse),le.isPerspectiveCamera&&(le.fov=no*2*Math.atan(1/le.projectionMatrix.elements[5]),le.zoom=1)}this.getCamera=function(){return P},this.getFoveation=function(){if(!(m===null&&g===null))return u},this.setFoveation=function(le){u=le,m!==null&&(m.fixedFoveation=le),g!==null&&g.fixedFoveation!==void 0&&(g.fixedFoveation=le)},this.hasDepthSensing=function(){return M.texture!==null},this.getDepthSensingMesh=function(){return M.getMesh(P)};let Ue=null;function Je(le,pe){if(f=pe.getViewerPose(h||a),x=pe,f!==null){const Fe=f.views;g!==null&&(e.setRenderTargetFramebuffer(A,g.framebuffer),e.setRenderTarget(A));let Se=!1;Fe.length!==P.cameras.length&&(P.cameras.length=0,Se=!0);for(let it=0;it<Fe.length;it++){const at=Fe[it];let Pt=null;if(g!==null)Pt=g.getViewport(at);else{const zt=p.getViewSubImage(m,at);Pt=zt.viewport,it===0&&(e.setRenderTargetTextures(A,zt.colorTexture,m.ignoreDepthValues?void 0:zt.depthStencilTexture),e.setRenderTarget(A))}let lt=L[it];lt===void 0&&(lt=new kn,lt.layers.enable(it),lt.viewport=new Dt,L[it]=lt),lt.matrix.fromArray(at.transform.matrix),lt.matrix.decompose(lt.position,lt.quaternion,lt.scale),lt.projectionMatrix.fromArray(at.projectionMatrix),lt.projectionMatrixInverse.copy(lt.projectionMatrix).invert(),lt.viewport.set(Pt.x,Pt.y,Pt.width,Pt.height),it===0&&(P.matrix.copy(lt.matrix),P.matrix.decompose(P.position,P.quaternion,P.scale)),Se===!0&&P.cameras.push(lt)}const qe=i.enabledFeatures;if(qe&&qe.includes("depth-sensing")){const it=p.getDepthInformation(Fe[0]);it&&it.isValid&&it.texture&&M.init(e,it,i.renderState)}}for(let Fe=0;Fe<w.length;Fe++){const Se=b[Fe],qe=w[Fe];Se!==null&&qe!==void 0&&qe.update(Se,pe,h||a)}Ue&&Ue(le,pe),pe.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:pe}),x=null}const pt=new Fg;pt.setAnimationLoop(Je),this.setAnimationLoop=function(le){Ue=le},this.dispose=function(){}}}const Zr=new xi,MR=new ot;function TR(r,e){function t(v,_){v.matrixAutoUpdate===!0&&v.updateMatrix(),_.value.copy(v.matrix)}function n(v,_){_.color.getRGB(v.fogColor.value,Ng(r)),_.isFog?(v.fogNear.value=_.near,v.fogFar.value=_.far):_.isFogExp2&&(v.fogDensity.value=_.density)}function i(v,_,A,w,b){_.isMeshBasicMaterial||_.isMeshLambertMaterial?s(v,_):_.isMeshToonMaterial?(s(v,_),p(v,_)):_.isMeshPhongMaterial?(s(v,_),f(v,_)):_.isMeshStandardMaterial?(s(v,_),m(v,_),_.isMeshPhysicalMaterial&&g(v,_,b)):_.isMeshMatcapMaterial?(s(v,_),x(v,_)):_.isMeshDepthMaterial?s(v,_):_.isMeshDistanceMaterial?(s(v,_),M(v,_)):_.isMeshNormalMaterial?s(v,_):_.isLineBasicMaterial?(a(v,_),_.isLineDashedMaterial&&c(v,_)):_.isPointsMaterial?u(v,_,A,w):_.isSpriteMaterial?h(v,_):_.isShadowMaterial?(v.color.value.copy(_.color),v.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function s(v,_){v.opacity.value=_.opacity,_.color&&v.diffuse.value.copy(_.color),_.emissive&&v.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.bumpMap&&(v.bumpMap.value=_.bumpMap,t(_.bumpMap,v.bumpMapTransform),v.bumpScale.value=_.bumpScale,_.side===qn&&(v.bumpScale.value*=-1)),_.normalMap&&(v.normalMap.value=_.normalMap,t(_.normalMap,v.normalMapTransform),v.normalScale.value.copy(_.normalScale),_.side===qn&&v.normalScale.value.negate()),_.displacementMap&&(v.displacementMap.value=_.displacementMap,t(_.displacementMap,v.displacementMapTransform),v.displacementScale.value=_.displacementScale,v.displacementBias.value=_.displacementBias),_.emissiveMap&&(v.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,v.emissiveMapTransform)),_.specularMap&&(v.specularMap.value=_.specularMap,t(_.specularMap,v.specularMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest);const A=e.get(_),w=A.envMap,b=A.envMapRotation;w&&(v.envMap.value=w,Zr.copy(b),Zr.x*=-1,Zr.y*=-1,Zr.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(Zr.y*=-1,Zr.z*=-1),v.envMapRotation.value.setFromMatrix4(MR.makeRotationFromEuler(Zr)),v.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,v.reflectivity.value=_.reflectivity,v.ior.value=_.ior,v.refractionRatio.value=_.refractionRatio),_.lightMap&&(v.lightMap.value=_.lightMap,v.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,v.lightMapTransform)),_.aoMap&&(v.aoMap.value=_.aoMap,v.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,v.aoMapTransform))}function a(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform))}function c(v,_){v.dashSize.value=_.dashSize,v.totalSize.value=_.dashSize+_.gapSize,v.scale.value=_.scale}function u(v,_,A,w){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.size.value=_.size*A,v.scale.value=w*.5,_.map&&(v.map.value=_.map,t(_.map,v.uvTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function h(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.rotation.value=_.rotation,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function f(v,_){v.specular.value.copy(_.specular),v.shininess.value=Math.max(_.shininess,1e-4)}function p(v,_){_.gradientMap&&(v.gradientMap.value=_.gradientMap)}function m(v,_){v.metalness.value=_.metalness,_.metalnessMap&&(v.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,v.metalnessMapTransform)),v.roughness.value=_.roughness,_.roughnessMap&&(v.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,v.roughnessMapTransform)),_.envMap&&(v.envMapIntensity.value=_.envMapIntensity)}function g(v,_,A){v.ior.value=_.ior,_.sheen>0&&(v.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),v.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(v.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,v.sheenColorMapTransform)),_.sheenRoughnessMap&&(v.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,v.sheenRoughnessMapTransform))),_.clearcoat>0&&(v.clearcoat.value=_.clearcoat,v.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(v.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,v.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(v.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===qn&&v.clearcoatNormalScale.value.negate())),_.dispersion>0&&(v.dispersion.value=_.dispersion),_.iridescence>0&&(v.iridescence.value=_.iridescence,v.iridescenceIOR.value=_.iridescenceIOR,v.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(v.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,v.iridescenceMapTransform)),_.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),_.transmission>0&&(v.transmission.value=_.transmission,v.transmissionSamplerMap.value=A.texture,v.transmissionSamplerSize.value.set(A.width,A.height),_.transmissionMap&&(v.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,v.transmissionMapTransform)),v.thickness.value=_.thickness,_.thicknessMap&&(v.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=_.attenuationDistance,v.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(v.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(v.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=_.specularIntensity,v.specularColor.value.copy(_.specularColor),_.specularColorMap&&(v.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,v.specularColorMapTransform)),_.specularIntensityMap&&(v.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,v.specularIntensityMapTransform))}function x(v,_){_.matcap&&(v.matcap.value=_.matcap)}function M(v,_){const A=e.get(_).light;v.referencePosition.value.setFromMatrixPosition(A.matrixWorld),v.nearDistance.value=A.shadow.camera.near,v.farDistance.value=A.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function ER(r,e,t,n){let i={},s={},a=[];const c=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function u(A,w){const b=w.program;n.uniformBlockBinding(A,b)}function h(A,w){let b=i[A.id];b===void 0&&(x(A),b=f(A),i[A.id]=b,A.addEventListener("dispose",v));const B=w.program;n.updateUBOMapping(A,B);const U=e.render.frame;s[A.id]!==U&&(m(A),s[A.id]=U)}function f(A){const w=p();A.__bindingPointIndex=w;const b=r.createBuffer(),B=A.__size,U=A.usage;return r.bindBuffer(r.UNIFORM_BUFFER,b),r.bufferData(r.UNIFORM_BUFFER,B,U),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,w,b),b}function p(){for(let A=0;A<c;A++)if(a.indexOf(A)===-1)return a.push(A),A;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function m(A){const w=i[A.id],b=A.uniforms,B=A.__cache;r.bindBuffer(r.UNIFORM_BUFFER,w);for(let U=0,O=b.length;U<O;U++){const H=Array.isArray(b[U])?b[U]:[b[U]];for(let L=0,P=H.length;L<P;L++){const V=H[L];if(g(V,U,L,B)===!0){const ee=V.__offset,Q=Array.isArray(V.value)?V.value:[V.value];let ae=0;for(let ce=0;ce<Q.length;ce++){const J=Q[ce],de=M(J);typeof J=="number"||typeof J=="boolean"?(V.__data[0]=J,r.bufferSubData(r.UNIFORM_BUFFER,ee+ae,V.__data)):J.isMatrix3?(V.__data[0]=J.elements[0],V.__data[1]=J.elements[1],V.__data[2]=J.elements[2],V.__data[3]=0,V.__data[4]=J.elements[3],V.__data[5]=J.elements[4],V.__data[6]=J.elements[5],V.__data[7]=0,V.__data[8]=J.elements[6],V.__data[9]=J.elements[7],V.__data[10]=J.elements[8],V.__data[11]=0):(J.toArray(V.__data,ae),ae+=de.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,ee,V.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function g(A,w,b,B){const U=A.value,O=w+"_"+b;if(B[O]===void 0)return typeof U=="number"||typeof U=="boolean"?B[O]=U:B[O]=U.clone(),!0;{const H=B[O];if(typeof U=="number"||typeof U=="boolean"){if(H!==U)return B[O]=U,!0}else if(H.equals(U)===!1)return H.copy(U),!0}return!1}function x(A){const w=A.uniforms;let b=0;const B=16;for(let O=0,H=w.length;O<H;O++){const L=Array.isArray(w[O])?w[O]:[w[O]];for(let P=0,V=L.length;P<V;P++){const ee=L[P],Q=Array.isArray(ee.value)?ee.value:[ee.value];for(let ae=0,ce=Q.length;ae<ce;ae++){const J=Q[ae],de=M(J),re=b%B,_e=re%de.boundary,Me=re+_e;b+=_e,Me!==0&&B-Me<de.storage&&(b+=B-Me),ee.__data=new Float32Array(de.storage/Float32Array.BYTES_PER_ELEMENT),ee.__offset=b,b+=de.storage}}}const U=b%B;return U>0&&(b+=B-U),A.__size=b,A.__cache={},this}function M(A){const w={boundary:0,storage:0};return typeof A=="number"||typeof A=="boolean"?(w.boundary=4,w.storage=4):A.isVector2?(w.boundary=8,w.storage=8):A.isVector3||A.isColor?(w.boundary=16,w.storage=12):A.isVector4?(w.boundary=16,w.storage=16):A.isMatrix3?(w.boundary=48,w.storage=48):A.isMatrix4?(w.boundary=64,w.storage=64):A.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",A),w}function v(A){const w=A.target;w.removeEventListener("dispose",v);const b=a.indexOf(w.__bindingPointIndex);a.splice(b,1),r.deleteBuffer(i[w.id]),delete i[w.id],delete s[w.id]}function _(){for(const A in i)r.deleteBuffer(i[A]);a=[],i={},s={}}return{bind:u,update:h,dispose:_}}class AR{constructor(e={}){const{canvas:t=pE(),context:n=null,depth:i=!0,stencil:s=!1,alpha:a=!1,antialias:c=!1,premultipliedAlpha:u=!0,preserveDrawingBuffer:h=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:p=!1,reverseDepthBuffer:m=!1}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");g=n.getContextAttributes().alpha}else g=a;const x=new Uint32Array(4),M=new Int32Array(4);let v=null,_=null;const A=[],w=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=bn,this.toneMapping=Sr,this.toneMappingExposure=1;const b=this;let B=!1,U=0,O=0,H=null,L=-1,P=null;const V=new Dt,ee=new Dt;let Q=null;const ae=new $e(0);let ce=0,J=t.width,de=t.height,re=1,_e=null,Me=null;const Ue=new Dt(0,0,J,de),Je=new Dt(0,0,J,de);let pt=!1;const le=new xd;let pe=!1,Fe=!1;const Se=new ot,qe=new ot,it=new F,at=new Dt,Pt={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let lt=!1;function zt(){return H===null?re:1}let X=n;function rn(C,j){return t.getContext(C,j)}try{const C={alpha:!0,depth:i,stencil:s,antialias:c,premultipliedAlpha:u,preserveDrawingBuffer:h,powerPreference:f,failIfMajorPerformanceCaveat:p};if("setAttribute"in t&&t.setAttribute("data-engine","three.js r170"),t.addEventListener("webglcontextlost",z,!1),t.addEventListener("webglcontextrestored",K,!1),t.addEventListener("webglcontextcreationerror",ie,!1),X===null){const j="webgl2";if(X=rn(j,C),X===null)throw rn(j)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(C){throw console.error("THREE.WebGLRenderer: "+C.message),C}let ut,mt,We,Tt,ke,N,E,Z,ue,fe,he,Oe,Ae,Le,ht,me,De,Be,Ze,Ne,_t,st,Ct,W;function Te(){ut=new I1(X),ut.init(),st=new gR(X,ut),mt=new E1(X,ut,e,st),We=new fR(X,ut),mt.reverseDepthBuffer&&m&&We.buffers.depth.setReversed(!0),Tt=new N1(X),ke=new JP,N=new mR(X,ut,We,ke,mt,st,Tt),E=new w1(b),Z=new C1(b),ue=new HE(X),Ct=new M1(X,ue),fe=new L1(X,ue,Tt,Ct),he=new U1(X,fe,ue,Tt),Ze=new O1(X,mt,N),me=new A1(ke),Oe=new ZP(b,E,Z,ut,mt,Ct,me),Ae=new TR(b,ke),Le=new eR,ht=new oR(ut),Be=new S1(b,E,Z,We,he,g,u),De=new hR(b,he,mt),W=new ER(X,Tt,mt,We),Ne=new T1(X,ut,Tt),_t=new D1(X,ut,Tt),Tt.programs=Oe.programs,b.capabilities=mt,b.extensions=ut,b.properties=ke,b.renderLists=Le,b.shadowMap=De,b.state=We,b.info=Tt}Te();const R=new SR(b,X);this.xr=R,this.getContext=function(){return X},this.getContextAttributes=function(){return X.getContextAttributes()},this.forceContextLoss=function(){const C=ut.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){const C=ut.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return re},this.setPixelRatio=function(C){C!==void 0&&(re=C,this.setSize(J,de,!1))},this.getSize=function(C){return C.set(J,de)},this.setSize=function(C,j,te=!0){if(R.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}J=C,de=j,t.width=Math.floor(C*re),t.height=Math.floor(j*re),te===!0&&(t.style.width=C+"px",t.style.height=j+"px"),this.setViewport(0,0,C,j)},this.getDrawingBufferSize=function(C){return C.set(J*re,de*re).floor()},this.setDrawingBufferSize=function(C,j,te){J=C,de=j,re=te,t.width=Math.floor(C*te),t.height=Math.floor(j*te),this.setViewport(0,0,C,j)},this.getCurrentViewport=function(C){return C.copy(V)},this.getViewport=function(C){return C.copy(Ue)},this.setViewport=function(C,j,te,ne){C.isVector4?Ue.set(C.x,C.y,C.z,C.w):Ue.set(C,j,te,ne),We.viewport(V.copy(Ue).multiplyScalar(re).round())},this.getScissor=function(C){return C.copy(Je)},this.setScissor=function(C,j,te,ne){C.isVector4?Je.set(C.x,C.y,C.z,C.w):Je.set(C,j,te,ne),We.scissor(ee.copy(Je).multiplyScalar(re).round())},this.getScissorTest=function(){return pt},this.setScissorTest=function(C){We.setScissorTest(pt=C)},this.setOpaqueSort=function(C){_e=C},this.setTransparentSort=function(C){Me=C},this.getClearColor=function(C){return C.copy(Be.getClearColor())},this.setClearColor=function(){Be.setClearColor.apply(Be,arguments)},this.getClearAlpha=function(){return Be.getClearAlpha()},this.setClearAlpha=function(){Be.setClearAlpha.apply(Be,arguments)},this.clear=function(C=!0,j=!0,te=!0){let ne=0;if(C){let q=!1;if(H!==null){const be=H.texture.format;q=be===md||be===pd||be===fd}if(q){const be=H.texture.type,Ce=be===Qi||be===ss||be===Jo||be===eo||be===ud||be===hd,He=Be.getClearColor(),Ve=Be.getClearAlpha(),rt=He.r,Qe=He.g,Ge=He.b;Ce?(x[0]=rt,x[1]=Qe,x[2]=Ge,x[3]=Ve,X.clearBufferuiv(X.COLOR,0,x)):(M[0]=rt,M[1]=Qe,M[2]=Ge,M[3]=Ve,X.clearBufferiv(X.COLOR,0,M))}else ne|=X.COLOR_BUFFER_BIT}j&&(ne|=X.DEPTH_BUFFER_BIT),te&&(ne|=X.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),X.clear(ne)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",z,!1),t.removeEventListener("webglcontextrestored",K,!1),t.removeEventListener("webglcontextcreationerror",ie,!1),Le.dispose(),ht.dispose(),ke.dispose(),E.dispose(),Z.dispose(),he.dispose(),Ct.dispose(),W.dispose(),Oe.dispose(),R.dispose(),R.removeEventListener("sessionstart",qt),R.removeEventListener("sessionend",Ke),ct.stop()};function z(C){C.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),B=!0}function K(){console.log("THREE.WebGLRenderer: Context Restored."),B=!1;const C=Tt.autoReset,j=De.enabled,te=De.autoUpdate,ne=De.needsUpdate,q=De.type;Te(),Tt.autoReset=C,De.enabled=j,De.autoUpdate=te,De.needsUpdate=ne,De.type=q}function ie(C){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}function ye(C){const j=C.target;j.removeEventListener("dispose",ye),xe(j)}function xe(C){we(C),ke.remove(C)}function we(C){const j=ke.get(C).programs;j!==void 0&&(j.forEach(function(te){Oe.releaseProgram(te)}),C.isShaderMaterial&&Oe.releaseShaderCache(C))}this.renderBufferDirect=function(C,j,te,ne,q,be){j===null&&(j=Pt);const Ce=q.isMesh&&q.matrixWorld.determinant()<0,He=ho(C,j,te,ne,q);We.setMaterial(ne,Ce);let Ve=te.index,rt=1;if(ne.wireframe===!0){if(Ve=fe.getWireframeAttribute(te),Ve===void 0)return;rt=2}const Qe=te.drawRange,Ge=te.attributes.position;let Mt=Qe.start*rt,Nt=(Qe.start+Qe.count)*rt;be!==null&&(Mt=Math.max(Mt,be.start*rt),Nt=Math.min(Nt,(be.start+be.count)*rt)),Ve!==null?(Mt=Math.max(Mt,0),Nt=Math.min(Nt,Ve.count)):Ge!=null&&(Mt=Math.max(Mt,0),Nt=Math.min(Nt,Ge.count));const Ut=Nt-Mt;if(Ut<0||Ut===1/0)return;Ct.setup(q,ne,He,te,Ve);let nn,At=Ne;if(Ve!==null&&(nn=ue.get(Ve),At=_t,At.setIndex(nn)),q.isMesh)ne.wireframe===!0?(We.setLineWidth(ne.wireframeLinewidth*zt()),At.setMode(X.LINES)):At.setMode(X.TRIANGLES);else if(q.isLine){let je=ne.linewidth;je===void 0&&(je=1),We.setLineWidth(je*zt()),q.isLineSegments?At.setMode(X.LINES):q.isLineLoop?At.setMode(X.LINE_LOOP):At.setMode(X.LINE_STRIP)}else q.isPoints?At.setMode(X.POINTS):q.isSprite&&At.setMode(X.TRIANGLES);if(q.isBatchedMesh)if(q._multiDrawInstances!==null)At.renderMultiDrawInstances(q._multiDrawStarts,q._multiDrawCounts,q._multiDrawCount,q._multiDrawInstances);else if(ut.get("WEBGL_multi_draw"))At.renderMultiDraw(q._multiDrawStarts,q._multiDrawCounts,q._multiDrawCount);else{const je=q._multiDrawStarts,Yn=q._multiDrawCounts,bt=q._multiDrawCount,Mn=Ve?ue.get(Ve).bytesPerElement:1,bi=ke.get(ne).currentProgram.getUniforms();for(let cn=0;cn<bt;cn++)bi.setValue(X,"_gl_DrawID",cn),At.render(je[cn]/Mn,Yn[cn])}else if(q.isInstancedMesh)At.renderInstances(Mt,Ut,q.count);else if(te.isInstancedBufferGeometry){const je=te._maxInstanceCount!==void 0?te._maxInstanceCount:1/0,Yn=Math.min(te.instanceCount,je);At.renderInstances(Mt,Ut,Yn)}else At.render(Mt,Ut)};function Ie(C,j,te){C.transparent===!0&&C.side===Xn&&C.forceSinglePass===!1?(C.side=qn,C.needsUpdate=!0,tr(C,j,te),C.side=Ji,C.needsUpdate=!0,tr(C,j,te),C.side=Xn):tr(C,j,te)}this.compile=function(C,j,te=null){te===null&&(te=C),_=ht.get(te),_.init(j),w.push(_),te.traverseVisible(function(q){q.isLight&&q.layers.test(j.layers)&&(_.pushLight(q),q.castShadow&&_.pushShadow(q))}),C!==te&&C.traverseVisible(function(q){q.isLight&&q.layers.test(j.layers)&&(_.pushLight(q),q.castShadow&&_.pushShadow(q))}),_.setupLights();const ne=new Set;return C.traverse(function(q){if(!(q.isMesh||q.isPoints||q.isLine||q.isSprite))return;const be=q.material;if(be)if(Array.isArray(be))for(let Ce=0;Ce<be.length;Ce++){const He=be[Ce];Ie(He,te,q),ne.add(He)}else Ie(be,te,q),ne.add(be)}),w.pop(),_=null,ne},this.compileAsync=function(C,j,te=null){const ne=this.compile(C,j,te);return new Promise(q=>{function be(){if(ne.forEach(function(Ce){ke.get(Ce).currentProgram.isReady()&&ne.delete(Ce)}),ne.size===0){q(C);return}setTimeout(be,10)}ut.get("KHR_parallel_shader_compile")!==null?be():setTimeout(be,10)})};let nt=null;function Et(C){nt&&nt(C)}function qt(){ct.stop()}function Ke(){ct.start()}const ct=new Fg;ct.setAnimationLoop(Et),typeof self<"u"&&ct.setContext(self),this.setAnimationLoop=function(C){nt=C,R.setAnimationLoop(C),C===null?ct.stop():ct.start()},R.addEventListener("sessionstart",qt),R.addEventListener("sessionend",Ke),this.render=function(C,j){if(j!==void 0&&j.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(B===!0)return;if(C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),j.parent===null&&j.matrixWorldAutoUpdate===!0&&j.updateMatrixWorld(),R.enabled===!0&&R.isPresenting===!0&&(R.cameraAutoUpdate===!0&&R.updateCamera(j),j=R.getCamera()),C.isScene===!0&&C.onBeforeRender(b,C,j,H),_=ht.get(C,w.length),_.init(j),w.push(_),qe.multiplyMatrices(j.projectionMatrix,j.matrixWorldInverse),le.setFromProjectionMatrix(qe),Fe=this.localClippingEnabled,pe=me.init(this.clippingPlanes,Fe),v=Le.get(C,A.length),v.init(),A.push(v),R.enabled===!0&&R.isPresenting===!0){const be=b.xr.getDepthSensingMesh();be!==null&&Gt(be,j,-1/0,b.sortObjects)}Gt(C,j,0,b.sortObjects),v.finish(),b.sortObjects===!0&&v.sort(_e,Me),lt=R.enabled===!1||R.isPresenting===!1||R.hasDepthSensing()===!1,lt&&Be.addToRenderList(v,C),this.info.render.frame++,pe===!0&&me.beginShadows();const te=_.state.shadowsArray;De.render(te,C,j),pe===!0&&me.endShadows(),this.info.autoReset===!0&&this.info.reset();const ne=v.opaque,q=v.transmissive;if(_.setupLights(),j.isArrayCamera){const be=j.cameras;if(q.length>0)for(let Ce=0,He=be.length;Ce<He;Ce++){const Ve=be[Ce];Xe(ne,q,C,Ve)}lt&&Be.render(C);for(let Ce=0,He=be.length;Ce<He;Ce++){const Ve=be[Ce];Rt(v,C,Ve,Ve.viewport)}}else q.length>0&&Xe(ne,q,C,j),lt&&Be.render(C),Rt(v,C,j);H!==null&&(N.updateMultisampleRenderTarget(H),N.updateRenderTargetMipmap(H)),C.isScene===!0&&C.onAfterRender(b,C,j),Ct.resetDefaultState(),L=-1,P=null,w.pop(),w.length>0?(_=w[w.length-1],pe===!0&&me.setGlobalState(b.clippingPlanes,_.state.camera)):_=null,A.pop(),A.length>0?v=A[A.length-1]:v=null};function Gt(C,j,te,ne){if(C.visible===!1)return;if(C.layers.test(j.layers)){if(C.isGroup)te=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(j);else if(C.isLight)_.pushLight(C),C.castShadow&&_.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||le.intersectsSprite(C)){ne&&at.setFromMatrixPosition(C.matrixWorld).applyMatrix4(qe);const Ce=he.update(C),He=C.material;He.visible&&v.push(C,Ce,He,te,at.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(!C.frustumCulled||le.intersectsObject(C))){const Ce=he.update(C),He=C.material;if(ne&&(C.boundingSphere!==void 0?(C.boundingSphere===null&&C.computeBoundingSphere(),at.copy(C.boundingSphere.center)):(Ce.boundingSphere===null&&Ce.computeBoundingSphere(),at.copy(Ce.boundingSphere.center)),at.applyMatrix4(C.matrixWorld).applyMatrix4(qe)),Array.isArray(He)){const Ve=Ce.groups;for(let rt=0,Qe=Ve.length;rt<Qe;rt++){const Ge=Ve[rt],Mt=He[Ge.materialIndex];Mt&&Mt.visible&&v.push(C,Ce,Mt,te,at.z,Ge)}}else He.visible&&v.push(C,Ce,He,te,at.z,null)}}const be=C.children;for(let Ce=0,He=be.length;Ce<He;Ce++)Gt(be[Ce],j,te,ne)}function Rt(C,j,te,ne){const q=C.opaque,be=C.transmissive,Ce=C.transparent;_.setupLightsView(te),pe===!0&&me.setGlobalState(b.clippingPlanes,te),ne&&We.viewport(V.copy(ne)),q.length>0&&yt(q,j,te),be.length>0&&yt(be,j,te),Ce.length>0&&yt(Ce,j,te),We.buffers.depth.setTest(!0),We.buffers.depth.setMask(!0),We.buffers.color.setMask(!0),We.setPolygonOffset(!1)}function Xe(C,j,te,ne){if((te.isScene===!0?te.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[ne.id]===void 0&&(_.state.transmissionRenderTarget[ne.id]=new os(1,1,{generateMipmaps:!0,type:ut.has("EXT_color_buffer_half_float")||ut.has("EXT_color_buffer_float")?na:Qi,minFilter:Yi,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:wt.workingColorSpace}));const be=_.state.transmissionRenderTarget[ne.id],Ce=ne.viewport||V;be.setSize(Ce.z,Ce.w);const He=b.getRenderTarget();b.setRenderTarget(be),b.getClearColor(ae),ce=b.getClearAlpha(),ce<1&&b.setClearColor(16777215,.5),b.clear(),lt&&Be.render(te);const Ve=b.toneMapping;b.toneMapping=Sr;const rt=ne.viewport;if(ne.viewport!==void 0&&(ne.viewport=void 0),_.setupLightsView(ne),pe===!0&&me.setGlobalState(b.clippingPlanes,ne),yt(C,te,ne),N.updateMultisampleRenderTarget(be),N.updateRenderTargetMipmap(be),ut.has("WEBGL_multisampled_render_to_texture")===!1){let Qe=!1;for(let Ge=0,Mt=j.length;Ge<Mt;Ge++){const Nt=j[Ge],Ut=Nt.object,nn=Nt.geometry,At=Nt.material,je=Nt.group;if(At.side===Xn&&Ut.layers.test(ne.layers)){const Yn=At.side;At.side=qn,At.needsUpdate=!0,On(Ut,te,ne,nn,At,je),At.side=Yn,At.needsUpdate=!0,Qe=!0}}Qe===!0&&(N.updateMultisampleRenderTarget(be),N.updateRenderTargetMipmap(be))}b.setRenderTarget(He),b.setClearColor(ae,ce),rt!==void 0&&(ne.viewport=rt),b.toneMapping=Ve}function yt(C,j,te){const ne=j.isScene===!0?j.overrideMaterial:null;for(let q=0,be=C.length;q<be;q++){const Ce=C[q],He=Ce.object,Ve=Ce.geometry,rt=ne===null?Ce.material:ne,Qe=Ce.group;He.layers.test(te.layers)&&On(He,j,te,Ve,rt,Qe)}}function On(C,j,te,ne,q,be){C.onBeforeRender(b,j,te,ne,q,be),C.modelViewMatrix.multiplyMatrices(te.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),q.onBeforeRender(b,j,te,ne,C,be),q.transparent===!0&&q.side===Xn&&q.forceSinglePass===!1?(q.side=qn,q.needsUpdate=!0,b.renderBufferDirect(te,j,ne,q,C,be),q.side=Ji,q.needsUpdate=!0,b.renderBufferDirect(te,j,ne,q,C,be),q.side=Xn):b.renderBufferDirect(te,j,ne,q,C,be),C.onAfterRender(b,j,te,ne,q,be)}function tr(C,j,te){j.isScene!==!0&&(j=Pt);const ne=ke.get(C),q=_.state.lights,be=_.state.shadowsArray,Ce=q.state.version,He=Oe.getParameters(C,q.state,be,j,te),Ve=Oe.getProgramCacheKey(He);let rt=ne.programs;ne.environment=C.isMeshStandardMaterial?j.environment:null,ne.fog=j.fog,ne.envMap=(C.isMeshStandardMaterial?Z:E).get(C.envMap||ne.environment),ne.envMapRotation=ne.environment!==null&&C.envMap===null?j.environmentRotation:C.envMapRotation,rt===void 0&&(C.addEventListener("dispose",ye),rt=new Map,ne.programs=rt);let Qe=rt.get(Ve);if(Qe!==void 0){if(ne.currentProgram===Qe&&ne.lightsStateVersion===Ce)return ri(C,He),Qe}else He.uniforms=Oe.getUniforms(C),C.onBeforeCompile(He,b),Qe=Oe.acquireProgram(He,Ve),rt.set(Ve,Qe),ne.uniforms=He.uniforms;const Ge=ne.uniforms;return(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(Ge.clippingPlanes=me.uniform),ri(C,He),ne.needsLights=nr(C),ne.lightsStateVersion=Ce,ne.needsLights&&(Ge.ambientLightColor.value=q.state.ambient,Ge.lightProbe.value=q.state.probe,Ge.directionalLights.value=q.state.directional,Ge.directionalLightShadows.value=q.state.directionalShadow,Ge.spotLights.value=q.state.spot,Ge.spotLightShadows.value=q.state.spotShadow,Ge.rectAreaLights.value=q.state.rectArea,Ge.ltc_1.value=q.state.rectAreaLTC1,Ge.ltc_2.value=q.state.rectAreaLTC2,Ge.pointLights.value=q.state.point,Ge.pointLightShadows.value=q.state.pointShadow,Ge.hemisphereLights.value=q.state.hemi,Ge.directionalShadowMap.value=q.state.directionalShadowMap,Ge.directionalShadowMatrix.value=q.state.directionalShadowMatrix,Ge.spotShadowMap.value=q.state.spotShadowMap,Ge.spotLightMatrix.value=q.state.spotLightMatrix,Ge.spotLightMap.value=q.state.spotLightMap,Ge.pointShadowMap.value=q.state.pointShadowMap,Ge.pointShadowMatrix.value=q.state.pointShadowMatrix),ne.currentProgram=Qe,ne.uniformsList=null,Qe}function hs(C){if(C.uniformsList===null){const j=C.currentProgram.getUniforms();C.uniformsList=Rc.seqWithValue(j.seq,C.uniforms)}return C.uniformsList}function ri(C,j){const te=ke.get(C);te.outputColorSpace=j.outputColorSpace,te.batching=j.batching,te.batchingColor=j.batchingColor,te.instancing=j.instancing,te.instancingColor=j.instancingColor,te.instancingMorph=j.instancingMorph,te.skinning=j.skinning,te.morphTargets=j.morphTargets,te.morphNormals=j.morphNormals,te.morphColors=j.morphColors,te.morphTargetsCount=j.morphTargetsCount,te.numClippingPlanes=j.numClippingPlanes,te.numIntersection=j.numClipIntersection,te.vertexAlphas=j.vertexAlphas,te.vertexTangents=j.vertexTangents,te.toneMapping=j.toneMapping}function ho(C,j,te,ne,q){j.isScene!==!0&&(j=Pt),N.resetTextureUnits();const be=j.fog,Ce=ne.isMeshStandardMaterial?j.environment:null,He=H===null?b.outputColorSpace:H.isXRRenderTarget===!0?H.texture.colorSpace:Hn,Ve=(ne.isMeshStandardMaterial?Z:E).get(ne.envMap||Ce),rt=ne.vertexColors===!0&&!!te.attributes.color&&te.attributes.color.itemSize===4,Qe=!!te.attributes.tangent&&(!!ne.normalMap||ne.anisotropy>0),Ge=!!te.morphAttributes.position,Mt=!!te.morphAttributes.normal,Nt=!!te.morphAttributes.color;let Ut=Sr;ne.toneMapped&&(H===null||H.isXRRenderTarget===!0)&&(Ut=b.toneMapping);const nn=te.morphAttributes.position||te.morphAttributes.normal||te.morphAttributes.color,At=nn!==void 0?nn.length:0,je=ke.get(ne),Yn=_.state.lights;if(pe===!0&&(Fe===!0||C!==P)){const Pn=C===P&&ne.id===L;me.setState(ne,C,Pn)}let bt=!1;ne.version===je.__version?(je.needsLights&&je.lightsStateVersion!==Yn.state.version||je.outputColorSpace!==He||q.isBatchedMesh&&je.batching===!1||!q.isBatchedMesh&&je.batching===!0||q.isBatchedMesh&&je.batchingColor===!0&&q.colorTexture===null||q.isBatchedMesh&&je.batchingColor===!1&&q.colorTexture!==null||q.isInstancedMesh&&je.instancing===!1||!q.isInstancedMesh&&je.instancing===!0||q.isSkinnedMesh&&je.skinning===!1||!q.isSkinnedMesh&&je.skinning===!0||q.isInstancedMesh&&je.instancingColor===!0&&q.instanceColor===null||q.isInstancedMesh&&je.instancingColor===!1&&q.instanceColor!==null||q.isInstancedMesh&&je.instancingMorph===!0&&q.morphTexture===null||q.isInstancedMesh&&je.instancingMorph===!1&&q.morphTexture!==null||je.envMap!==Ve||ne.fog===!0&&je.fog!==be||je.numClippingPlanes!==void 0&&(je.numClippingPlanes!==me.numPlanes||je.numIntersection!==me.numIntersection)||je.vertexAlphas!==rt||je.vertexTangents!==Qe||je.morphTargets!==Ge||je.morphNormals!==Mt||je.morphColors!==Nt||je.toneMapping!==Ut||je.morphTargetsCount!==At)&&(bt=!0):(bt=!0,je.__version=ne.version);let Mn=je.currentProgram;bt===!0&&(Mn=tr(ne,j,q));let bi=!1,cn=!1,Ii=!1;const Ft=Mn.getUniforms(),Vn=je.uniforms;if(We.useProgram(Mn.program)&&(bi=!0,cn=!0,Ii=!0),ne.id!==L&&(L=ne.id,cn=!0),bi||P!==C){We.buffers.depth.getReversed()?(Se.copy(C.projectionMatrix),gE(Se),_E(Se),Ft.setValue(X,"projectionMatrix",Se)):Ft.setValue(X,"projectionMatrix",C.projectionMatrix),Ft.setValue(X,"viewMatrix",C.matrixWorldInverse);const Tn=Ft.map.cameraPosition;Tn!==void 0&&Tn.setValue(X,it.setFromMatrixPosition(C.matrixWorld)),mt.logarithmicDepthBuffer&&Ft.setValue(X,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),(ne.isMeshPhongMaterial||ne.isMeshToonMaterial||ne.isMeshLambertMaterial||ne.isMeshBasicMaterial||ne.isMeshStandardMaterial||ne.isShaderMaterial)&&Ft.setValue(X,"isOrthographic",C.isOrthographicCamera===!0),P!==C&&(P=C,cn=!0,Ii=!0)}if(q.isSkinnedMesh){Ft.setOptional(X,q,"bindMatrix"),Ft.setOptional(X,q,"bindMatrixInverse");const Pn=q.skeleton;Pn&&(Pn.boneTexture===null&&Pn.computeBoneTexture(),Ft.setValue(X,"boneTexture",Pn.boneTexture,N))}q.isBatchedMesh&&(Ft.setOptional(X,q,"batchingTexture"),Ft.setValue(X,"batchingTexture",q._matricesTexture,N),Ft.setOptional(X,q,"batchingIdTexture"),Ft.setValue(X,"batchingIdTexture",q._indirectTexture,N),Ft.setOptional(X,q,"batchingColorTexture"),q._colorsTexture!==null&&Ft.setValue(X,"batchingColorTexture",q._colorsTexture,N));const Li=te.morphAttributes;if((Li.position!==void 0||Li.normal!==void 0||Li.color!==void 0)&&Ze.update(q,te,Mn),(cn||je.receiveShadow!==q.receiveShadow)&&(je.receiveShadow=q.receiveShadow,Ft.setValue(X,"receiveShadow",q.receiveShadow)),ne.isMeshGouraudMaterial&&ne.envMap!==null&&(Vn.envMap.value=Ve,Vn.flipEnvMap.value=Ve.isCubeTexture&&Ve.isRenderTargetTexture===!1?-1:1),ne.isMeshStandardMaterial&&ne.envMap===null&&j.environment!==null&&(Vn.envMapIntensity.value=j.environmentIntensity),cn&&(Ft.setValue(X,"toneMappingExposure",b.toneMappingExposure),je.needsLights&&Ci(Vn,Ii),be&&ne.fog===!0&&Ae.refreshFogUniforms(Vn,be),Ae.refreshMaterialUniforms(Vn,ne,re,de,_.state.transmissionRenderTarget[C.id]),Rc.upload(X,hs(je),Vn,N)),ne.isShaderMaterial&&ne.uniformsNeedUpdate===!0&&(Rc.upload(X,hs(je),Vn,N),ne.uniformsNeedUpdate=!1),ne.isSpriteMaterial&&Ft.setValue(X,"center",q.center),Ft.setValue(X,"modelViewMatrix",q.modelViewMatrix),Ft.setValue(X,"normalMatrix",q.normalMatrix),Ft.setValue(X,"modelMatrix",q.matrixWorld),ne.isShaderMaterial||ne.isRawShaderMaterial){const Pn=ne.uniformsGroups;for(let Tn=0,Kn=Pn.length;Tn<Kn;Tn++){const ds=Pn[Tn];W.update(ds,Mn),W.bind(ds,Mn)}}return Mn}function Ci(C,j){C.ambientLightColor.needsUpdate=j,C.lightProbe.needsUpdate=j,C.directionalLights.needsUpdate=j,C.directionalLightShadows.needsUpdate=j,C.pointLights.needsUpdate=j,C.pointLightShadows.needsUpdate=j,C.spotLights.needsUpdate=j,C.spotLightShadows.needsUpdate=j,C.rectAreaLights.needsUpdate=j,C.hemisphereLights.needsUpdate=j}function nr(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}this.getActiveCubeFace=function(){return U},this.getActiveMipmapLevel=function(){return O},this.getRenderTarget=function(){return H},this.setRenderTargetTextures=function(C,j,te){ke.get(C.texture).__webglTexture=j,ke.get(C.depthTexture).__webglTexture=te;const ne=ke.get(C);ne.__hasExternalTextures=!0,ne.__autoAllocateDepthBuffer=te===void 0,ne.__autoAllocateDepthBuffer||ut.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),ne.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(C,j){const te=ke.get(C);te.__webglFramebuffer=j,te.__useDefaultFramebuffer=j===void 0},this.setRenderTarget=function(C,j=0,te=0){H=C,U=j,O=te;let ne=!0,q=null,be=!1,Ce=!1;if(C){const Ve=ke.get(C);if(Ve.__useDefaultFramebuffer!==void 0)We.bindFramebuffer(X.FRAMEBUFFER,null),ne=!1;else if(Ve.__webglFramebuffer===void 0)N.setupRenderTarget(C);else if(Ve.__hasExternalTextures)N.rebindTextures(C,ke.get(C.texture).__webglTexture,ke.get(C.depthTexture).__webglTexture);else if(C.depthBuffer){const Ge=C.depthTexture;if(Ve.__boundDepthTexture!==Ge){if(Ge!==null&&ke.has(Ge)&&(C.width!==Ge.image.width||C.height!==Ge.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");N.setupDepthRenderbuffer(C)}}const rt=C.texture;(rt.isData3DTexture||rt.isDataArrayTexture||rt.isCompressedArrayTexture)&&(Ce=!0);const Qe=ke.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Array.isArray(Qe[j])?q=Qe[j][te]:q=Qe[j],be=!0):C.samples>0&&N.useMultisampledRTT(C)===!1?q=ke.get(C).__webglMultisampledFramebuffer:Array.isArray(Qe)?q=Qe[te]:q=Qe,V.copy(C.viewport),ee.copy(C.scissor),Q=C.scissorTest}else V.copy(Ue).multiplyScalar(re).floor(),ee.copy(Je).multiplyScalar(re).floor(),Q=pt;if(We.bindFramebuffer(X.FRAMEBUFFER,q)&&ne&&We.drawBuffers(C,q),We.viewport(V),We.scissor(ee),We.setScissorTest(Q),be){const Ve=ke.get(C.texture);X.framebufferTexture2D(X.FRAMEBUFFER,X.COLOR_ATTACHMENT0,X.TEXTURE_CUBE_MAP_POSITIVE_X+j,Ve.__webglTexture,te)}else if(Ce){const Ve=ke.get(C.texture),rt=j||0;X.framebufferTextureLayer(X.FRAMEBUFFER,X.COLOR_ATTACHMENT0,Ve.__webglTexture,te||0,rt)}L=-1},this.readRenderTargetPixels=function(C,j,te,ne,q,be,Ce){if(!(C&&C.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let He=ke.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Ce!==void 0&&(He=He[Ce]),He){We.bindFramebuffer(X.FRAMEBUFFER,He);try{const Ve=C.texture,rt=Ve.format,Qe=Ve.type;if(!mt.textureFormatReadable(rt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!mt.textureTypeReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}j>=0&&j<=C.width-ne&&te>=0&&te<=C.height-q&&X.readPixels(j,te,ne,q,st.convert(rt),st.convert(Qe),be)}finally{const Ve=H!==null?ke.get(H).__webglFramebuffer:null;We.bindFramebuffer(X.FRAMEBUFFER,Ve)}}},this.readRenderTargetPixelsAsync=async function(C,j,te,ne,q,be,Ce){if(!(C&&C.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let He=ke.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Ce!==void 0&&(He=He[Ce]),He){const Ve=C.texture,rt=Ve.format,Qe=Ve.type;if(!mt.textureFormatReadable(rt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!mt.textureTypeReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(j>=0&&j<=C.width-ne&&te>=0&&te<=C.height-q){We.bindFramebuffer(X.FRAMEBUFFER,He);const Ge=X.createBuffer();X.bindBuffer(X.PIXEL_PACK_BUFFER,Ge),X.bufferData(X.PIXEL_PACK_BUFFER,be.byteLength,X.STREAM_READ),X.readPixels(j,te,ne,q,st.convert(rt),st.convert(Qe),0);const Mt=H!==null?ke.get(H).__webglFramebuffer:null;We.bindFramebuffer(X.FRAMEBUFFER,Mt);const Nt=X.fenceSync(X.SYNC_GPU_COMMANDS_COMPLETE,0);return X.flush(),await mE(X,Nt,4),X.bindBuffer(X.PIXEL_PACK_BUFFER,Ge),X.getBufferSubData(X.PIXEL_PACK_BUFFER,0,be),X.deleteBuffer(Ge),X.deleteSync(Nt),be}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(C,j=null,te=0){C.isTexture!==!0&&(Wo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),j=arguments[0]||null,C=arguments[1]);const ne=Math.pow(2,-te),q=Math.floor(C.image.width*ne),be=Math.floor(C.image.height*ne),Ce=j!==null?j.x:0,He=j!==null?j.y:0;N.setTexture2D(C,0),X.copyTexSubImage2D(X.TEXTURE_2D,te,0,0,Ce,He,q,be),We.unbindTexture()},this.copyTextureToTexture=function(C,j,te=null,ne=null,q=0){C.isTexture!==!0&&(Wo("WebGLRenderer: copyTextureToTexture function signature has changed."),ne=arguments[0]||null,C=arguments[1],j=arguments[2],q=arguments[3]||0,te=null);let be,Ce,He,Ve,rt,Qe,Ge,Mt,Nt;const Ut=C.isCompressedTexture?C.mipmaps[q]:C.image;te!==null?(be=te.max.x-te.min.x,Ce=te.max.y-te.min.y,He=te.isBox3?te.max.z-te.min.z:1,Ve=te.min.x,rt=te.min.y,Qe=te.isBox3?te.min.z:0):(be=Ut.width,Ce=Ut.height,He=Ut.depth||1,Ve=0,rt=0,Qe=0),ne!==null?(Ge=ne.x,Mt=ne.y,Nt=ne.z):(Ge=0,Mt=0,Nt=0);const nn=st.convert(j.format),At=st.convert(j.type);let je;j.isData3DTexture?(N.setTexture3D(j,0),je=X.TEXTURE_3D):j.isDataArrayTexture||j.isCompressedArrayTexture?(N.setTexture2DArray(j,0),je=X.TEXTURE_2D_ARRAY):(N.setTexture2D(j,0),je=X.TEXTURE_2D),X.pixelStorei(X.UNPACK_FLIP_Y_WEBGL,j.flipY),X.pixelStorei(X.UNPACK_PREMULTIPLY_ALPHA_WEBGL,j.premultiplyAlpha),X.pixelStorei(X.UNPACK_ALIGNMENT,j.unpackAlignment);const Yn=X.getParameter(X.UNPACK_ROW_LENGTH),bt=X.getParameter(X.UNPACK_IMAGE_HEIGHT),Mn=X.getParameter(X.UNPACK_SKIP_PIXELS),bi=X.getParameter(X.UNPACK_SKIP_ROWS),cn=X.getParameter(X.UNPACK_SKIP_IMAGES);X.pixelStorei(X.UNPACK_ROW_LENGTH,Ut.width),X.pixelStorei(X.UNPACK_IMAGE_HEIGHT,Ut.height),X.pixelStorei(X.UNPACK_SKIP_PIXELS,Ve),X.pixelStorei(X.UNPACK_SKIP_ROWS,rt),X.pixelStorei(X.UNPACK_SKIP_IMAGES,Qe);const Ii=C.isDataArrayTexture||C.isData3DTexture,Ft=j.isDataArrayTexture||j.isData3DTexture;if(C.isRenderTargetTexture||C.isDepthTexture){const Vn=ke.get(C),Li=ke.get(j),Pn=ke.get(Vn.__renderTarget),Tn=ke.get(Li.__renderTarget);We.bindFramebuffer(X.READ_FRAMEBUFFER,Pn.__webglFramebuffer),We.bindFramebuffer(X.DRAW_FRAMEBUFFER,Tn.__webglFramebuffer);for(let Kn=0;Kn<He;Kn++)Ii&&X.framebufferTextureLayer(X.READ_FRAMEBUFFER,X.COLOR_ATTACHMENT0,ke.get(C).__webglTexture,q,Qe+Kn),C.isDepthTexture?(Ft&&X.framebufferTextureLayer(X.DRAW_FRAMEBUFFER,X.COLOR_ATTACHMENT0,ke.get(j).__webglTexture,q,Nt+Kn),X.blitFramebuffer(Ve,rt,be,Ce,Ge,Mt,be,Ce,X.DEPTH_BUFFER_BIT,X.NEAREST)):Ft?X.copyTexSubImage3D(je,q,Ge,Mt,Nt+Kn,Ve,rt,be,Ce):X.copyTexSubImage2D(je,q,Ge,Mt,Nt+Kn,Ve,rt,be,Ce);We.bindFramebuffer(X.READ_FRAMEBUFFER,null),We.bindFramebuffer(X.DRAW_FRAMEBUFFER,null)}else Ft?C.isDataTexture||C.isData3DTexture?X.texSubImage3D(je,q,Ge,Mt,Nt,be,Ce,He,nn,At,Ut.data):j.isCompressedArrayTexture?X.compressedTexSubImage3D(je,q,Ge,Mt,Nt,be,Ce,He,nn,Ut.data):X.texSubImage3D(je,q,Ge,Mt,Nt,be,Ce,He,nn,At,Ut):C.isDataTexture?X.texSubImage2D(X.TEXTURE_2D,q,Ge,Mt,be,Ce,nn,At,Ut.data):C.isCompressedTexture?X.compressedTexSubImage2D(X.TEXTURE_2D,q,Ge,Mt,Ut.width,Ut.height,nn,Ut.data):X.texSubImage2D(X.TEXTURE_2D,q,Ge,Mt,be,Ce,nn,At,Ut);X.pixelStorei(X.UNPACK_ROW_LENGTH,Yn),X.pixelStorei(X.UNPACK_IMAGE_HEIGHT,bt),X.pixelStorei(X.UNPACK_SKIP_PIXELS,Mn),X.pixelStorei(X.UNPACK_SKIP_ROWS,bi),X.pixelStorei(X.UNPACK_SKIP_IMAGES,cn),q===0&&j.generateMipmaps&&X.generateMipmap(je),We.unbindTexture()},this.copyTextureToTexture3D=function(C,j,te=null,ne=null,q=0){return C.isTexture!==!0&&(Wo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),te=arguments[0]||null,ne=arguments[1]||null,C=arguments[2],j=arguments[3],q=arguments[4]||0),Wo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(C,j,te,ne,q)},this.initRenderTarget=function(C){ke.get(C).__webglFramebuffer===void 0&&N.setupRenderTarget(C)},this.initTexture=function(C){C.isCubeTexture?N.setTextureCube(C,0):C.isData3DTexture?N.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?N.setTexture2DArray(C,0):N.setTexture2D(C,0),We.unbindTexture()},this.resetState=function(){U=0,O=0,H=null,We.reset(),Ct.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ki}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=wt._getDrawingBufferColorSpace(e),t.unpackColorSpace=wt._getUnpackColorSpace()}}class Md{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new $e(e),this.density=t}clone(){return new Md(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class wR extends Jt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new xi,this.environmentIntensity=1,this.environmentRotation=new xi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class PR{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=ed,this.updateRanges=[],this.version=0,this.uuid=yi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=yi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=yi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Fn=new F;class Td{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Fn.fromBufferAttribute(this,t),Fn.applyMatrix4(e),this.setXYZ(t,Fn.x,Fn.y,Fn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Fn.fromBufferAttribute(this,t),Fn.applyNormalMatrix(e),this.setXYZ(t,Fn.x,Fn.y,Fn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Fn.fromBufferAttribute(this,t),Fn.transformDirection(e),this.setXYZ(t,Fn.x,Fn.y,Fn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=gi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=kt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=kt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=gi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=gi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=gi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=gi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),i=kt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=kt(t,this.array),n=kt(n,this.array),i=kt(i,this.array),s=kt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new an(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Td(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Em=new F,Am=new Dt,wm=new Dt,RR=new F,Pm=new ot,uc=new F,Zu=new wi,Rm=new ot,Ju=new oo;class Gg extends Ee{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Cp,this.bindMatrix=new ot,this.bindMatrixInverse=new ot,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new er),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,uc),this.boundingBox.expandByPoint(uc)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new wi),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,uc),this.boundingSphere.expandByPoint(uc)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,i=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Zu.copy(this.boundingSphere),Zu.applyMatrix4(i),e.ray.intersectsSphere(Zu)!==!1&&(Rm.copy(i).invert(),Ju.copy(e.ray).applyMatrix4(Rm),!(this.boundingBox!==null&&Ju.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Ju)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new Dt,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);const s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Cp?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===FT?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,i=this.geometry;Am.fromBufferAttribute(i.attributes.skinIndex,e),wm.fromBufferAttribute(i.attributes.skinWeight,e),Em.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){const a=wm.getComponent(s);if(a!==0){const c=Am.getComponent(s);Pm.multiplyMatrices(n.bones[c].matrixWorld,n.boneInverses[c]),t.addScaledVector(RR.copy(Em).applyMatrix4(Pm),a)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Vc extends Jt{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Wg extends Sn{constructor(e=null,t=1,n=1,i,s,a,c,u,h=zn,f=zn,p,m){super(null,a,c,u,h,f,i,s,p,m),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Cm=new ot,CR=new ot;class ia{constructor(e=[],t=[]){this.uuid=yi(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new ot)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new ot;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,a=e.length;s<a;s++){const c=e[s]?e[s].matrixWorld:CR;Cm.multiplyMatrices(c,t[s]),Cm.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new ia(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Wg(t,e,e,li,vi);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){const s=e.bones[n];let a=t[s];a===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),a=new Vc),this.bones.push(a),this.boneInverses.push(new ot().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){const a=t[i];e.bones.push(a.uuid);const c=n[i];e.boneInverses.push(c.toArray())}return e}}class nd extends an{constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const ks=new ot,Im=new ot,hc=[],Lm=new er,IR=new ot,Uo=new Ee,Fo=new wi;class LR extends Ee{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new nd(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let i=0;i<n;i++)this.setMatrixAt(i,IR)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new er),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,ks),Lm.copy(e.boundingBox).applyMatrix4(ks),this.boundingBox.union(Lm)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new wi),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,ks),Fo.copy(e.boundingSphere).applyMatrix4(ks),this.boundingSphere.union(Fo)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,i=this.morphTexture.source.data.data,s=n.length+1,a=e*s+1;for(let c=0;c<n.length;c++)n[c]=i[a+c]}raycast(e,t){const n=this.matrixWorld,i=this.count;if(Uo.geometry=this.geometry,Uo.material=this.material,Uo.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Fo.copy(this.boundingSphere),Fo.applyMatrix4(n),e.ray.intersectsSphere(Fo)!==!1))for(let s=0;s<i;s++){this.getMatrixAt(s,ks),Im.multiplyMatrices(n,ks),Uo.matrixWorld=Im,Uo.raycast(e,hc);for(let a=0,c=hc.length;a<c;a++){const u=hc[a];u.instanceId=s,u.object=this,t.push(u)}hc.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new nd(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,i=n.length+1;this.morphTexture===null&&(this.morphTexture=new Wg(new Float32Array(i*this.count),i,this.count,dd,vi));const s=this.morphTexture.source.data.data;let a=0;for(let h=0;h<n.length;h++)a+=n[h];const c=this.geometry.morphTargetsRelative?1:1-a,u=i*e;s[u]=c,s.set(n,u+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Gc extends Ai{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new $e(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Uc=new F,Fc=new F,Dm=new ot,Bo=new oo,dc=new wi,Qu=new F,Nm=new F;class mi extends Jt{constructor(e=new mn,t=new Gc){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)Uc.fromBufferAttribute(t,i-1),Fc.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=Uc.distanceTo(Fc);e.setAttribute("lineDistance",new Xt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),dc.copy(n.boundingSphere),dc.applyMatrix4(i),dc.radius+=s,e.ray.intersectsSphere(dc)===!1)return;Dm.copy(i).invert(),Bo.copy(e.ray).applyMatrix4(Dm);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=this.isLineSegments?2:1,f=n.index,m=n.attributes.position;if(f!==null){const g=Math.max(0,a.start),x=Math.min(f.count,a.start+a.count);for(let M=g,v=x-1;M<v;M+=h){const _=f.getX(M),A=f.getX(M+1),w=fc(this,e,Bo,u,_,A);w&&t.push(w)}if(this.isLineLoop){const M=f.getX(x-1),v=f.getX(g),_=fc(this,e,Bo,u,M,v);_&&t.push(_)}}else{const g=Math.max(0,a.start),x=Math.min(m.count,a.start+a.count);for(let M=g,v=x-1;M<v;M+=h){const _=fc(this,e,Bo,u,M,M+1);_&&t.push(_)}if(this.isLineLoop){const M=fc(this,e,Bo,u,x-1,g);M&&t.push(M)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function fc(r,e,t,n,i,s){const a=r.geometry.attributes.position;if(Uc.fromBufferAttribute(a,i),Fc.fromBufferAttribute(a,s),t.distanceSqToSegment(Uc,Fc,Qu,Nm)>n)return;Qu.applyMatrix4(r.matrixWorld);const u=e.ray.origin.distanceTo(Qu);if(!(u<e.near||u>e.far))return{distance:u,point:Nm.clone().applyMatrix4(r.matrixWorld),index:i,face:null,faceIndex:null,barycoord:null,object:r}}const Om=new F,Um=new F;class jg extends mi{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)Om.fromBufferAttribute(t,i),Um.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Om.distanceTo(Um);e.setAttribute("lineDistance",new Xt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class DR extends mi{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Xg extends Ai{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new $e(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Fm=new ot,id=new oo,pc=new wi,mc=new F;class NR extends Jt{constructor(e=new mn,t=new Xg){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),pc.copy(n.boundingSphere),pc.applyMatrix4(i),pc.radius+=s,e.ray.intersectsSphere(pc)===!1)return;Fm.copy(i).invert(),id.copy(e.ray).applyMatrix4(Fm);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=n.index,p=n.attributes.position;if(h!==null){const m=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=m,M=g;x<M;x++){const v=h.getX(x);mc.fromBufferAttribute(p,v),Bm(mc,v,u,i,e,t,this)}}else{const m=Math.max(0,a.start),g=Math.min(p.count,a.start+a.count);for(let x=m,M=g;x<M;x++)mc.fromBufferAttribute(p,x),Bm(mc,x,u,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function Bm(r,e,t,n,i,s,a){const c=id.distanceSqToPoint(r);if(c<t){const u=new F;id.closestPointToPoint(r,u),u.applyMatrix4(n);const h=i.ray.origin.distanceTo(u);if(h<i.near||h>i.far)return;s.push({distance:h,distanceToRay:Math.sqrt(c),point:u,index:e,face:null,faceIndex:null,barycoord:null,object:a})}}class An extends mn{constructor(e=1,t=1,n=1,i=32,s=1,a=!1,c=0,u=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:i,heightSegments:s,openEnded:a,thetaStart:c,thetaLength:u};const h=this;i=Math.floor(i),s=Math.floor(s);const f=[],p=[],m=[],g=[];let x=0;const M=[],v=n/2;let _=0;A(),a===!1&&(e>0&&w(!0),t>0&&w(!1)),this.setIndex(f),this.setAttribute("position",new Xt(p,3)),this.setAttribute("normal",new Xt(m,3)),this.setAttribute("uv",new Xt(g,2));function A(){const b=new F,B=new F;let U=0;const O=(t-e)/n;for(let H=0;H<=s;H++){const L=[],P=H/s,V=P*(t-e)+e;for(let ee=0;ee<=i;ee++){const Q=ee/i,ae=Q*u+c,ce=Math.sin(ae),J=Math.cos(ae);B.x=V*ce,B.y=-P*n+v,B.z=V*J,p.push(B.x,B.y,B.z),b.set(ce,O,J).normalize(),m.push(b.x,b.y,b.z),g.push(Q,1-P),L.push(x++)}M.push(L)}for(let H=0;H<i;H++)for(let L=0;L<s;L++){const P=M[L][H],V=M[L+1][H],ee=M[L+1][H+1],Q=M[L][H+1];(e>0||L!==0)&&(f.push(P,V,Q),U+=3),(t>0||L!==s-1)&&(f.push(V,ee,Q),U+=3)}h.addGroup(_,U,0),_+=U}function w(b){const B=x,U=new tt,O=new F;let H=0;const L=b===!0?e:t,P=b===!0?1:-1;for(let ee=1;ee<=i;ee++)p.push(0,v*P,0),m.push(0,P,0),g.push(.5,.5),x++;const V=x;for(let ee=0;ee<=i;ee++){const ae=ee/i*u+c,ce=Math.cos(ae),J=Math.sin(ae);O.x=L*J,O.y=v*P,O.z=L*ce,p.push(O.x,O.y,O.z),m.push(0,P,0),U.x=ce*.5+.5,U.y=J*.5*P+.5,g.push(U.x,U.y),x++}for(let ee=0;ee<i;ee++){const Q=B+ee,ae=V+ee;b===!0?f.push(ae,ae+1,Q):f.push(ae+1,ae,Q),H+=3}h.addGroup(_,H,b===!0?1:2),_+=H}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new An(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ed extends An{constructor(e=1,t=1,n=32,i=1,s=!1,a=0,c=Math.PI*2){super(0,e,t,n,i,s,a,c),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:i,openEnded:s,thetaStart:a,thetaLength:c}}static fromJSON(e){return new Ed(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ad extends mn{constructor(e=[],t=[],n=1,i=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:i};const s=[],a=[];c(i),h(n),f(),this.setAttribute("position",new Xt(s,3)),this.setAttribute("normal",new Xt(s.slice(),3)),this.setAttribute("uv",new Xt(a,2)),i===0?this.computeVertexNormals():this.normalizeNormals();function c(A){const w=new F,b=new F,B=new F;for(let U=0;U<t.length;U+=3)g(t[U+0],w),g(t[U+1],b),g(t[U+2],B),u(w,b,B,A)}function u(A,w,b,B){const U=B+1,O=[];for(let H=0;H<=U;H++){O[H]=[];const L=A.clone().lerp(b,H/U),P=w.clone().lerp(b,H/U),V=U-H;for(let ee=0;ee<=V;ee++)ee===0&&H===U?O[H][ee]=L:O[H][ee]=L.clone().lerp(P,ee/V)}for(let H=0;H<U;H++)for(let L=0;L<2*(U-H)-1;L++){const P=Math.floor(L/2);L%2===0?(m(O[H][P+1]),m(O[H+1][P]),m(O[H][P])):(m(O[H][P+1]),m(O[H+1][P+1]),m(O[H+1][P]))}}function h(A){const w=new F;for(let b=0;b<s.length;b+=3)w.x=s[b+0],w.y=s[b+1],w.z=s[b+2],w.normalize().multiplyScalar(A),s[b+0]=w.x,s[b+1]=w.y,s[b+2]=w.z}function f(){const A=new F;for(let w=0;w<s.length;w+=3){A.x=s[w+0],A.y=s[w+1],A.z=s[w+2];const b=v(A)/2/Math.PI+.5,B=_(A)/Math.PI+.5;a.push(b,1-B)}x(),p()}function p(){for(let A=0;A<a.length;A+=6){const w=a[A+0],b=a[A+2],B=a[A+4],U=Math.max(w,b,B),O=Math.min(w,b,B);U>.9&&O<.1&&(w<.2&&(a[A+0]+=1),b<.2&&(a[A+2]+=1),B<.2&&(a[A+4]+=1))}}function m(A){s.push(A.x,A.y,A.z)}function g(A,w){const b=A*3;w.x=e[b+0],w.y=e[b+1],w.z=e[b+2]}function x(){const A=new F,w=new F,b=new F,B=new F,U=new tt,O=new tt,H=new tt;for(let L=0,P=0;L<s.length;L+=9,P+=6){A.set(s[L+0],s[L+1],s[L+2]),w.set(s[L+3],s[L+4],s[L+5]),b.set(s[L+6],s[L+7],s[L+8]),U.set(a[P+0],a[P+1]),O.set(a[P+2],a[P+3]),H.set(a[P+4],a[P+5]),B.copy(A).add(w).add(b).divideScalar(3);const V=v(B);M(U,P+0,A,V),M(O,P+2,w,V),M(H,P+4,b,V)}}function M(A,w,b,B){B<0&&A.x===1&&(a[w]=A.x-1),b.x===0&&b.z===0&&(a[w]=B/2/Math.PI+.5)}function v(A){return Math.atan2(A.z,-A.x)}function _(A){return Math.atan2(-A.y,Math.sqrt(A.x*A.x+A.z*A.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ad(e.vertices,e.indices,e.radius,e.details)}}class Ws extends Ad{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],i=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,i,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Ws(e.radius,e.detail)}}class ra extends mn{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,a=0,c=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:a,thetaLength:c},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const u=Math.min(a+c,Math.PI);let h=0;const f=[],p=new F,m=new F,g=[],x=[],M=[],v=[];for(let _=0;_<=n;_++){const A=[],w=_/n;let b=0;_===0&&a===0?b=.5/t:_===n&&u===Math.PI&&(b=-.5/t);for(let B=0;B<=t;B++){const U=B/t;p.x=-e*Math.cos(i+U*s)*Math.sin(a+w*c),p.y=e*Math.cos(a+w*c),p.z=e*Math.sin(i+U*s)*Math.sin(a+w*c),x.push(p.x,p.y,p.z),m.copy(p).normalize(),M.push(m.x,m.y,m.z),v.push(U+b,1-w),A.push(h++)}f.push(A)}for(let _=0;_<n;_++)for(let A=0;A<t;A++){const w=f[_][A+1],b=f[_][A],B=f[_+1][A],U=f[_+1][A+1];(_!==0||a>0)&&g.push(w,b,U),(_!==n-1||u<Math.PI)&&g.push(b,B,U)}this.setIndex(g),this.setAttribute("position",new Xt(x,3)),this.setAttribute("normal",new Xt(M,3)),this.setAttribute("uv",new Xt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ra(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class rs extends mn{constructor(e=1,t=.4,n=12,i=48,s=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:i,arc:s},n=Math.floor(n),i=Math.floor(i);const a=[],c=[],u=[],h=[],f=new F,p=new F,m=new F;for(let g=0;g<=n;g++)for(let x=0;x<=i;x++){const M=x/i*s,v=g/n*Math.PI*2;p.x=(e+t*Math.cos(v))*Math.cos(M),p.y=(e+t*Math.cos(v))*Math.sin(M),p.z=t*Math.sin(v),c.push(p.x,p.y,p.z),f.x=e*Math.cos(M),f.y=e*Math.sin(M),m.subVectors(p,f).normalize(),u.push(m.x,m.y,m.z),h.push(x/i),h.push(g/n)}for(let g=1;g<=n;g++)for(let x=1;x<=i;x++){const M=(i+1)*g+x-1,v=(i+1)*(g-1)+x-1,_=(i+1)*(g-1)+x,A=(i+1)*g+x;a.push(M,v,A),a.push(v,_,A)}this.setIndex(a),this.setAttribute("position",new Xt(c,3)),this.setAttribute("normal",new Xt(u,3)),this.setAttribute("uv",new Xt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new rs(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class as extends Ai{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new $e(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new $e(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Eg,this.normalScale=new tt(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new xi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Pi extends as{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new tt(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return wn(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new $e(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new $e(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new $e(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function gc(r,e,t){return!r||!t&&r.constructor===e?r:typeof e.BYTES_PER_ELEMENT=="number"?new e(r):Array.prototype.slice.call(r)}function OR(r){return ArrayBuffer.isView(r)&&!(r instanceof DataView)}function UR(r){function e(i,s){return r[i]-r[s]}const t=r.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}function km(r,e,t){const n=r.length,i=new r.constructor(n);for(let s=0,a=0;a!==n;++s){const c=t[s]*e;for(let u=0;u!==e;++u)i[a++]=r[c+u]}return i}function qg(r,e,t,n){let i=1,s=r[0];for(;s!==void 0&&s[n]===void 0;)s=r[i++];if(s===void 0)return;let a=s[n];if(a!==void 0)if(Array.isArray(a))do a=s[n],a!==void 0&&(e.push(s.time),t.push.apply(t,a)),s=r[i++];while(s!==void 0);else if(a.toArray!==void 0)do a=s[n],a!==void 0&&(e.push(s.time),a.toArray(t,t.length)),s=r[i++];while(s!==void 0);else do a=s[n],a!==void 0&&(e.push(s.time),t.push(a)),s=r[i++];while(s!==void 0)}class sa{constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let a;n:{i:if(!(e<i)){for(let c=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===c)break;if(s=i,i=t[++n],e<i)break t}a=t.length;break n}if(!(e>=s)){const c=t[1];e<c&&(n=2,s=c);for(let u=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===u)break;if(i=s,s=t[--n-1],e>=s)break t}a=n,n=0;break n}break e}for(;n<a;){const c=n+a>>>1;e<t[c]?a=c:n=c+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let a=0;a!==i;++a)t[a]=n[s+a];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class FR extends sa{constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Hs,endingEnd:Hs}}intervalChanged_(e,t,n){const i=this.parameterPositions;let s=e-2,a=e+1,c=i[s],u=i[a];if(c===void 0)switch(this.getSettings_().endingStart){case Vs:s=e,c=2*t-n;break;case Nc:s=i.length-2,c=t+i[s]-i[s+1];break;default:s=e,c=n}if(u===void 0)switch(this.getSettings_().endingEnd){case Vs:a=e,u=2*n-t;break;case Nc:a=1,u=n+i[1]-i[0];break;default:a=e-1,u=t}const h=(n-t)*.5,f=this.valueSize;this._weightPrev=h/(t-c),this._weightNext=h/(u-n),this._offsetPrev=s*f,this._offsetNext=a*f}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=this._offsetPrev,p=this._offsetNext,m=this._weightPrev,g=this._weightNext,x=(n-t)/(i-t),M=x*x,v=M*x,_=-m*v+2*m*M-m*x,A=(1+m)*v+(-1.5-2*m)*M+(-.5+m)*x+1,w=(-1-g)*v+(1.5+g)*M+.5*x,b=g*v-g*M;for(let B=0;B!==c;++B)s[B]=_*a[f+B]+A*a[h+B]+w*a[u+B]+b*a[p+B];return s}}class Yg extends sa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=(n-t)/(i-t),p=1-f;for(let m=0;m!==c;++m)s[m]=a[h+m]*p+a[u+m]*f;return s}}class BR extends sa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}}class Ri{constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=gc(t,this.TimeBufferType),this.values=gc(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:gc(e.times,Array),values:gc(e.values,Array)};const i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new BR(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Yg(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new FR(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case Qo:t=this.InterpolantFactoryMethodDiscrete;break;case ea:t=this.InterpolantFactoryMethodLinear;break;case Mu:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return Qo;case this.InterpolantFactoryMethodLinear:return ea;case this.InterpolantFactoryMethodSmooth:return Mu}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){const n=this.times,i=n.length;let s=0,a=i-1;for(;s!==i&&n[s]<e;)++s;for(;a!==-1&&n[a]>t;)--a;if(++a,s!==0||a!==i){s>=a&&(a=Math.max(a,1),s=a-1);const c=this.getValueSize();this.times=n.slice(s,a),this.values=this.values.slice(s*c,a*c)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let a=null;for(let c=0;c!==s;c++){const u=n[c];if(typeof u=="number"&&isNaN(u)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,c,u),e=!1;break}if(a!==null&&a>u){console.error("THREE.KeyframeTrack: Out of order keys.",this,c,u,a),e=!1;break}a=u}if(i!==void 0&&OR(i))for(let c=0,u=i.length;c!==u;++c){const h=i[c];if(isNaN(h)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,c,h),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),i=this.getInterpolation()===Mu,s=e.length-1;let a=1;for(let c=1;c<s;++c){let u=!1;const h=e[c],f=e[c+1];if(h!==f&&(c!==1||h!==e[0]))if(i)u=!0;else{const p=c*n,m=p-n,g=p+n;for(let x=0;x!==n;++x){const M=t[p+x];if(M!==t[m+x]||M!==t[g+x]){u=!0;break}}}if(u){if(c!==a){e[a]=e[c];const p=c*n,m=a*n;for(let g=0;g!==n;++g)t[m+g]=t[p+g]}++a}}if(s>0){e[a]=e[s];for(let c=s*n,u=a*n,h=0;h!==n;++h)t[u+h]=t[c+h];++a}return a!==e.length?(this.times=e.slice(0,a),this.values=t.slice(0,a*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}}Ri.prototype.TimeBufferType=Float32Array;Ri.prototype.ValueBufferType=Float32Array;Ri.prototype.DefaultInterpolation=ea;class lo extends Ri{constructor(e,t,n){super(e,t,n)}}lo.prototype.ValueTypeName="bool";lo.prototype.ValueBufferType=Array;lo.prototype.DefaultInterpolation=Qo;lo.prototype.InterpolantFactoryMethodLinear=void 0;lo.prototype.InterpolantFactoryMethodSmooth=void 0;class Kg extends Ri{}Kg.prototype.ValueTypeName="color";class ro extends Ri{}ro.prototype.ValueTypeName="number";class kR extends sa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=(n-t)/(i-t);let h=e*c;for(let f=h+c;h!==f;h+=4)en.slerpFlat(s,0,a,h-c,a,h,u);return s}}class cs extends Ri{InterpolantFactoryMethodLinear(e){return new kR(this.times,this.values,this.getValueSize(),e)}}cs.prototype.ValueTypeName="quaternion";cs.prototype.InterpolantFactoryMethodSmooth=void 0;class uo extends Ri{constructor(e,t,n){super(e,t,n)}}uo.prototype.ValueTypeName="string";uo.prototype.ValueBufferType=Array;uo.prototype.DefaultInterpolation=Qo;uo.prototype.InterpolantFactoryMethodLinear=void 0;uo.prototype.InterpolantFactoryMethodSmooth=void 0;class ls extends Ri{}ls.prototype.ValueTypeName="vector";class Bc{constructor(e="",t=-1,n=[],i=_d){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=yi(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,i=1/(e.fps||1);for(let a=0,c=n.length;a!==c;++a)t.push(HR(n[a]).scale(i));const s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){const t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,a=n.length;s!==a;++s)t.push(Ri.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){const s=t.length,a=[];for(let c=0;c<s;c++){let u=[],h=[];u.push((c+s-1)%s,c,(c+1)%s),h.push(0,1,0);const f=UR(u);u=km(u,1,f),h=km(h,1,f),!i&&u[0]===0&&(u.push(s),h.push(h[0])),a.push(new ro(".morphTargetInfluences["+t[c].name+"]",u,h).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const i={},s=/^([\w-]*?)([\d]+)$/;for(let c=0,u=e.length;c<u;c++){const h=e[c],f=h.name.match(s);if(f&&f.length>1){const p=f[1];let m=i[p];m||(i[p]=m=[]),m.push(h)}}const a=[];for(const c in i)a.push(this.CreateFromMorphTargetSequence(c,i[c],t,n));return a}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(p,m,g,x,M){if(g.length!==0){const v=[],_=[];qg(g,v,_,x),v.length!==0&&M.push(new p(m,v,_))}},i=[],s=e.name||"default",a=e.fps||30,c=e.blendMode;let u=e.length||-1;const h=e.hierarchy||[];for(let p=0;p<h.length;p++){const m=h[p].keys;if(!(!m||m.length===0))if(m[0].morphTargets){const g={};let x;for(x=0;x<m.length;x++)if(m[x].morphTargets)for(let M=0;M<m[x].morphTargets.length;M++)g[m[x].morphTargets[M]]=-1;for(const M in g){const v=[],_=[];for(let A=0;A!==m[x].morphTargets.length;++A){const w=m[x];v.push(w.time),_.push(w.morphTarget===M?1:0)}i.push(new ro(".morphTargetInfluence["+M+"]",v,_))}u=g.length*a}else{const g=".bones["+t[p].name+"]";n(ls,g+".position",m,"pos",i),n(cs,g+".quaternion",m,"rot",i),n(ls,g+".scale",m,"scl",i)}}return i.length===0?null:new this(s,u,i,c)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,i=e.length;n!==i;++n){const s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function zR(r){switch(r.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return ro;case"vector":case"vector2":case"vector3":case"vector4":return ls;case"color":return Kg;case"quaternion":return cs;case"bool":case"boolean":return lo;case"string":return uo}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+r)}function HR(r){if(r.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=zR(r.type);if(r.times===void 0){const t=[],n=[];qg(r.keys,t,n,"value"),r.times=t,r.values=n}return e.parse!==void 0?e.parse(r):new e(r.name,r.times,r.values,r.interpolation)}const xr={enabled:!1,files:{},add:function(r,e){this.enabled!==!1&&(this.files[r]=e)},get:function(r){if(this.enabled!==!1)return this.files[r]},remove:function(r){delete this.files[r]},clear:function(){this.files={}}};class VR{constructor(e,t,n){const i=this;let s=!1,a=0,c=0,u;const h=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(f){c++,s===!1&&i.onStart!==void 0&&i.onStart(f,a,c),s=!0},this.itemEnd=function(f){a++,i.onProgress!==void 0&&i.onProgress(f,a,c),a===c&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(f){i.onError!==void 0&&i.onError(f)},this.resolveURL=function(f){return u?u(f):f},this.setURLModifier=function(f){return u=f,this},this.addHandler=function(f,p){return h.push(f,p),this},this.removeHandler=function(f){const p=h.indexOf(f);return p!==-1&&h.splice(p,2),this},this.getHandler=function(f){for(let p=0,m=h.length;p<m;p+=2){const g=h[p],x=h[p+1];if(g.global&&(g.lastIndex=0),g.test(f))return x}return null}}}const GR=new VR;class us{constructor(e){this.manager=e!==void 0?e:GR,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}us.DEFAULT_MATERIAL_NAME="__DEFAULT";const ji={};class WR extends Error{constructor(e,t){super(e),this.response=t}}class wd extends us{constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=xr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(ji[e]!==void 0){ji[e].push({onLoad:t,onProgress:n,onError:i});return}ji[e]=[],ji[e].push({onLoad:t,onProgress:n,onError:i});const a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),c=this.mimeType,u=this.responseType;fetch(a).then(h=>{if(h.status===200||h.status===0){if(h.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||h.body===void 0||h.body.getReader===void 0)return h;const f=ji[e],p=h.body.getReader(),m=h.headers.get("X-File-Size")||h.headers.get("Content-Length"),g=m?parseInt(m):0,x=g!==0;let M=0;const v=new ReadableStream({start(_){A();function A(){p.read().then(({done:w,value:b})=>{if(w)_.close();else{M+=b.byteLength;const B=new ProgressEvent("progress",{lengthComputable:x,loaded:M,total:g});for(let U=0,O=f.length;U<O;U++){const H=f[U];H.onProgress&&H.onProgress(B)}_.enqueue(b),A()}},w=>{_.error(w)})}}});return new Response(v)}else throw new WR(`fetch for "${h.url}" responded with ${h.status}: ${h.statusText}`,h)}).then(h=>{switch(u){case"arraybuffer":return h.arrayBuffer();case"blob":return h.blob();case"document":return h.text().then(f=>new DOMParser().parseFromString(f,c));case"json":return h.json();default:if(c===void 0)return h.text();{const p=/charset="?([^;"\s]*)"?/i.exec(c),m=p&&p[1]?p[1].toLowerCase():void 0,g=new TextDecoder(m);return h.arrayBuffer().then(x=>g.decode(x))}}}).then(h=>{xr.add(e,h);const f=ji[e];delete ji[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onLoad&&g.onLoad(h)}}).catch(h=>{const f=ji[e];if(f===void 0)throw this.manager.itemError(e),h;delete ji[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onError&&g.onError(h)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class jR extends us{constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=xr.get(e);if(a!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a;const c=ta("img");function u(){f(),xr.add(e,this),t&&t(this),s.manager.itemEnd(e)}function h(p){f(),i&&i(p),s.manager.itemError(e),s.manager.itemEnd(e)}function f(){c.removeEventListener("load",u,!1),c.removeEventListener("error",h,!1)}return c.addEventListener("load",u,!1),c.addEventListener("error",h,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(c.crossOrigin=this.crossOrigin),s.manager.itemStart(e),c.src=e,c}}class XR extends us{constructor(e){super(e)}load(e,t,n,i){const s=new Sn,a=new jR(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(c){s.image=c,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}}class Wc extends Jt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new $e(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const eh=new ot,zm=new F,Hm=new F;class Pd{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new tt(512,512),this.map=null,this.mapPass=null,this.matrix=new ot,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new xd,this._frameExtents=new tt(1,1),this._viewportCount=1,this._viewports=[new Dt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;zm.setFromMatrixPosition(e.matrixWorld),t.position.copy(zm),Hm.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Hm),t.updateMatrixWorld(),eh.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(eh),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(eh)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class qR extends Pd{constructor(){super(new kn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=no*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class YR extends Wc{constructor(e,t,n=0,i=Math.PI/3,s=0,a=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(Jt.DEFAULT_UP),this.updateMatrix(),this.target=new Jt,this.distance=n,this.angle=i,this.penumbra=s,this.decay=a,this.map=null,this.shadow=new qR}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Vm=new ot,ko=new F,th=new F;class KR extends Pd{constructor(){super(new kn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new tt(4,2),this._viewportCount=6,this._viewports=[new Dt(2,1,1,1),new Dt(0,1,1,1),new Dt(3,1,1,1),new Dt(1,1,1,1),new Dt(3,0,1,1),new Dt(1,0,1,1)],this._cubeDirections=[new F(1,0,0),new F(-1,0,0),new F(0,0,1),new F(0,0,-1),new F(0,1,0),new F(0,-1,0)],this._cubeUps=[new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,0,1),new F(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),ko.setFromMatrixPosition(e.matrixWorld),n.position.copy(ko),th.copy(n.position),th.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(th),n.updateMatrixWorld(),i.makeTranslation(-ko.x,-ko.y,-ko.z),Vm.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Vm)}}class $g extends Wc{constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new KR}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class $R extends Pd{constructor(){super(new bd(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Cc extends Wc{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Jt.DEFAULT_UP),this.updateMatrix(),this.target=new Jt,this.shadow=new $R}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class ZR extends Wc{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class Zo{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class JR extends us{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=xr.get(e);if(a!==void 0){if(s.manager.itemStart(e),a.then){a.then(h=>{t&&t(h),s.manager.itemEnd(e)}).catch(h=>{i&&i(h)});return}return setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a}const c={};c.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",c.headers=this.requestHeader;const u=fetch(e,c).then(function(h){return h.blob()}).then(function(h){return createImageBitmap(h,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(h){return xr.add(e,h),t&&t(h),s.manager.itemEnd(e),h}).catch(function(h){i&&i(h),xr.remove(e),s.manager.itemError(e),s.manager.itemEnd(e)});xr.add(e,u),s.manager.itemStart(e)}}class QR{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Gm(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Gm();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Gm(){return performance.now()}class eC{constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,a;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,a=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,a=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,a=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=a,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){const n=this.buffer,i=this.valueSize,s=e*i+i;let a=this.cumulativeWeight;if(a===0){for(let c=0;c!==i;++c)n[s+c]=n[c];a=t}else{a+=t;const c=t/a;this._mixBufferRegion(n,s,0,c,i)}this.cumulativeWeight=a}accumulateAdditive(e){const t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){const t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,a=this.cumulativeWeightAdditive,c=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){const u=t*this._origIndex;this._mixBufferRegion(n,i,u,1-s,t)}a>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let u=t,h=t+t;u!==h;++u)if(n[u]!==n[u+t]){c.setValue(n,i);break}}saveOriginalState(){const e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,a=i;s!==a;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){const e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){const e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){const e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let a=0;a!==s;++a)e[t+a]=e[n+a]}_slerp(e,t,n,i){en.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){const a=this._workIndex*s;en.multiplyQuaternionsFlat(e,a,e,t,e,n),en.slerpFlat(e,t,e,t,e,a,i)}_lerp(e,t,n,i,s){const a=1-i;for(let c=0;c!==s;++c){const u=t+c;e[u]=e[u]*a+e[n+c]*i}}_lerpAdditive(e,t,n,i,s){for(let a=0;a!==s;++a){const c=t+a;e[c]=e[c]+e[n+a]*i}}}const Rd="\\[\\]\\.:\\/",tC=new RegExp("["+Rd+"]","g"),Cd="[^"+Rd+"]",nC="[^"+Rd.replace("\\.","")+"]",iC=/((?:WC+[\/:])*)/.source.replace("WC",Cd),rC=/(WCOD+)?/.source.replace("WCOD",nC),sC=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Cd),oC=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Cd),aC=new RegExp("^"+iC+rC+sC+oC+"$"),cC=["material","materials","bones","map"];class lC{constructor(e,t,n){const i=n||Ot.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class Ot{constructor(e,t,n){this.path=t,this.parsedPath=n||Ot.parseTrackName(t),this.node=Ot.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new Ot.Composite(e,t,n):new Ot(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(tC,"")}static parseTrackName(e){const t=aC.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){const s=n.nodeName.substring(i+1);cC.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(s){for(let a=0;a<s.length;a++){const c=s[a];if(c.name===t||c.uuid===t)return c;const u=n(c.children);if(u)return u}return null},i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,i=t.propertyName;let s=t.propertyIndex;if(e||(e=Ot.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let h=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let f=0;f<e.length;f++)if(e[f].name===h){h=f;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(h!==void 0){if(e[h]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[h]}}const a=e[i];if(a===void 0){const h=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+h+"."+i+" but it wasn't found.",e);return}let c=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?c=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(c=this.Versioning.MatrixWorldNeedsUpdate);let u=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}u=this.BindingType.ArrayElement,this.resolvedProperty=a,this.propertyIndex=s}else a.fromArray!==void 0&&a.toArray!==void 0?(u=this.BindingType.HasFromToArray,this.resolvedProperty=a):Array.isArray(a)?(u=this.BindingType.EntireArray,this.resolvedProperty=a):this.propertyName=i;this.getValue=this.GetterByBindingType[u],this.setValue=this.SetterByBindingTypeAndVersioning[u][c]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}Ot.Composite=lC;Ot.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};Ot.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};Ot.prototype.GetterByBindingType=[Ot.prototype._getValue_direct,Ot.prototype._getValue_array,Ot.prototype._getValue_arrayElement,Ot.prototype._getValue_toArray];Ot.prototype.SetterByBindingTypeAndVersioning=[[Ot.prototype._setValue_direct,Ot.prototype._setValue_direct_setNeedsUpdate,Ot.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[Ot.prototype._setValue_array,Ot.prototype._setValue_array_setNeedsUpdate,Ot.prototype._setValue_array_setMatrixWorldNeedsUpdate],[Ot.prototype._setValue_arrayElement,Ot.prototype._setValue_arrayElement_setNeedsUpdate,Ot.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[Ot.prototype._setValue_fromArray,Ot.prototype._setValue_fromArray_setNeedsUpdate,Ot.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];class uC{constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;const s=t.tracks,a=s.length,c=new Array(a),u={endingStart:Hs,endingEnd:Hs};for(let h=0;h!==a;++h){const f=s[h].createInterpolant(null);c[h]=f,f.settings=u}this._interpolantSettings=u,this._interpolants=c,this._propertyBindings=new Array(a),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=gd,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){const i=this._clip.duration,s=e._clip.duration,a=s/i,c=i/s;e.warp(1,a,t),this.warp(c,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){const e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){const i=this._mixer,s=i.time,a=this.timeScale;let c=this._timeScaleInterpolant;c===null&&(c=i._lendControlInterpolant(),this._timeScaleInterpolant=c);const u=c.parameterPositions,h=c.sampleValues;return u[0]=s,u[1]=s+n,h[0]=e/a,h[1]=t/a,this}stopWarping(){const e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}const s=this._startTime;if(s!==null){const u=(e-s)*n;u<0||n===0?t=0:(this._startTime=null,t=n*u)}t*=this._updateTimeScale(e);const a=this._updateTime(t),c=this._updateWeight(e);if(c>0){const u=this._interpolants,h=this._propertyBindings;switch(this.blendMode){case zT:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulateAdditive(c);break;case _d:default:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulate(i,c)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;const n=this._weightInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;const n=this._timeScaleInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){const t=this._clip.duration,n=this.loop;let i=this.time+e,s=this._loopCount;const a=n===kT;if(e===0)return s===-1?i:a&&(s&1)===1?t-i:i;if(n===BT){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,a)):this._setEndings(this.repetitions===0,!0,a)),i>=t||i<0){const c=Math.floor(i/t);i-=t*c,s+=Math.abs(c);const u=this.repetitions-s;if(u<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(u===1){const h=e<0;this._setEndings(h,!h,a)}else this._setEndings(!1,!1,a);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:c})}}else this.time=i;if(a&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){const i=this._interpolantSettings;n?(i.endingStart=Vs,i.endingEnd=Vs):(e?i.endingStart=this.zeroSlopeAtStart?Vs:Hs:i.endingStart=Nc,t?i.endingEnd=this.zeroSlopeAtEnd?Vs:Hs:i.endingEnd=Nc)}_scheduleFading(e,t,n){const i=this._mixer,s=i.time;let a=this._weightInterpolant;a===null&&(a=i._lendControlInterpolant(),this._weightInterpolant=a);const c=a.parameterPositions,u=a.sampleValues;return c[0]=s,u[0]=t,c[1]=s+e,u[1]=n,this}}const hC=new Float32Array(1);class Zg extends Tr{constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){const n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,a=e._propertyBindings,c=e._interpolants,u=n.uuid,h=this._bindingsByRootAndName;let f=h[u];f===void 0&&(f={},h[u]=f);for(let p=0;p!==s;++p){const m=i[p],g=m.name;let x=f[g];if(x!==void 0)++x.referenceCount,a[p]=x;else{if(x=a[p],x!==void 0){x._cacheIndex===null&&(++x.referenceCount,this._addInactiveBinding(x,u,g));continue}const M=t&&t._propertyBindings[p].binding.parsedPath;x=new eC(Ot.create(n,g,M),m.ValueTypeName,m.getValueSize()),++x.referenceCount,this._addInactiveBinding(x,u,g),a[p]=x}c[p].resultBuffer=x.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){const n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;const e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){const t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){const i=this._actions,s=this._actionsByClip;let a=s[t];if(a===void 0)a={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=a;else{const c=a.knownActions;e._byClipCacheIndex=c.length,c.push(e)}e._cacheIndex=i.length,i.push(e),a.actionByRoot[n]=e}_removeInactiveAction(e){const t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;const s=e._clip.uuid,a=this._actionsByClip,c=a[s],u=c.knownActions,h=u[u.length-1],f=e._byClipCacheIndex;h._byClipCacheIndex=f,u[f]=h,u.pop(),e._byClipCacheIndex=null;const p=c.actionByRoot,m=(e._localRoot||this._root).uuid;delete p[m],u.length===0&&delete a[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){const t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){const t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){const i=this._bindingsByRootAndName,s=this._bindings;let a=i[t];a===void 0&&(a={},i[t]=a),a[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){const t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,a=this._bindingsByRootAndName,c=a[i],u=t[t.length-1],h=e._cacheIndex;u._cacheIndex=h,t[h]=u,t.pop(),delete c[s],Object.keys(c).length===0&&delete a[i]}_lendBinding(e){const t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){const t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){const e=this._controlInterpolants,t=this._nActiveControlInterpolants++;let n=e[t];return n===void 0&&(n=new Yg(new Float32Array(2),new Float32Array(2),1,hC),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){const t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){const i=t||this._root,s=i.uuid;let a=typeof e=="string"?Bc.findByName(i,e):e;const c=a!==null?a.uuid:e,u=this._actionsByClip[c];let h=null;if(n===void 0&&(a!==null?n=a.blendMode:n=_d),u!==void 0){const p=u.actionByRoot[s];if(p!==void 0&&p.blendMode===n)return p;h=u.knownActions[0],a===null&&(a=h._clip)}if(a===null)return null;const f=new uC(this,a,t,n);return this._bindAction(f,h),this._addInactiveAction(f,c,s),f}existingAction(e,t){const n=t||this._root,i=n.uuid,s=typeof e=="string"?Bc.findByName(n,e):e,a=s?s.uuid:e,c=this._actionsByClip[a];return c!==void 0&&c.actionByRoot[i]||null}stopAllAction(){const e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;const t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),a=this._accuIndex^=1;for(let h=0;h!==n;++h)t[h]._update(i,e,s,a);const c=this._bindings,u=this._nActiveBindings;for(let h=0;h!==u;++h)c[h].apply(a);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){const t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){const a=s.knownActions;for(let c=0,u=a.length;c!==u;++c){const h=a[c];this._deactivateAction(h);const f=h._cacheIndex,p=t[t.length-1];h._cacheIndex=null,h._byClipCacheIndex=null,p._cacheIndex=f,t[f]=p,t.pop(),this._removeInactiveBindingsForAction(h)}delete i[n]}}uncacheRoot(e){const t=e.uuid,n=this._actionsByClip;for(const a in n){const c=n[a].actionByRoot,u=c[t];u!==void 0&&(this._deactivateAction(u),this._removeInactiveAction(u))}const i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(const a in s){const c=s[a];c.restoreOriginalState(),this._removeInactiveBinding(c)}}uncacheAction(e,t){const n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}}const Wm=new ot;class Jg{constructor(e,t,n=0,i=1/0){this.ray=new oo(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new yd,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Wm.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Wm),this}intersectObject(e,t=!0,n=[]){return rd(e,this,n,t),n.sort(jm),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)rd(e[i],this,n,t);return n.sort(jm),n}}function jm(r,e){return r.distance-e.distance}function rd(r,e,t,n){let i=!0;if(r.layers.test(e.layers)&&r.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const s=r.children;for(let a=0,c=s.length;a<c;a++)rd(s[a],e,t,!0)}}class Xm{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(wn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const pr=new F,_c=new ot,nh=new ot;class dC extends jg{constructor(e){const t=Qg(e),n=new mn,i=[],s=[],a=new $e(0,0,1),c=new $e(0,1,0);for(let h=0;h<t.length;h++){const f=t[h];f.parent&&f.parent.isBone&&(i.push(0,0,0),i.push(0,0,0),s.push(a.r,a.g,a.b),s.push(c.r,c.g,c.b))}n.setAttribute("position",new Xt(i,3)),n.setAttribute("color",new Xt(s,3));const u=new Gc({vertexColors:!0,depthTest:!1,depthWrite:!1,toneMapped:!1,transparent:!0});super(n,u),this.isSkeletonHelper=!0,this.type="SkeletonHelper",this.root=e,this.bones=t,this.matrix=e.matrixWorld,this.matrixAutoUpdate=!1}updateMatrixWorld(e){const t=this.bones,n=this.geometry,i=n.getAttribute("position");nh.copy(this.root.matrixWorld).invert();for(let s=0,a=0;s<t.length;s++){const c=t[s];c.parent&&c.parent.isBone&&(_c.multiplyMatrices(nh,c.matrixWorld),pr.setFromMatrixPosition(_c),i.setXYZ(a,pr.x,pr.y,pr.z),_c.multiplyMatrices(nh,c.parent.matrixWorld),pr.setFromMatrixPosition(_c),i.setXYZ(a+1,pr.x,pr.y,pr.z),a+=2)}n.getAttribute("position").needsUpdate=!0,super.updateMatrixWorld(e)}dispose(){this.geometry.dispose(),this.material.dispose()}}function Qg(r){const e=[];r.isBone===!0&&e.push(r);for(let t=0;t<r.children.length;t++)e.push.apply(e,Qg(r.children[t]));return e}class e_ extends Tr{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(){}disconnect(){}dispose(){}update(){}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:"170"}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__="170");class t_ extends us{constructor(e){super(e),this.animateBonePositions=!0,this.animateBoneRotations=!0}load(e,t,n,i){const s=this,a=new wd(s.manager);a.setPath(s.path),a.setRequestHeader(s.requestHeader),a.setWithCredentials(s.withCredentials),a.load(e,function(c){try{t(s.parse(c))}catch(u){i?i(u):console.error(u),s.manager.itemError(e)}},n,i)}parse(e){function t(g){c(g)!=="HIERARCHY"&&console.error("THREE.BVHLoader: HIERARCHY expected.");const x=[],M=i(g,c(g),x);c(g)!=="MOTION"&&console.error("THREE.BVHLoader: MOTION expected.");let v=c(g).split(/[\s]+/);const _=parseInt(v[1]);isNaN(_)&&console.error("THREE.BVHLoader: Failed to read number of frames."),v=c(g).split(/[\s]+/);const A=parseFloat(v[2]);isNaN(A)&&console.error("THREE.BVHLoader: Failed to read frame time.");for(let w=0;w<_;w++)v=c(g).split(/[\s]+/),n(v,w*A,M);return x}function n(g,x,M){if(M.type==="ENDSITE")return;const v={time:x,position:new F,rotation:new en};M.frames.push(v);const _=new en,A=new F(1,0,0),w=new F(0,1,0),b=new F(0,0,1);for(let B=0;B<M.channels.length;B++)switch(M.channels[B]){case"Xposition":v.position.x=parseFloat(g.shift().trim());break;case"Yposition":v.position.y=parseFloat(g.shift().trim());break;case"Zposition":v.position.z=parseFloat(g.shift().trim());break;case"Xrotation":_.setFromAxisAngle(A,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Yrotation":_.setFromAxisAngle(w,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Zrotation":_.setFromAxisAngle(b,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;default:console.warn("THREE.BVHLoader: Invalid channel type.")}for(let B=0;B<M.children.length;B++)n(g,x,M.children[B])}function i(g,x,M){const v={name:"",type:"",frames:[]};M.push(v);let _=x.split(/[\s]+/);_[0].toUpperCase()==="END"&&_[1].toUpperCase()==="SITE"?(v.type="ENDSITE",v.name="ENDSITE"):(v.name=_[1],v.type=_[0].toUpperCase()),c(g)!=="{"&&console.error("THREE.BVHLoader: Expected opening { after type & name"),_=c(g).split(/[\s]+/),_[0]!=="OFFSET"&&console.error("THREE.BVHLoader: Expected OFFSET but got: "+_[0]),_.length!==4&&console.error("THREE.BVHLoader: Invalid number of values for OFFSET.");const A=new F(parseFloat(_[1]),parseFloat(_[2]),parseFloat(_[3]));if((isNaN(A.x)||isNaN(A.y)||isNaN(A.z))&&console.error("THREE.BVHLoader: Invalid values of OFFSET."),v.offset=A,v.type!=="ENDSITE"){_=c(g).split(/[\s]+/),_[0]!=="CHANNELS"&&console.error("THREE.BVHLoader: Expected CHANNELS definition.");const w=parseInt(_[1]);v.channels=_.splice(2,w),v.children=[]}for(;;){const w=c(g);if(w==="}")return v;v.children.push(i(g,w,M))}}function s(g,x){const M=new Vc;if(x.push(M),M.position.add(g.offset),M.name=g.name,g.type!=="ENDSITE")for(let v=0;v<g.children.length;v++)M.add(s(g.children[v],x));return M}function a(g){const x=[];for(let M=0;M<g.length;M++){const v=g[M];if(v.type==="ENDSITE")continue;const _=[],A=[],w=[];for(let b=0;b<v.frames.length;b++){const B=v.frames[b];_.push(B.time),A.push(B.position.x+v.offset.x),A.push(B.position.y+v.offset.y),A.push(B.position.z+v.offset.z),w.push(B.rotation.x),w.push(B.rotation.y),w.push(B.rotation.z),w.push(B.rotation.w)}u.animateBonePositions&&x.push(new ls(v.name+".position",_,A)),u.animateBoneRotations&&x.push(new cs(v.name+".quaternion",_,w))}return new Bc("animation",-1,x)}function c(g){let x;for(;(x=g.shift().trim()).length===0;);return x}const u=this,h=e.split(/[\r\n]+/g),f=t(h),p=[];s(f[0],p);const m=a(f);return{skeleton:new ia(p),clip:m}}}var Ei=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},ih={},qm;function fn(){return qm||(qm=1,(function(r){var e=Object.defineProperty,t=Object.defineProperties,n=Object.getOwnPropertyDescriptors,i=Object.getOwnPropertySymbols,s=Object.prototype.hasOwnProperty,a=Object.prototype.propertyIsEnumerable,c=(S,D,G)=>D in S?e(S,D,{enumerable:!0,configurable:!0,writable:!0,value:G}):S[D]=G,u=(S,D)=>{for(var G in D||(D={}))s.call(D,G)&&c(S,G,D[G]);if(i)for(var G of i(D))a.call(D,G)&&c(S,G,D[G]);return S},h=(S,D)=>t(S,n(D)),f=S=>e(S,"__esModule",{value:!0}),p=(S,D)=>{f(S);for(var G in D)e(S,G,{get:D[G],enumerable:!0})};p(r,{Atom:()=>Ma,PointerProxy:()=>Ll,Ticker:()=>Ea,getPointerParts:()=>Pr,isPointer:()=>Di,isPrism:()=>_s,iterateAndCountTicks:()=>Rl,iterateOver:()=>Il,pointer:()=>mo,pointerToPrism:()=>ys,prism:()=>Lr,val:()=>bo});var m=Array.isArray,g=m,x=typeof Ei=="object"&&Ei&&Ei.Object===Object&&Ei,M=x,v=typeof self=="object"&&self&&self.Object===Object&&self,_=M||v||Function("return this")(),A=_,w=A.Symbol,b=w,B=Object.prototype,U=B.hasOwnProperty,O=B.toString,H=b?b.toStringTag:void 0;function L(S){var D=U.call(S,H),G=S[H];try{S[H]=void 0;var se=!0}catch{}var et=O.call(S);return se&&(D?S[H]=G:delete S[H]),et}var P=L,V=Object.prototype,ee=V.toString;function Q(S){return ee.call(S)}var ae=Q,ce="[object Null]",J="[object Undefined]",de=b?b.toStringTag:void 0;function re(S){return S==null?S===void 0?J:ce:de&&de in Object(S)?P(S):ae(S)}var _e=re;function Me(S){return S!=null&&typeof S=="object"}var Ue=Me,Je="[object Symbol]";function pt(S){return typeof S=="symbol"||Ue(S)&&_e(S)==Je}var le=pt,pe=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Fe=/^\w*$/;function Se(S,D){if(g(S))return!1;var G=typeof S;return G=="number"||G=="symbol"||G=="boolean"||S==null||le(S)?!0:Fe.test(S)||!pe.test(S)||D!=null&&S in Object(D)}var qe=Se;function it(S){var D=typeof S;return S!=null&&(D=="object"||D=="function")}var at=it,Pt="[object AsyncFunction]",lt="[object Function]",zt="[object GeneratorFunction]",X="[object Proxy]";function rn(S){if(!at(S))return!1;var D=_e(S);return D==lt||D==zt||D==Pt||D==X}var ut=rn,mt=A["__core-js_shared__"],We=mt,Tt=(function(){var S=/[^.]+$/.exec(We&&We.keys&&We.keys.IE_PROTO||"");return S?"Symbol(src)_1."+S:""})();function ke(S){return!!Tt&&Tt in S}var N=ke,E=Function.prototype,Z=E.toString;function ue(S){if(S!=null){try{return Z.call(S)}catch{}try{return S+""}catch{}}return""}var fe=ue,he=/[\\^$.*+?()[\]{}|]/g,Oe=/^\[object .+?Constructor\]$/,Ae=Function.prototype,Le=Object.prototype,ht=Ae.toString,me=Le.hasOwnProperty,De=RegExp("^"+ht.call(me).replace(he,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Be(S){if(!at(S)||N(S))return!1;var D=ut(S)?De:Oe;return D.test(fe(S))}var Ze=Be;function Ne(S,D){return S==null?void 0:S[D]}var _t=Ne;function st(S,D){var G=_t(S,D);return Ze(G)?G:void 0}var Ct=st,W=Ct(Object,"create"),Te=W;function R(){this.__data__=Te?Te(null):{},this.size=0}var z=R;function K(S){var D=this.has(S)&&delete this.__data__[S];return this.size-=D?1:0,D}var ie=K,ye="__lodash_hash_undefined__",xe=Object.prototype,we=xe.hasOwnProperty;function Ie(S){var D=this.__data__;if(Te){var G=D[S];return G===ye?void 0:G}return we.call(D,S)?D[S]:void 0}var nt=Ie,Et=Object.prototype,qt=Et.hasOwnProperty;function Ke(S){var D=this.__data__;return Te?D[S]!==void 0:qt.call(D,S)}var ct=Ke,Gt="__lodash_hash_undefined__";function Rt(S,D){var G=this.__data__;return this.size+=this.has(S)?0:1,G[S]=Te&&D===void 0?Gt:D,this}var Xe=Rt;function yt(S){var D=-1,G=S==null?0:S.length;for(this.clear();++D<G;){var se=S[D];this.set(se[0],se[1])}}yt.prototype.clear=z,yt.prototype.delete=ie,yt.prototype.get=nt,yt.prototype.has=ct,yt.prototype.set=Xe;var On=yt;function tr(){this.__data__=[],this.size=0}var hs=tr;function ri(S,D){return S===D||S!==S&&D!==D}var ho=ri;function Ci(S,D){for(var G=S.length;G--;)if(ho(S[G][0],D))return G;return-1}var nr=Ci,C=Array.prototype,j=C.splice;function te(S){var D=this.__data__,G=nr(D,S);if(G<0)return!1;var se=D.length-1;return G==se?D.pop():j.call(D,G,1),--this.size,!0}var ne=te;function q(S){var D=this.__data__,G=nr(D,S);return G<0?void 0:D[G][1]}var be=q;function Ce(S){return nr(this.__data__,S)>-1}var He=Ce;function Ve(S,D){var G=this.__data__,se=nr(G,S);return se<0?(++this.size,G.push([S,D])):G[se][1]=D,this}var rt=Ve;function Qe(S){var D=-1,G=S==null?0:S.length;for(this.clear();++D<G;){var se=S[D];this.set(se[0],se[1])}}Qe.prototype.clear=hs,Qe.prototype.delete=ne,Qe.prototype.get=be,Qe.prototype.has=He,Qe.prototype.set=rt;var Ge=Qe,Mt=Ct(A,"Map"),Nt=Mt;function Ut(){this.size=0,this.__data__={hash:new On,map:new(Nt||Ge),string:new On}}var nn=Ut;function At(S){var D=typeof S;return D=="string"||D=="number"||D=="symbol"||D=="boolean"?S!=="__proto__":S===null}var je=At;function Yn(S,D){var G=S.__data__;return je(D)?G[typeof D=="string"?"string":"hash"]:G.map}var bt=Yn;function Mn(S){var D=bt(this,S).delete(S);return this.size-=D?1:0,D}var bi=Mn;function cn(S){return bt(this,S).get(S)}var Ii=cn;function Ft(S){return bt(this,S).has(S)}var Vn=Ft;function Li(S,D){var G=bt(this,S),se=G.size;return G.set(S,D),this.size+=G.size==se?0:1,this}var Pn=Li;function Tn(S){var D=-1,G=S==null?0:S.length;for(this.clear();++D<G;){var se=S[D];this.set(se[0],se[1])}}Tn.prototype.clear=nn,Tn.prototype.delete=bi,Tn.prototype.get=Ii,Tn.prototype.has=Vn,Tn.prototype.set=Pn;var Kn=Tn,ds="Expected a function";function fo(S,D){if(typeof S!="function"||D!=null&&typeof D!="function")throw new TypeError(ds);var G=function(){var se=arguments,et=D?D.apply(this,se):se[0],It=G.cache;if(It.has(et))return It.get(et);var En=S.apply(this,se);return G.cache=It.set(et,En)||It,En};return G.cache=new(fo.Cache||Kn),G}fo.Cache=Kn;var jc=fo,ir=500;function fs(S){var D=jc(S,function(se){return G.size===ir&&G.clear(),se}),G=D.cache;return D}var Xc=fs,Er=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,qc=/\\(\\)?/g,Yc=Xc(function(S){var D=[];return S.charCodeAt(0)===46&&D.push(""),S.replace(Er,function(G,se,et,It){D.push(et?It.replace(qc,"$1"):se||G)}),D}),Kc=Yc;function $c(S,D){for(var G=-1,se=S==null?0:S.length,et=Array(se);++G<se;)et[G]=D(S[G],G,S);return et}var Zc=$c,Ar=b?b.prototype:void 0,oa=Ar?Ar.toString:void 0;function aa(S){if(typeof S=="string")return S;if(g(S))return Zc(S,aa)+"";if(le(S))return oa?oa.call(S):"";var D=S+"";return D=="0"&&1/S==-1/0?"-0":D}var Jc=aa;function Qc(S){return S==null?"":Jc(S)}var el=Qc;function tl(S,D){return g(S)?S:qe(S,D)?[S]:Kc(el(S))}var nl=tl;function il(S){if(typeof S=="string"||le(S))return S;var D=S+"";return D=="0"&&1/S==-1/0?"-0":D}var rr=il;function ps(S,D){D=nl(D,S);for(var G=0,se=D.length;S!=null&&G<se;)S=S[rr(D[G++])];return G&&G==se?S:void 0}var rl=ps;function po(S,D,G){var se=S==null?void 0:rl(S,D);return se===void 0?G:se}var sl=po;function ol(S,D){return function(G){return S(D(G))}}var al=ol,cl=al(Object.getPrototypeOf,Object),ll=cl,ul="[object Object]",hl=Function.prototype,dl=Object.prototype,ca=hl.toString,fl=dl.hasOwnProperty,la=ca.call(Object);function ua(S){if(!Ue(S)||_e(S)!=ul)return!1;var D=ll(S);if(D===null)return!0;var G=fl.call(D,"constructor")&&D.constructor;return typeof G=="function"&&G instanceof G&&ca.call(G)==la}var ha=ua;function da(S){var D=S==null?0:S.length;return D?S[D-1]:void 0}var pl=da,ms=new WeakMap,fa=new WeakMap,wr=Symbol("pointerMeta"),ml={get(S,D){if(D===wr)return ms.get(S);let G=fa.get(S);G||(G=new Map,fa.set(S,G));const se=G.get(D);if(se!==void 0)return se;const et=ms.get(S),It=gs({root:et.root,path:[...et.path,D]});return G.set(D,It),It}},hi=S=>S[wr],Pr=S=>{const{root:D,path:G}=hi(S);return{root:D,path:G}};function gs(S){var D;const G={root:S.root,path:(D=S.path)!=null?D:[]},se={};return ms.set(se,G),new Proxy(se,ml)}var mo=gs,Di=S=>S&&!!hi(S);function pa(S,D,G){return D.length===0?G(S):sr(S,D,G)}var sr=(S,D,G)=>{if(D.length===0)return G(S);if(Array.isArray(S)){let[se,...et]=D;se=parseInt(String(se),10),isNaN(se)&&(se=0);const It=S[se],En=sr(It,et,G);if(It===En)return S;const si=[...S];return si.splice(se,1,En),si}else if(typeof S=="object"&&S!==null){const[se,...et]=D,It=S[se],En=sr(It,et,G);return It===En?S:h(u({},S),{[se]:En})}else{const[se,...et]=D;return{[se]:sr(void 0,et,G)}}},hn=class{constructor(){this._head=void 0}peek(){return this._head&&this._head.data}pop(){const S=this._head;if(S)return this._head=S.next,S.data}push(S){const D={next:this._head,data:S};this._head=D}};function _s(S){return!!(S&&S.isPrism&&S.isPrism===!0)}function go(){const S=()=>{},D=new hn,G=S;return{type:"Dataverse_discoveryMechanism",startIgnoringDependencies:()=>{D.push(G)},stopIgnoringDependencies:()=>{D.peek()!==G||D.pop()},reportResolutionStart:or=>{const Dr=D.peek();Dr&&Dr(or),D.push(G)},reportResolutionEnd:or=>{D.pop()},pushCollector:or=>{D.push(or)},popCollector:or=>{if(D.peek()!==or)throw new Error("Popped collector is not on top of the stack");D.pop()}}}function gl(){const S="__dataverse_discoveryMechanism_sharedStack",D=typeof window<"u"?window:typeof Ei<"u"?Ei:{};if(D){const G=D[S];if(G&&typeof G=="object"&&G.type==="Dataverse_discoveryMechanism")return G;{const se=go();return D[S]=se,se}}else return go()}var{startIgnoringDependencies:Ni,stopIgnoringDependencies:Rr,reportResolutionEnd:_l,reportResolutionStart:vl,pushCollector:_o,popCollector:yl}=gl(),ma=()=>{},xl=class{constructor(S,D){this._fn=S,this._prismInstance=D,this._didMarkDependentsAsStale=!1,this._isFresh=!1,this._cacheOfDendencyValues=new Map,this._dependents=new Set,this._dependencies=new Set,this._possiblyStaleDeps=new Set,this._scope=new ga(this),this._lastValue=void 0,this._forciblySetToStale=!1,this._reactToDependencyGoingStale=G=>{this._possiblyStaleDeps.add(G),this._markAsStale()};for(const G of this._dependencies)G._addDependent(this._reactToDependencyGoingStale);Ni(),this.getValue(),Rr()}get hasDependents(){return this._dependents.size>0}removeDependent(S){this._dependents.delete(S)}addDependent(S){this._dependents.add(S)}destroy(){for(const S of this._dependencies)S._removeDependent(this._reactToDependencyGoingStale);_a(this._scope)}getValue(){if(!this._isFresh){const S=this._recalculate();this._lastValue=S,this._isFresh=!0,this._didMarkDependentsAsStale=!1,this._forciblySetToStale=!1}return this._lastValue}_recalculate(){let S;if(!this._forciblySetToStale&&this._possiblyStaleDeps.size>0){let se=!1;Ni();for(const et of this._possiblyStaleDeps)if(this._cacheOfDendencyValues.get(et)!==et.getValue()){se=!0;break}if(Rr(),this._possiblyStaleDeps.clear(),!se)return this._lastValue}const D=new Set;this._cacheOfDendencyValues.clear();const G=se=>{D.add(se),this._addDependency(se)};_o(G),vn.push(this._scope);try{S=this._fn()}catch(se){console.error(se)}finally{vn.pop()!==this._scope&&console.warn("The Prism hook stack has slipped. This is a bug.")}yl(G);for(const se of this._dependencies)D.has(se)||this._removeDependency(se);this._dependencies=D,Ni();for(const se of D)this._cacheOfDendencyValues.set(se,se.getValue());return Rr(),S}forceStale(){this._forciblySetToStale=!0,this._markAsStale()}_markAsStale(){if(!this._didMarkDependentsAsStale){this._didMarkDependentsAsStale=!0,this._isFresh=!1;for(const S of this._dependents)S(this._prismInstance)}}_addDependency(S){this._dependencies.has(S)||(this._dependencies.add(S),S._addDependent(this._reactToDependencyGoingStale))}_removeDependency(S){this._dependencies.has(S)&&(this._dependencies.delete(S),S._removeDependent(this._reactToDependencyGoingStale))}},vo={},bl=class{constructor(S){this._fn=S,this.isPrism=!0,this._state={hot:!1,handle:void 0}}get isHot(){return this._state.hot}onChange(S,D,G=!1){const se=()=>{S.onThisOrNextTick(It)};let et=vo;const It=()=>{const si=this.getValue();si!==et&&(et=si,D(si))};return this._addDependent(se),G&&(et=this.getValue(),D(et)),()=>{this._removeDependent(se),S.offThisOrNextTick(It),S.offNextTick(It)}}onStale(S){const D=()=>{this._removeDependent(G)},G=()=>S();return this._addDependent(G),D}keepHot(){return this.onStale(()=>{})}_addDependent(S){this._state.hot||this._goHot(),this._state.handle.addDependent(S)}_goHot(){const S=new xl(this._fn,this);this._state={hot:!0,handle:S}}_removeDependent(S){const D=this._state;if(!D.hot)return;const G=D.handle;G.removeDependent(S),G.hasDependents||(this._state={hot:!1,handle:void 0},G.destroy())}getValue(){vl(this);const S=this._state;let D;return S.hot?D=S.handle.getValue():D=Ir(this._fn),_l(this),D}},ga=class{constructor(S){this._hotHandle=S,this._refs=new Map,this.isPrismScope=!0,this.subs={},this.effects=new Map,this.memos=new Map}ref(S,D){let G=this._refs.get(S);if(G!==void 0)return G;{const se={current:D};return this._refs.set(S,se),se}}effect(S,D,G){let se=this.effects.get(S);se===void 0&&(se={cleanup:ma,deps:void 0},this.effects.set(S,se)),va(se.deps,G)&&(se.cleanup(),Ni(),se.cleanup=vs(D,ma).value,Rr(),se.deps=G)}memo(S,D,G){let se=this.memos.get(S);return se===void 0&&(se={cachedValue:null,deps:void 0},this.memos.set(S,se)),va(se.deps,G)&&(Ni(),se.cachedValue=vs(D,void 0).value,Rr(),se.deps=G),se.cachedValue}state(S,D){const{value:G,setValue:se}=this.memo("state/"+S,()=>{const et={current:D};return{value:et,setValue:En=>{et.current=En,this._hotHandle.forceStale()}}},[]);return[G.current,se]}sub(S){return this.subs[S]||(this.subs[S]=new ga(this._hotHandle)),this.subs[S]}cleanupEffects(){for(const S of this.effects.values())vs(S.cleanup,void 0);this.effects.clear()}source(S,D){return this.effect("$$source/blah",()=>S(()=>{this._hotHandle.forceStale()}),[S]),D()}};function _a(S){for(const D of Object.values(S.subs))_a(D);S.cleanupEffects()}function vs(S,D){try{return{value:S(),ok:!0}}catch(G){return setTimeout(function(){throw G}),{value:D,ok:!1}}}var vn=new hn;function Sl(S,D){const G=vn.peek();if(!G)throw new Error("prism.ref() is called outside of a prism() call.");return G.ref(S,D)}function yo(S,D,G){const se=vn.peek();if(!se)throw new Error("prism.effect() is called outside of a prism() call.");return se.effect(S,D,G)}function va(S,D){if(S===void 0||D===void 0)return!0;const G=S.length;if(G!==D.length)return!0;for(let se=0;se<G;se++)if(S[se]!==D[se])return!0;return!1}function ya(S,D,G){const se=vn.peek();if(!se)throw new Error("prism.memo() is called outside of a prism() call.");return se.memo(S,D,G)}function Un(S,D){const G=vn.peek();if(!G)throw new Error("prism.state() is called outside of a prism() call.");return G.state(S,D)}function Ml(){if(!vn.peek())throw new Error("The parent function is called outside of a prism() call.")}function Tl(S,D){const G=vn.peek();if(!G)throw new Error("prism.scope() is called outside of a prism() call.");const se=G.sub(S);vn.push(se);const et=vs(D,void 0).value;return vn.pop(),et}function El(S,D,G){return ya(S,()=>dn(D),G).getValue()}function xa(){return!!vn.peek()}function Al(S,D){const G=vn.peek();if(!G)throw new Error("prism.source() is called outside of a prism() call.");return G.source(S,D)}var dn=S=>new bl(S),Cr=class{effect(S,D,G){console.warn("prism.effect() does not run in cold prisms")}memo(S,D,G){return D()}state(S,D){return[D,()=>{}]}ref(S,D){return{current:D}}sub(S){return new Cr}source(S,D){return D()}};function Ir(S){const D=new Cr;vn.push(D);let G;try{G=S()}catch(se){console.error(se)}finally{vn.pop()!==D&&console.warn("The Prism hook stack has slipped. This is a bug.")}return G}dn.ref=Sl,dn.effect=yo,dn.memo=ya,dn.ensurePrism=Ml,dn.state=Un,dn.scope=Tl,dn.sub=El,dn.inPrism=xa,dn.source=Al;var Lr=dn,ba;(function(S){S[S.Dict=0]="Dict",S[S.Array=1]="Array",S[S.Other=2]="Other"})(ba||(ba={}));var Bt=S=>Array.isArray(S)?1:ha(S)?0:2,xo=(S,D,G=Bt(S))=>G===0&&typeof D=="string"||G===1&&wl(D)?S[D]:void 0,wl=S=>{const D=typeof S=="number"?S:parseInt(S,10);return!isNaN(D)&&D>=0&&D<1/0&&(D|0)===D},Sa=class{constructor(S,D){this._parent=S,this._path=D,this.children=new Map,this.identityChangeListeners=new Set}addIdentityChangeListener(S){this.identityChangeListeners.add(S)}removeIdentityChangeListener(S){this.identityChangeListeners.delete(S),this._checkForGC()}removeChild(S){this.children.delete(S),this._checkForGC()}getChild(S){return this.children.get(S)}getOrCreateChild(S){let D=this.children.get(S);return D||(D=D=new Sa(this,this._path.concat([S])),this.children.set(S,D)),D}_checkForGC(){this.identityChangeListeners.size>0||this.children.size>0||this._parent&&this._parent.removeChild(pl(this._path))}},Ma=class{constructor(S){this.$$isPointerToPrismProvider=!0,this.pointer=mo({root:this,path:[]}),this.prism=this.pointerToPrism(this.pointer),this._onPointerValueChange=(D,G)=>{const{path:se}=Pr(D),et=this._getOrCreateScopeForPath(se);return et.identityChangeListeners.add(G),()=>{et.identityChangeListeners.delete(G)}},this._currentState=S,this._rootScope=new Sa(void 0,[])}set(S){const D=this._currentState;this._currentState=S,this._checkUpdates(this._rootScope,D,S)}get(){return this._currentState}getByPointer(S){const D=Di(S)?S:S(this.pointer),G=Pr(D).path;return this._getIn(G)}_getIn(S){return S.length===0?this.get():sl(this.get(),S)}reduce(S){this.set(S(this.get()))}reduceByPointer(S,D){const G=Di(S)?S:S(this.pointer),se=Pr(G).path,et=pa(this.get(),se,D);this.set(et)}setByPointer(S,D){this.reduceByPointer(S,()=>D)}_checkUpdates(S,D,G){if(D===G)return;for(const It of S.identityChangeListeners)It(G);if(S.children.size===0)return;const se=Bt(D),et=Bt(G);if(!(se===2&&se===et))for(const[It,En]of S.children){const si=xo(D,It,se),Aa=xo(G,It,et);this._checkUpdates(En,si,Aa)}}_getOrCreateScopeForPath(S){let D=this._rootScope;for(const G of S)D=D.getOrCreateChild(G);return D}pointerToPrism(S){const{path:D}=Pr(S),G=et=>this._onPointerValueChange(S,et),se=()=>this._getIn(D);return Lr(()=>Lr.source(G,se))}},Ta=new WeakMap;function Pl(S){return typeof S=="object"&&S!==null&&S.$$isPointerToPrismProvider===!0}var ys=S=>{const D=hi(S);let G=Ta.get(D);if(!G){const se=D.root;if(!Pl(se))throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");G=se.pointerToPrism(S),Ta.set(D,G)}return G},bo=S=>Di(S)?ys(S).getValue():_s(S)?S.getValue():S;function*Rl(S){let D;if(Di(S))D=ys(S);else if(_s(S))D=S;else throw new Error("Only pointers and prisms are supported");let G=0;const se=D.onStale(()=>{G++});try{for(;;){const et=G;G=0,yield{value:D.getValue(),ticks:et}}}finally{se()}}var Cl=180,Ea=class{constructor(S){this._conf=S,this._ticking=!1,this._dormant=!0,this._numberOfDormantTicks=0,this.__ticks=0,this._scheduledForThisOrNextTick=new Set,this._scheduledForNextTick=new Set,this._timeAtCurrentTick=0}get dormant(){return this._dormant}onThisOrNextTick(S){this._scheduledForThisOrNextTick.add(S),this._dormant&&this._goActive()}onNextTick(S){this._scheduledForNextTick.add(S),this._dormant&&this._goActive()}offThisOrNextTick(S){this._scheduledForThisOrNextTick.delete(S)}offNextTick(S){this._scheduledForNextTick.delete(S)}get time(){return this._ticking?this._timeAtCurrentTick:performance.now()}_goActive(){var S,D;this._dormant&&(this._dormant=!1,(D=(S=this._conf)==null?void 0:S.onActive)==null||D.call(S))}_goDormant(){var S,D;this._dormant||(this._dormant=!0,this._numberOfDormantTicks=0,(D=(S=this._conf)==null?void 0:S.onDormant)==null||D.call(S))}tick(S=performance.now()){if(this.__ticks++,!this._dormant&&this._scheduledForNextTick.size===0&&this._scheduledForThisOrNextTick.size===0&&(this._numberOfDormantTicks++,this._numberOfDormantTicks>=Cl)){this._goDormant();return}this._ticking=!0,this._timeAtCurrentTick=S;for(const D of this._scheduledForNextTick)this._scheduledForThisOrNextTick.add(D);this._scheduledForNextTick.clear(),this._tick(0),this._ticking=!1}_tick(S){const D=this.time;if(S>10&&console.warn("_tick() recursing for 10 times"),S>100)throw new Error("Maximum recursion limit for _tick()");const G=this._scheduledForThisOrNextTick;this._scheduledForThisOrNextTick=new Set;for(const se of G)se(D);if(this._scheduledForThisOrNextTick.size>0)return this._tick(S+1)}};function*Il(S){let D;if(Di(S))D=ys(S);else if(_s(S))D=S;else throw new Error("Only pointers and prisms are supported");const G=new Ea,se=D.onChange(G,et=>{});try{for(;;)G.tick(),yield D.getValue()}finally{se()}}var Ll=class{constructor(S){this.$$isPointerToPrismProvider=!0,this._currentPointerBox=new Ma(S),this.pointer=mo({root:this,path:[]})}setPointer(S){this._currentPointerBox.set(S)}pointerToPrism(S){const{path:D}=hi(S);return Lr(()=>{const G=this._currentPointerBox.prism.getValue(),se=D.reduce((et,It)=>et[It],G);return bo(se)})}}})(ih)),ih}const Ym={type:"change"},Id={type:"start"},n_={type:"end"},vc=new oo,Km=new _r,fC=Math.cos(70*wg.DEG2RAD),pn=new F,jn=2*Math.PI,Vt={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},rh=1e-6;class pC extends e_{constructor(e,t=null){super(e,t),this.state=Vt.NONE,this.enabled=!0,this.target=new F,this.cursor=new F,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:js.ROTATE,MIDDLE:js.DOLLY,RIGHT:js.PAN},this.touches={ONE:zs.ROTATE,TWO:zs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new F,this._lastQuaternion=new en,this._lastTargetPosition=new F,this._quat=new en().setFromUnitVectors(e.up,new F(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new Xm,this._sphericalDelta=new Xm,this._scale=1,this._panOffset=new F,this._rotateStart=new tt,this._rotateEnd=new tt,this._rotateDelta=new tt,this._panStart=new tt,this._panEnd=new tt,this._panDelta=new tt,this._dollyStart=new tt,this._dollyEnd=new tt,this._dollyDelta=new tt,this._dollyDirection=new F,this._mouse=new tt,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=gC.bind(this),this._onPointerDown=mC.bind(this),this._onPointerUp=_C.bind(this),this._onContextMenu=TC.bind(this),this._onMouseWheel=xC.bind(this),this._onKeyDown=bC.bind(this),this._onTouchStart=SC.bind(this),this._onTouchMove=MC.bind(this),this._onMouseDown=vC.bind(this),this._onMouseMove=yC.bind(this),this._interceptControlDown=EC.bind(this),this._interceptControlUp=AC.bind(this),this.domElement!==null&&this.connect(),this.update()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Ym),this.update(),this.state=Vt.NONE}update(e=null){const t=this.object.position;pn.copy(t).sub(this.target),pn.applyQuaternion(this._quat),this._spherical.setFromVector3(pn),this.autoRotate&&this.state===Vt.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,i=this.maxAzimuthAngle;isFinite(n)&&isFinite(i)&&(n<-Math.PI?n+=jn:n>Math.PI&&(n-=jn),i<-Math.PI?i+=jn:i>Math.PI&&(i-=jn),n<=i?this._spherical.theta=Math.max(n,Math.min(i,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+i)/2?Math.max(n,this._spherical.theta):Math.min(i,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const a=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=a!=this._spherical.radius}if(pn.setFromSpherical(this._spherical),pn.applyQuaternion(this._quatInverse),t.copy(this.target).add(pn),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let a=null;if(this.object.isPerspectiveCamera){const c=pn.length();a=this._clampDistance(c*this._scale);const u=c-a;this.object.position.addScaledVector(this._dollyDirection,u),this.object.updateMatrixWorld(),s=!!u}else if(this.object.isOrthographicCamera){const c=new F(this._mouse.x,this._mouse.y,0);c.unproject(this.object);const u=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=u!==this.object.zoom;const h=new F(this._mouse.x,this._mouse.y,0);h.unproject(this.object),this.object.position.sub(h).add(c),this.object.updateMatrixWorld(),a=pn.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;a!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(a).add(this.object.position):(vc.origin.copy(this.object.position),vc.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(vc.direction))<fC?this.object.lookAt(this.target):(Km.setFromNormalAndCoplanarPoint(this.object.up,this.target),vc.intersectPlane(Km,this.target))))}else if(this.object.isOrthographicCamera){const a=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),a!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>rh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>rh||this._lastTargetPosition.distanceToSquared(this.target)>rh?(this.dispatchEvent(Ym),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?jn/60*this.autoRotateSpeed*e:jn/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){pn.setFromMatrixColumn(t,0),pn.multiplyScalar(-e),this._panOffset.add(pn)}_panUp(e,t){this.screenSpacePanning===!0?pn.setFromMatrixColumn(t,1):(pn.setFromMatrixColumn(t,0),pn.crossVectors(this.object.up,pn)),pn.multiplyScalar(e),this._panOffset.add(pn)}_pan(e,t){const n=this.domElement;if(this.object.isPerspectiveCamera){const i=this.object.position;pn.copy(i).sub(this.target);let s=pn.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/n.clientHeight,this.object.matrix),this._panUp(2*t*s/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const n=this.domElement.getBoundingClientRect(),i=e-n.left,s=t-n.top,a=n.width,c=n.height;this._mouse.x=i/a*2-1,this._mouse.y=-(s/c)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(jn*this._rotateDelta.x/t.clientHeight),this._rotateUp(jn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(jn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(-jn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(jn*this.rotateSpeed/this.domElement.clientHeight):this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(-jn*this.rotateSpeed/this.domElement.clientHeight):this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._rotateStart.set(n,i)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panStart.set(n,i)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const n=this._getSecondPointerPosition(e),i=.5*(e.pageX+n.x),s=.5*(e.pageY+n.y);this._rotateEnd.set(i,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(jn*this._rotateDelta.x/t.clientHeight),this._rotateUp(jn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panEnd.set(n,i)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const a=(e.pageX+t.x)*.5,c=(e.pageY+t.y)*.5;this._updateZoomParameters(a,c)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new tt,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}}function mC(r){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(r)&&(this._addPointer(r),r.pointerType==="touch"?this._onTouchStart(r):this._onMouseDown(r)))}function gC(r){this.enabled!==!1&&(r.pointerType==="touch"?this._onTouchMove(r):this._onMouseMove(r))}function _C(r){switch(this._removePointer(r),this._pointers.length){case 0:this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(n_),this.state=Vt.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function vC(r){let e;switch(r.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case js.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(r),this.state=Vt.DOLLY;break;case js.ROTATE:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Vt.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Vt.ROTATE}break;case js.PAN:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Vt.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Vt.PAN}break;default:this.state=Vt.NONE}this.state!==Vt.NONE&&this.dispatchEvent(Id)}function yC(r){switch(this.state){case Vt.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(r);break;case Vt.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(r);break;case Vt.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(r);break}}function xC(r){this.enabled===!1||this.enableZoom===!1||this.state!==Vt.NONE||(r.preventDefault(),this.dispatchEvent(Id),this._handleMouseWheel(this._customWheelEvent(r)),this.dispatchEvent(n_))}function bC(r){this.enabled===!1||this.enablePan===!1||this._handleKeyDown(r)}function SC(r){switch(this._trackPointer(r),this._pointers.length){case 1:switch(this.touches.ONE){case zs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(r),this.state=Vt.TOUCH_ROTATE;break;case zs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(r),this.state=Vt.TOUCH_PAN;break;default:this.state=Vt.NONE}break;case 2:switch(this.touches.TWO){case zs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(r),this.state=Vt.TOUCH_DOLLY_PAN;break;case zs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(r),this.state=Vt.TOUCH_DOLLY_ROTATE;break;default:this.state=Vt.NONE}break;default:this.state=Vt.NONE}this.state!==Vt.NONE&&this.dispatchEvent(Id)}function MC(r){switch(this._trackPointer(r),this.state){case Vt.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(r),this.update();break;case Vt.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(r),this.update();break;case Vt.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(r),this.update();break;case Vt.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(r),this.update();break;default:this.state=Vt.NONE}}function TC(r){this.enabled!==!1&&r.preventDefault()}function EC(r){r.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function AC(r){r.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}const Jr=new Jg,Nn=new F,mr=new F,tn=new en,$m={X:new F(1,0,0),Y:new F(0,1,0),Z:new F(0,0,1)},sh={type:"change"},Zm={type:"mouseDown",mode:null},Jm={type:"mouseUp",mode:null},Qm={type:"objectChange"};class wC extends e_{constructor(e,t=null){super(void 0,t);const n=new DC(this);this._root=n;const i=new NC;this._gizmo=i,n.add(i);const s=new OC;this._plane=s,n.add(s);const a=this;function c(w,b){let B=b;Object.defineProperty(a,w,{get:function(){return B!==void 0?B:b},set:function(U){B!==U&&(B=U,s[w]=U,i[w]=U,a.dispatchEvent({type:w+"-changed",value:U}),a.dispatchEvent(sh))}}),a[w]=b,s[w]=b,i[w]=b}c("camera",e),c("object",void 0),c("enabled",!0),c("axis",null),c("mode","translate"),c("translationSnap",null),c("rotationSnap",null),c("scaleSnap",null),c("space","world"),c("size",1),c("dragging",!1),c("showX",!0),c("showY",!0),c("showZ",!0),c("minX",-1/0),c("maxX",1/0),c("minY",-1/0),c("maxY",1/0),c("minZ",-1/0),c("maxZ",1/0);const u=new F,h=new F,f=new en,p=new en,m=new F,g=new en,x=new F,M=new F,v=new F,_=0,A=new F;c("worldPosition",u),c("worldPositionStart",h),c("worldQuaternion",f),c("worldQuaternionStart",p),c("cameraPosition",m),c("cameraQuaternion",g),c("pointStart",x),c("pointEnd",M),c("rotationAxis",v),c("rotationAngle",_),c("eye",A),this._offset=new F,this._startNorm=new F,this._endNorm=new F,this._cameraScale=new F,this._parentPosition=new F,this._parentQuaternion=new en,this._parentQuaternionInv=new en,this._parentScale=new F,this._worldScaleStart=new F,this._worldQuaternionInv=new en,this._worldScale=new F,this._positionStart=new F,this._quaternionStart=new en,this._scaleStart=new F,this._getPointer=PC.bind(this),this._onPointerDown=CC.bind(this),this._onPointerHover=RC.bind(this),this._onPointerMove=IC.bind(this),this._onPointerUp=LC.bind(this),t!==null&&this.connect()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointermove",this._onPointerHover),this.domElement.addEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerHover),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="auto"}getHelper(){return this._root}pointerHover(e){if(this.object===void 0||this.dragging===!0)return;e!==null&&Jr.setFromCamera(e,this.camera);const t=oh(this._gizmo.picker[this.mode],Jr);t?this.axis=t.object.name:this.axis=null}pointerDown(e){if(!(this.object===void 0||this.dragging===!0||e!=null&&e.button!==0)&&this.axis!==null){e!==null&&Jr.setFromCamera(e,this.camera);const t=oh(this._plane,Jr,!0);t&&(this.object.updateMatrixWorld(),this.object.parent.updateMatrixWorld(),this._positionStart.copy(this.object.position),this._quaternionStart.copy(this.object.quaternion),this._scaleStart.copy(this.object.scale),this.object.matrixWorld.decompose(this.worldPositionStart,this.worldQuaternionStart,this._worldScaleStart),this.pointStart.copy(t.point).sub(this.worldPositionStart)),this.dragging=!0,Zm.mode=this.mode,this.dispatchEvent(Zm)}}pointerMove(e){const t=this.axis,n=this.mode,i=this.object;let s=this.space;if(n==="scale"?s="local":(t==="E"||t==="XYZE"||t==="XYZ")&&(s="world"),i===void 0||t===null||this.dragging===!1||e!==null&&e.button!==-1)return;e!==null&&Jr.setFromCamera(e,this.camera);const a=oh(this._plane,Jr,!0);if(a){if(this.pointEnd.copy(a.point).sub(this.worldPositionStart),n==="translate")this._offset.copy(this.pointEnd).sub(this.pointStart),s==="local"&&t!=="XYZ"&&this._offset.applyQuaternion(this._worldQuaternionInv),t.indexOf("X")===-1&&(this._offset.x=0),t.indexOf("Y")===-1&&(this._offset.y=0),t.indexOf("Z")===-1&&(this._offset.z=0),s==="local"&&t!=="XYZ"?this._offset.applyQuaternion(this._quaternionStart).divide(this._parentScale):this._offset.applyQuaternion(this._parentQuaternionInv).divide(this._parentScale),i.position.copy(this._offset).add(this._positionStart),this.translationSnap&&(s==="local"&&(i.position.applyQuaternion(tn.copy(this._quaternionStart).invert()),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.position.applyQuaternion(this._quaternionStart)),s==="world"&&(i.parent&&i.position.add(Nn.setFromMatrixPosition(i.parent.matrixWorld)),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.parent&&i.position.sub(Nn.setFromMatrixPosition(i.parent.matrixWorld)))),i.position.x=Math.max(this.minX,Math.min(this.maxX,i.position.x)),i.position.y=Math.max(this.minY,Math.min(this.maxY,i.position.y)),i.position.z=Math.max(this.minZ,Math.min(this.maxZ,i.position.z));else if(n==="scale"){if(t.search("XYZ")!==-1){let c=this.pointEnd.length()/this.pointStart.length();this.pointEnd.dot(this.pointStart)<0&&(c*=-1),mr.set(c,c,c)}else Nn.copy(this.pointStart),mr.copy(this.pointEnd),Nn.applyQuaternion(this._worldQuaternionInv),mr.applyQuaternion(this._worldQuaternionInv),mr.divide(Nn),t.search("X")===-1&&(mr.x=1),t.search("Y")===-1&&(mr.y=1),t.search("Z")===-1&&(mr.z=1);i.scale.copy(this._scaleStart).multiply(mr),this.scaleSnap&&(t.search("X")!==-1&&(i.scale.x=Math.round(i.scale.x/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Y")!==-1&&(i.scale.y=Math.round(i.scale.y/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Z")!==-1&&(i.scale.z=Math.round(i.scale.z/this.scaleSnap)*this.scaleSnap||this.scaleSnap))}else if(n==="rotate"){this._offset.copy(this.pointEnd).sub(this.pointStart);const c=20/this.worldPosition.distanceTo(Nn.setFromMatrixPosition(this.camera.matrixWorld));let u=!1;t==="XYZE"?(this.rotationAxis.copy(this._offset).cross(this.eye).normalize(),this.rotationAngle=this._offset.dot(Nn.copy(this.rotationAxis).cross(this.eye))*c):(t==="X"||t==="Y"||t==="Z")&&(this.rotationAxis.copy($m[t]),Nn.copy($m[t]),s==="local"&&Nn.applyQuaternion(this.worldQuaternion),Nn.cross(this.eye),Nn.length()===0?u=!0:this.rotationAngle=this._offset.dot(Nn.normalize())*c),(t==="E"||u)&&(this.rotationAxis.copy(this.eye),this.rotationAngle=this.pointEnd.angleTo(this.pointStart),this._startNorm.copy(this.pointStart).normalize(),this._endNorm.copy(this.pointEnd).normalize(),this.rotationAngle*=this._endNorm.cross(this._startNorm).dot(this.eye)<0?1:-1),this.rotationSnap&&(this.rotationAngle=Math.round(this.rotationAngle/this.rotationSnap)*this.rotationSnap),s==="local"&&t!=="E"&&t!=="XYZE"?(i.quaternion.copy(this._quaternionStart),i.quaternion.multiply(tn.setFromAxisAngle(this.rotationAxis,this.rotationAngle)).normalize()):(this.rotationAxis.applyQuaternion(this._parentQuaternionInv),i.quaternion.copy(tn.setFromAxisAngle(this.rotationAxis,this.rotationAngle)),i.quaternion.multiply(this._quaternionStart).normalize())}this.dispatchEvent(sh),this.dispatchEvent(Qm)}}pointerUp(e){e!==null&&e.button!==0||(this.dragging&&this.axis!==null&&(Jm.mode=this.mode,this.dispatchEvent(Jm)),this.dragging=!1,this.axis=null)}dispose(){this.disconnect(),this._root.dispose()}attach(e){return this.object=e,this._root.visible=!0,this}detach(){return this.object=void 0,this.axis=null,this._root.visible=!1,this}reset(){this.enabled&&this.dragging&&(this.object.position.copy(this._positionStart),this.object.quaternion.copy(this._quaternionStart),this.object.scale.copy(this._scaleStart),this.dispatchEvent(sh),this.dispatchEvent(Qm),this.pointStart.copy(this.pointEnd))}getRaycaster(){return Jr}getMode(){return this.mode}setMode(e){this.mode=e}setTranslationSnap(e){this.translationSnap=e}setRotationSnap(e){this.rotationSnap=e}setScaleSnap(e){this.scaleSnap=e}setSize(e){this.size=e}setSpace(e){this.space=e}}function PC(r){if(this.domElement.ownerDocument.pointerLockElement)return{x:0,y:0,button:r.button};{const e=this.domElement.getBoundingClientRect();return{x:(r.clientX-e.left)/e.width*2-1,y:-(r.clientY-e.top)/e.height*2+1,button:r.button}}}function RC(r){if(this.enabled)switch(r.pointerType){case"mouse":case"pen":this.pointerHover(this._getPointer(r));break}}function CC(r){this.enabled&&(document.pointerLockElement||this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.pointerHover(this._getPointer(r)),this.pointerDown(this._getPointer(r)))}function IC(r){this.enabled&&this.pointerMove(this._getPointer(r))}function LC(r){this.enabled&&(this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.pointerUp(this._getPointer(r)))}function oh(r,e,t){const n=e.intersectObject(r,!0);for(let i=0;i<n.length;i++)if(n[i].object.visible||t)return n[i];return!1}const yc=new xi,jt=new F(0,1,0),eg=new F(0,0,0),tg=new ot,xc=new en,Ic=new en,Mi=new F,ng=new ot,Xo=new F(1,0,0),ts=new F(0,1,0),qo=new F(0,0,1),bc=new F,zo=new F,Ho=new F;class DC extends Jt{constructor(e){super(),this.isTransformControlsRoot=!0,this.controls=e,this.visible=!1}updateMatrixWorld(e){const t=this.controls;t.object!==void 0&&(t.object.updateMatrixWorld(),t.object.parent===null?console.error("TransformControls: The attached 3D object must be a part of the scene graph."):t.object.parent.matrixWorld.decompose(t._parentPosition,t._parentQuaternion,t._parentScale),t.object.matrixWorld.decompose(t.worldPosition,t.worldQuaternion,t._worldScale),t._parentQuaternionInv.copy(t._parentQuaternion).invert(),t._worldQuaternionInv.copy(t.worldQuaternion).invert()),t.camera.updateMatrixWorld(),t.camera.matrixWorld.decompose(t.cameraPosition,t.cameraQuaternion,t._cameraScale),t.camera.isOrthographicCamera?t.camera.getWorldDirection(t.eye).negate():t.eye.copy(t.cameraPosition).sub(t.worldPosition).normalize(),super.updateMatrixWorld(e)}dispose(){this.traverse(function(e){e.geometry&&e.geometry.dispose(),e.material&&e.material.dispose()})}}class NC extends Jt{constructor(){super(),this.isTransformControlsGizmo=!0,this.type="TransformControlsGizmo";const e=new ui({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),t=new Gc({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),n=e.clone();n.opacity=.15;const i=t.clone();i.opacity=.5;const s=e.clone();s.color.setHex(16711680);const a=e.clone();a.color.setHex(65280);const c=e.clone();c.color.setHex(255);const u=e.clone();u.color.setHex(16711680),u.opacity=.5;const h=e.clone();h.color.setHex(65280),h.opacity=.5;const f=e.clone();f.color.setHex(255),f.opacity=.5;const p=e.clone();p.opacity=.25;const m=e.clone();m.color.setHex(16776960),m.opacity=.25,e.clone().color.setHex(16776960);const x=e.clone();x.color.setHex(7895160);const M=new An(0,.04,.1,12);M.translate(0,.05,0);const v=new sn(.08,.08,.08);v.translate(0,.04,0);const _=new mn;_.setAttribute("position",new Xt([0,0,0,1,0,0],3));const A=new An(.0075,.0075,.5,3);A.translate(0,.25,0);function w(ce,J){const de=new rs(ce,.0075,3,64,J*Math.PI*2);return de.rotateY(Math.PI/2),de.rotateX(Math.PI/2),de}function b(){const ce=new mn;return ce.setAttribute("position",new Xt([0,0,0,1,1,1],3)),ce}const B={X:[[new Ee(M,s),[.5,0,0],[0,0,-Math.PI/2]],[new Ee(M,s),[-.5,0,0],[0,0,Math.PI/2]],[new Ee(A,s),[0,0,0],[0,0,-Math.PI/2]]],Y:[[new Ee(M,a),[0,.5,0]],[new Ee(M,a),[0,-.5,0],[Math.PI,0,0]],[new Ee(A,a)]],Z:[[new Ee(M,c),[0,0,.5],[Math.PI/2,0,0]],[new Ee(M,c),[0,0,-.5],[-Math.PI/2,0,0]],[new Ee(A,c),null,[Math.PI/2,0,0]]],XYZ:[[new Ee(new Ws(.1,0),p.clone()),[0,0,0]]],XY:[[new Ee(new sn(.15,.15,.01),f.clone()),[.15,.15,0]]],YZ:[[new Ee(new sn(.15,.15,.01),u.clone()),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Ee(new sn(.15,.15,.01),h.clone()),[.15,0,.15],[-Math.PI/2,0,0]]]},U={X:[[new Ee(new An(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Ee(new An(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Ee(new An(.2,0,.6,4),n),[0,.3,0]],[new Ee(new An(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Ee(new An(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Ee(new An(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XYZ:[[new Ee(new Ws(.2,0),n)]],XY:[[new Ee(new sn(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Ee(new sn(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Ee(new sn(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]]},O={START:[[new Ee(new Ws(.01,2),i),null,null,null,"helper"]],END:[[new Ee(new Ws(.01,2),i),null,null,null,"helper"]],DELTA:[[new mi(b(),i),null,null,null,"helper"]],X:[[new mi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new mi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new mi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]},H={XYZE:[[new Ee(w(.5,1),x),null,[0,Math.PI/2,0]]],X:[[new Ee(w(.5,.5),s)]],Y:[[new Ee(w(.5,.5),a),null,[0,0,-Math.PI/2]]],Z:[[new Ee(w(.5,.5),c),null,[0,Math.PI/2,0]]],E:[[new Ee(w(.75,1),m),null,[0,Math.PI/2,0]]]},L={AXIS:[[new mi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]]},P={XYZE:[[new Ee(new ra(.25,10,8),n)]],X:[[new Ee(new rs(.5,.1,4,24),n),[0,0,0],[0,-Math.PI/2,-Math.PI/2]]],Y:[[new Ee(new rs(.5,.1,4,24),n),[0,0,0],[Math.PI/2,0,0]]],Z:[[new Ee(new rs(.5,.1,4,24),n),[0,0,0],[0,0,-Math.PI/2]]],E:[[new Ee(new rs(.75,.1,2,24),n)]]},V={X:[[new Ee(v,s),[.5,0,0],[0,0,-Math.PI/2]],[new Ee(A,s),[0,0,0],[0,0,-Math.PI/2]],[new Ee(v,s),[-.5,0,0],[0,0,Math.PI/2]]],Y:[[new Ee(v,a),[0,.5,0]],[new Ee(A,a)],[new Ee(v,a),[0,-.5,0],[0,0,Math.PI]]],Z:[[new Ee(v,c),[0,0,.5],[Math.PI/2,0,0]],[new Ee(A,c),[0,0,0],[Math.PI/2,0,0]],[new Ee(v,c),[0,0,-.5],[-Math.PI/2,0,0]]],XY:[[new Ee(new sn(.15,.15,.01),f),[.15,.15,0]]],YZ:[[new Ee(new sn(.15,.15,.01),u),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Ee(new sn(.15,.15,.01),h),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Ee(new sn(.1,.1,.1),p.clone())]]},ee={X:[[new Ee(new An(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Ee(new An(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Ee(new An(.2,0,.6,4),n),[0,.3,0]],[new Ee(new An(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Ee(new An(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Ee(new An(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XY:[[new Ee(new sn(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Ee(new sn(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Ee(new sn(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Ee(new sn(.2,.2,.2),n),[0,0,0]]]},Q={X:[[new mi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new mi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new mi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]};function ae(ce){const J=new Jt;for(const de in ce)for(let re=ce[de].length;re--;){const _e=ce[de][re][0].clone(),Me=ce[de][re][1],Ue=ce[de][re][2],Je=ce[de][re][3],pt=ce[de][re][4];_e.name=de,_e.tag=pt,Me&&_e.position.set(Me[0],Me[1],Me[2]),Ue&&_e.rotation.set(Ue[0],Ue[1],Ue[2]),Je&&_e.scale.set(Je[0],Je[1],Je[2]),_e.updateMatrix();const le=_e.geometry.clone();le.applyMatrix4(_e.matrix),_e.geometry=le,_e.renderOrder=1/0,_e.position.set(0,0,0),_e.rotation.set(0,0,0),_e.scale.set(1,1,1),J.add(_e)}return J}this.gizmo={},this.picker={},this.helper={},this.add(this.gizmo.translate=ae(B)),this.add(this.gizmo.rotate=ae(H)),this.add(this.gizmo.scale=ae(V)),this.add(this.picker.translate=ae(U)),this.add(this.picker.rotate=ae(P)),this.add(this.picker.scale=ae(ee)),this.add(this.helper.translate=ae(O)),this.add(this.helper.rotate=ae(L)),this.add(this.helper.scale=ae(Q)),this.picker.translate.visible=!1,this.picker.rotate.visible=!1,this.picker.scale.visible=!1}updateMatrixWorld(e){const n=(this.mode==="scale"?"local":this.space)==="local"?this.worldQuaternion:Ic;this.gizmo.translate.visible=this.mode==="translate",this.gizmo.rotate.visible=this.mode==="rotate",this.gizmo.scale.visible=this.mode==="scale",this.helper.translate.visible=this.mode==="translate",this.helper.rotate.visible=this.mode==="rotate",this.helper.scale.visible=this.mode==="scale";let i=[];i=i.concat(this.picker[this.mode].children),i=i.concat(this.gizmo[this.mode].children),i=i.concat(this.helper[this.mode].children);for(let s=0;s<i.length;s++){const a=i[s];a.visible=!0,a.rotation.set(0,0,0),a.position.copy(this.worldPosition);let c;if(this.camera.isOrthographicCamera?c=(this.camera.top-this.camera.bottom)/this.camera.zoom:c=this.worldPosition.distanceTo(this.cameraPosition)*Math.min(1.9*Math.tan(Math.PI*this.camera.fov/360)/this.camera.zoom,7),a.scale.set(1,1,1).multiplyScalar(c*this.size/4),a.tag==="helper"){a.visible=!1,a.name==="AXIS"?(a.visible=!!this.axis,this.axis==="X"&&(tn.setFromEuler(yc.set(0,0,0)),a.quaternion.copy(n).multiply(tn),Math.abs(jt.copy(Xo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Y"&&(tn.setFromEuler(yc.set(0,0,Math.PI/2)),a.quaternion.copy(n).multiply(tn),Math.abs(jt.copy(ts).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Z"&&(tn.setFromEuler(yc.set(0,Math.PI/2,0)),a.quaternion.copy(n).multiply(tn),Math.abs(jt.copy(qo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="XYZE"&&(tn.setFromEuler(yc.set(0,Math.PI/2,0)),jt.copy(this.rotationAxis),a.quaternion.setFromRotationMatrix(tg.lookAt(eg,jt,ts)),a.quaternion.multiply(tn),a.visible=this.dragging),this.axis==="E"&&(a.visible=!1)):a.name==="START"?(a.position.copy(this.worldPositionStart),a.visible=this.dragging):a.name==="END"?(a.position.copy(this.worldPosition),a.visible=this.dragging):a.name==="DELTA"?(a.position.copy(this.worldPositionStart),a.quaternion.copy(this.worldQuaternionStart),Nn.set(1e-10,1e-10,1e-10).add(this.worldPositionStart).sub(this.worldPosition).multiplyScalar(-1),Nn.applyQuaternion(this.worldQuaternionStart.clone().invert()),a.scale.copy(Nn),a.visible=this.dragging):(a.quaternion.copy(n),this.dragging?a.position.copy(this.worldPositionStart):a.position.copy(this.worldPosition),this.axis&&(a.visible=this.axis.search(a.name)!==-1));continue}a.quaternion.copy(n),this.mode==="translate"||this.mode==="scale"?(a.name==="X"&&Math.abs(jt.copy(Xo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Y"&&Math.abs(jt.copy(ts).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Z"&&Math.abs(jt.copy(qo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XY"&&Math.abs(jt.copy(qo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="YZ"&&Math.abs(jt.copy(Xo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XZ"&&Math.abs(jt.copy(ts).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1)):this.mode==="rotate"&&(xc.copy(n),jt.copy(this.eye).applyQuaternion(tn.copy(n).invert()),a.name.search("E")!==-1&&a.quaternion.setFromRotationMatrix(tg.lookAt(this.eye,eg,ts)),a.name==="X"&&(tn.setFromAxisAngle(Xo,Math.atan2(-jt.y,jt.z)),tn.multiplyQuaternions(xc,tn),a.quaternion.copy(tn)),a.name==="Y"&&(tn.setFromAxisAngle(ts,Math.atan2(jt.x,jt.z)),tn.multiplyQuaternions(xc,tn),a.quaternion.copy(tn)),a.name==="Z"&&(tn.setFromAxisAngle(qo,Math.atan2(jt.y,jt.x)),tn.multiplyQuaternions(xc,tn),a.quaternion.copy(tn))),a.visible=a.visible&&(a.name.indexOf("X")===-1||this.showX),a.visible=a.visible&&(a.name.indexOf("Y")===-1||this.showY),a.visible=a.visible&&(a.name.indexOf("Z")===-1||this.showZ),a.visible=a.visible&&(a.name.indexOf("E")===-1||this.showX&&this.showY&&this.showZ),a.material._color=a.material._color||a.material.color.clone(),a.material._opacity=a.material._opacity||a.material.opacity,a.material.color.copy(a.material._color),a.material.opacity=a.material._opacity,this.enabled&&this.axis&&(a.name===this.axis||this.axis.split("").some(function(u){return a.name===u}))&&(a.material.color.setHex(16776960),a.material.opacity=1)}super.updateMatrixWorld(e)}}class OC extends Ee{constructor(){super(new ao(1e5,1e5,2,2),new ui({visible:!1,wireframe:!0,side:Xn,transparent:!0,opacity:.1,toneMapped:!1})),this.isTransformControlsPlane=!0,this.type="TransformControlsPlane"}updateMatrixWorld(e){let t=this.space;switch(this.position.copy(this.worldPosition),this.mode==="scale"&&(t="local"),bc.copy(Xo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),zo.copy(ts).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Ho.copy(qo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),jt.copy(zo),this.mode){case"translate":case"scale":switch(this.axis){case"X":jt.copy(this.eye).cross(bc),Mi.copy(bc).cross(jt);break;case"Y":jt.copy(this.eye).cross(zo),Mi.copy(zo).cross(jt);break;case"Z":jt.copy(this.eye).cross(Ho),Mi.copy(Ho).cross(jt);break;case"XY":Mi.copy(Ho);break;case"YZ":Mi.copy(bc);break;case"XZ":jt.copy(Ho),Mi.copy(zo);break;case"XYZ":case"E":Mi.set(0,0,0);break}break;case"rotate":default:Mi.set(0,0,0)}Mi.length()===0?this.quaternion.copy(this.cameraQuaternion):(ng.lookAt(Nn.set(0,0,0),Mi,jt),this.quaternion.setFromRotationMatrix(ng)),super.updateMatrixWorld(e)}}function ah(r){const e=new $i,t=new Ed(.4,1,16),n=new ui({color:r,transparent:!0,opacity:1,side:Xn,depthTest:!1,depthWrite:!1}),i=new Ee(t,n);i.rotation.x=Math.PI,i.renderOrder=999;const s=new ra(.35,32,32),a=new ui({color:new $e(1,1,1),emissive:r,emissiveIntensity:2,transparent:!0,opacity:1,depthTest:!1,depthWrite:!1}),c=new Ee(s,a);return c.position.y=.5,c.renderOrder=999,e.add(i),e.add(c),e}function UC(r){const e=new AR({canvas:r,antialias:!0});e.setPixelRatio(window.devicePixelRatio),e.setSize(r.clientWidth,r.clientHeight),e.shadowMap.enabled=!1,e.toneMapping=dg,e.toneMappingExposure=1.6,e.outputColorSpace=bn;const t=new wR;t.background=new $e(1381664),t.fog=new Md(1381664,.03);const n=new kn(50,r.clientWidth/r.clientHeight,.1,1e3);n.position.set(0,1.6,5);const i=new pC(n,r);i.target.set(0,.9,0),i.enableDamping=!0,i.dampingFactor=.08,i.update();const s=new ao(14,10),a=new as({color:4864558,roughness:.35,metalness:.05}),c=new Ee(s,a);c.rotation.x=-Math.PI/2,c.position.y=-.01,c.receiveShadow=!0,t.add(c);const u=new sn(14.2,.06,10.2),h=new as({color:3811866,roughness:.6}),f=new Ee(u,h);f.position.y=-.04,f.receiveShadow=!0,t.add(f);const p=new ZR(16777215,.8);t.add(p);const m=new Cc(16777215,3);m.position.set(2,4,-5),t.add(m);const g=ah(new $e(16777215));g.position.copy(m.position),g.lookAt(new F(0,0,0)),g.userData.light=m,t.add(g);const x=new Cc(15658751,2);x.position.set(-3,3,-4),t.add(x);const M=ah(new $e(15658751));M.position.copy(x.position),M.lookAt(new F(0,0,0)),M.userData.light=x,t.add(M);const v=new Cc(16772829,2.5);v.position.set(0,4,5),t.add(v);const _=ah(new $e(16772829));_.position.copy(v.position),_.lookAt(new F(0,0,0)),_.userData.light=v,t.add(_);const A={ambient:p,spotLeft:m,spotRight:x,backLight:v},w={spotLeftIcon:g,spotRightIcon:M,backLightIcon:_},b=new wC(n,r);b.setMode("translate"),b.setSize(.8),t.add(b),b.addEventListener("dragging-changed",U=>{i.enabled=!U.value});function B(){const U=r.clientWidth,O=r.clientHeight;e.setSize(U,O),n.aspect=U/O,n.updateProjectionMatrix()}return window.addEventListener("resize",B),{scene:t,camera:n,renderer:e,controls:i,lights:A,lightIcons:w,transformControls:b}}var Yo={exports:{}};Yo.exports;var ig;function FC(){return ig||(ig=1,(function(r,e){var t=Object.create,n=Object.defineProperty,i=Object.defineProperties,s=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyDescriptors,c=Object.getOwnPropertyNames,u=Object.getOwnPropertySymbols,h=Object.getPrototypeOf,f=Object.prototype.hasOwnProperty,p=Object.prototype.propertyIsEnumerable,m=(o,l,d)=>l in o?n(o,l,{enumerable:!0,configurable:!0,writable:!0,value:d}):o[l]=d,g=(o,l)=>{for(var d in l||(l={}))f.call(l,d)&&m(o,d,l[d]);if(u)for(var d of u(l))p.call(l,d)&&m(o,d,l[d]);return o},x=(o,l)=>i(o,a(l)),M=(o,l)=>function(){return l||(0,o[c(o)[0]])((l={exports:{}}).exports,l),l.exports},v=(o,l)=>{for(var d in l)n(o,d,{get:l[d],enumerable:!0})},_=(o,l,d,y)=>{if(l&&typeof l=="object"||typeof l=="function")for(let T of c(l))!f.call(o,T)&&T!==d&&n(o,T,{get:()=>l[T],enumerable:!(y=s(l,T))||y.enumerable});return o},A=(o,l,d)=>(d=o!=null?t(h(o)):{},_(!o||!o.__esModule?n(d,"default",{value:o,enumerable:!0}):d,o)),w=o=>_(n({},"__esModule",{value:!0}),o),b=(o,l,d)=>(m(o,typeof l!="symbol"?l+"":l,d),d),B=M({"../node_modules/timing-function/lib/UnitBezier.js"(o,l){l.exports=(function(){function d(y,T,I,k){this.set(y,T,I,k)}return d.prototype.set=function(y,T,I,k){this._cx=3*y,this._bx=3*(I-y)-this._cx,this._ax=1-this._cx-this._bx,this._cy=3*T,this._by=3*(k-T)-this._cy,this._ay=1-this._cy-this._by},d.epsilon=1e-6,d.prototype._sampleCurveX=function(y){return((this._ax*y+this._bx)*y+this._cx)*y},d.prototype._sampleCurveY=function(y){return((this._ay*y+this._by)*y+this._cy)*y},d.prototype._sampleCurveDerivativeX=function(y){return(3*this._ax*y+2*this._bx)*y+this._cx},d.prototype._solveCurveX=function(y,T){var I,k,Y,$,oe,ge;for(Y=void 0,$=void 0,oe=void 0,ge=void 0,I=void 0,k=void 0,oe=y,k=0;k<8;){if(ge=this._sampleCurveX(oe)-y,Math.abs(ge)<T)return oe;if(I=this._sampleCurveDerivativeX(oe),Math.abs(I)<T)break;oe=oe-ge/I,k++}if(Y=0,$=1,oe=y,oe<Y)return Y;if(oe>$)return $;for(;Y<$;){if(ge=this._sampleCurveX(oe),Math.abs(ge-y)<T)return oe;y>ge?Y=oe:$=oe,oe=($-Y)*.5+Y}return oe},d.prototype.solve=function(y,T){return this._sampleCurveY(this._solveCurveX(y,T))},d.prototype.solveSimple=function(y){return this._sampleCurveY(this._solveCurveX(y,1e-6))},d})()}}),U=M({"../node_modules/levenshtein-edit-distance/index.js"(o,l){var d,y;d=[],y=[];function T(I,k,Y){var $,oe,ge,ve,Pe,Ye,ze,ft;if(I===k)return 0;if($=I.length,oe=k.length,$===0)return oe;if(oe===0)return $;for(Y&&(I=I.toLowerCase(),k=k.toLowerCase()),ze=0;ze<$;)y[ze]=I.charCodeAt(ze),d[ze]=++ze;for(ft=0;ft<oe;)for(ge=k.charCodeAt(ft),ve=Pe=ft++,ze=-1;++ze<$;)Ye=ge===y[ze]?Pe:Pe+1,Pe=d[ze],d[ze]=ve=Pe>ve?Ye>ve?ve+1:Ye:Ye>Pe?Pe+1:Ye;return ve}l.exports=T}}),O=M({"../node_modules/propose/propose.js"(o,l){var d=U();function y(){var T,I,k,Y,$,oe=0,ge=arguments[0],ve=arguments[1],Pe=ve.length,Ye=arguments[2];Ye&&(Y=Ye.threshold,$=Ye.ignoreCase),Y===void 0&&(Y=0);for(var ze=0;ze<Pe;++ze)$?I=d(ge,ve[ze],!0):I=d(ge,ve[ze]),I>ge.length?T=1-I/ve[ze].length:T=1-I/ge.length,T>oe&&(oe=T,k=ve[ze]);return oe>=Y?k:null}l.exports=y}}),H=M({"../node_modules/fast-deep-equal/index.js"(o,l){l.exports=function d(y,T){if(y===T)return!0;if(y&&T&&typeof y=="object"&&typeof T=="object"){if(y.constructor!==T.constructor)return!1;var I,k,Y;if(Array.isArray(y)){if(I=y.length,I!=T.length)return!1;for(k=I;k--!==0;)if(!d(y[k],T[k]))return!1;return!0}if(y.constructor===RegExp)return y.source===T.source&&y.flags===T.flags;if(y.valueOf!==Object.prototype.valueOf)return y.valueOf()===T.valueOf();if(y.toString!==Object.prototype.toString)return y.toString()===T.toString();if(Y=Object.keys(y),I=Y.length,I!==Object.keys(T).length)return!1;for(k=I;k--!==0;)if(!Object.prototype.hasOwnProperty.call(T,Y[k]))return!1;for(k=I;k--!==0;){var $=Y[k];if(!d(y[$],T[$]))return!1}return!0}return y!==y&&T!==T}}}),L={};v(L,{createRafDriver:()=>eu,getProject:()=>Tp,notify:()=>Ss,onChange:()=>Su,types:()=>tu,val:()=>Ep}),r.exports=w(L);var P={};v(P,{createRafDriver:()=>eu,getProject:()=>Tp,notify:()=>Ss,onChange:()=>Su,types:()=>tu,val:()=>Ep});var V=fn(),ee=class{constructor(){b(this,"atom",new V.Atom({projects:{}}))}add(o,l){this.atom.setByPointer(d=>d.projects[o],l)}get(o){return this.atom.get().projects[o]}has(o){return!!this.get(o)}},Q=new ee,ae=Q,ce=new WeakMap;function J(o){return ce.get(o)}function de(o,l){ce.set(o,l)}var re=[],_e=Array.isArray,Me=_e,Ue=typeof Ei=="object"&&Ei&&Ei.Object===Object&&Ei,Je=Ue,pt=typeof self=="object"&&self&&self.Object===Object&&self,le=Je||pt||Function("return this")(),pe=le,Fe=pe.Symbol,Se=Fe,qe=Object.prototype,it=qe.hasOwnProperty,at=qe.toString,Pt=Se?Se.toStringTag:void 0;function lt(o){var l=it.call(o,Pt),d=o[Pt];try{o[Pt]=void 0;var y=!0}catch{}var T=at.call(o);return y&&(l?o[Pt]=d:delete o[Pt]),T}var zt=lt,X=Object.prototype,rn=X.toString;function ut(o){return rn.call(o)}var mt=ut,We="[object Null]",Tt="[object Undefined]",ke=Se?Se.toStringTag:void 0;function N(o){return o==null?o===void 0?Tt:We:ke&&ke in Object(o)?zt(o):mt(o)}var E=N;function Z(o){return o!=null&&typeof o=="object"}var ue=Z,fe="[object Symbol]";function he(o){return typeof o=="symbol"||ue(o)&&E(o)==fe}var Oe=he,Ae=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Le=/^\w*$/;function ht(o,l){if(Me(o))return!1;var d=typeof o;return d=="number"||d=="symbol"||d=="boolean"||o==null||Oe(o)?!0:Le.test(o)||!Ae.test(o)||l!=null&&o in Object(l)}var me=ht;function De(o){var l=typeof o;return o!=null&&(l=="object"||l=="function")}var Be=De,Ze="[object AsyncFunction]",Ne="[object Function]",_t="[object GeneratorFunction]",st="[object Proxy]";function Ct(o){if(!Be(o))return!1;var l=E(o);return l==Ne||l==_t||l==Ze||l==st}var W=Ct,Te=pe["__core-js_shared__"],R=Te,z=(function(){var o=/[^.]+$/.exec(R&&R.keys&&R.keys.IE_PROTO||"");return o?"Symbol(src)_1."+o:""})();function K(o){return!!z&&z in o}var ie=K,ye=Function.prototype,xe=ye.toString;function we(o){if(o!=null){try{return xe.call(o)}catch{}try{return o+""}catch{}}return""}var Ie=we,nt=/[\\^$.*+?()[\]{}|]/g,Et=/^\[object .+?Constructor\]$/,qt=Function.prototype,Ke=Object.prototype,ct=qt.toString,Gt=Ke.hasOwnProperty,Rt=RegExp("^"+ct.call(Gt).replace(nt,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Xe(o){if(!Be(o)||ie(o))return!1;var l=W(o)?Rt:Et;return l.test(Ie(o))}var yt=Xe;function On(o,l){return o==null?void 0:o[l]}var tr=On;function hs(o,l){var d=tr(o,l);return yt(d)?d:void 0}var ri=hs,ho=ri(Object,"create"),Ci=ho;function nr(){this.__data__=Ci?Ci(null):{},this.size=0}var C=nr;function j(o){var l=this.has(o)&&delete this.__data__[o];return this.size-=l?1:0,l}var te=j,ne="__lodash_hash_undefined__",q=Object.prototype,be=q.hasOwnProperty;function Ce(o){var l=this.__data__;if(Ci){var d=l[o];return d===ne?void 0:d}return be.call(l,o)?l[o]:void 0}var He=Ce,Ve=Object.prototype,rt=Ve.hasOwnProperty;function Qe(o){var l=this.__data__;return Ci?l[o]!==void 0:rt.call(l,o)}var Ge=Qe,Mt="__lodash_hash_undefined__";function Nt(o,l){var d=this.__data__;return this.size+=this.has(o)?0:1,d[o]=Ci&&l===void 0?Mt:l,this}var Ut=Nt;function nn(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}nn.prototype.clear=C,nn.prototype.delete=te,nn.prototype.get=He,nn.prototype.has=Ge,nn.prototype.set=Ut;var At=nn;function je(){this.__data__=[],this.size=0}var Yn=je;function bt(o,l){return o===l||o!==o&&l!==l}var Mn=bt;function bi(o,l){for(var d=o.length;d--;)if(Mn(o[d][0],l))return d;return-1}var cn=bi,Ii=Array.prototype,Ft=Ii.splice;function Vn(o){var l=this.__data__,d=cn(l,o);if(d<0)return!1;var y=l.length-1;return d==y?l.pop():Ft.call(l,d,1),--this.size,!0}var Li=Vn;function Pn(o){var l=this.__data__,d=cn(l,o);return d<0?void 0:l[d][1]}var Tn=Pn;function Kn(o){return cn(this.__data__,o)>-1}var ds=Kn;function fo(o,l){var d=this.__data__,y=cn(d,o);return y<0?(++this.size,d.push([o,l])):d[y][1]=l,this}var jc=fo;function ir(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}ir.prototype.clear=Yn,ir.prototype.delete=Li,ir.prototype.get=Tn,ir.prototype.has=ds,ir.prototype.set=jc;var fs=ir,Xc=ri(pe,"Map"),Er=Xc;function qc(){this.size=0,this.__data__={hash:new At,map:new(Er||fs),string:new At}}var Yc=qc;function Kc(o){var l=typeof o;return l=="string"||l=="number"||l=="symbol"||l=="boolean"?o!=="__proto__":o===null}var $c=Kc;function Zc(o,l){var d=o.__data__;return $c(l)?d[typeof l=="string"?"string":"hash"]:d.map}var Ar=Zc;function oa(o){var l=Ar(this,o).delete(o);return this.size-=l?1:0,l}var aa=oa;function Jc(o){return Ar(this,o).get(o)}var Qc=Jc;function el(o){return Ar(this,o).has(o)}var tl=el;function nl(o,l){var d=Ar(this,o),y=d.size;return d.set(o,l),this.size+=d.size==y?0:1,this}var il=nl;function rr(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}rr.prototype.clear=Yc,rr.prototype.delete=aa,rr.prototype.get=Qc,rr.prototype.has=tl,rr.prototype.set=il;var ps=rr,rl="Expected a function";function po(o,l){if(typeof o!="function"||l!=null&&typeof l!="function")throw new TypeError(rl);var d=function(){var y=arguments,T=l?l.apply(this,y):y[0],I=d.cache;if(I.has(T))return I.get(T);var k=o.apply(this,y);return d.cache=I.set(T,k)||I,k};return d.cache=new(po.Cache||ps),d}po.Cache=ps;var sl=po,ol=500;function al(o){var l=sl(o,function(y){return d.size===ol&&d.clear(),y}),d=l.cache;return l}var cl=al,ll=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,ul=/\\(\\)?/g,hl=cl(function(o){var l=[];return o.charCodeAt(0)===46&&l.push(""),o.replace(ll,function(d,y,T,I){l.push(T?I.replace(ul,"$1"):y||d)}),l}),dl=hl;function ca(o,l){for(var d=-1,y=o==null?0:o.length,T=Array(y);++d<y;)T[d]=l(o[d],d,o);return T}var fl=ca,la=Se?Se.prototype:void 0,ua=la?la.toString:void 0;function ha(o){if(typeof o=="string")return o;if(Me(o))return fl(o,ha)+"";if(Oe(o))return ua?ua.call(o):"";var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var da=ha;function pl(o){return o==null?"":da(o)}var ms=pl;function fa(o,l){return Me(o)?o:me(o,l)?[o]:dl(ms(o))}var wr=fa;function ml(o){if(typeof o=="string"||Oe(o))return o;var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var hi=ml;function Pr(o,l){l=wr(l,o);for(var d=0,y=l.length;o!=null&&d<y;)o=o[hi(l[d++])];return d&&d==y?o:void 0}var gs=Pr;function mo(o,l,d){var y=o==null?void 0:gs(o,l);return y===void 0?d:y}var Di=mo;function pa(o,l){return l.length===0?o:Di(o,l)}var sr=class{constructor(){b(this,"_values",{})}get(o,l){if(this.has(o))return this._values[o];{const d=l();return this._values[o]=d,d}}has(o){return this._values.hasOwnProperty(o)}},hn=fn(),_s=(function(){try{var o=ri(Object,"defineProperty");return o({},"",{}),o}catch{}})(),go=_s;function gl(o,l,d){l=="__proto__"&&go?go(o,l,{configurable:!0,enumerable:!0,value:d,writable:!0}):o[l]=d}var Ni=gl,Rr=Object.prototype,_l=Rr.hasOwnProperty;function vl(o,l,d){var y=o[l];(!(_l.call(o,l)&&Mn(y,d))||d===void 0&&!(l in o))&&Ni(o,l,d)}var _o=vl,yl=9007199254740991,ma=/^(?:0|[1-9]\d*)$/;function xl(o,l){var d=typeof o;return l=l??yl,!!l&&(d=="number"||d!="symbol"&&ma.test(o))&&o>-1&&o%1==0&&o<l}var vo=xl;function bl(o,l,d,y){if(!Be(o))return o;l=wr(l,o);for(var T=-1,I=l.length,k=I-1,Y=o;Y!=null&&++T<I;){var $=hi(l[T]),oe=d;if($==="__proto__"||$==="constructor"||$==="prototype")return o;if(T!=k){var ge=Y[$];oe=y?y(ge,$,Y):void 0,oe===void 0&&(oe=Be(ge)?ge:vo(l[T+1])?[]:{})}_o(Y,$,oe),Y=Y[$]}return o}var ga=bl;function _a(o,l,d){return o==null?o:ga(o,l,d)}var vs=_a,vn=new WeakMap;function Sl(o){return yo(o)}function yo(o){if(vn.has(o))return vn.get(o);const l=o.type==="compound"?ya(o):o.type==="enum"?va(o):o.default;return vn.set(o,l),l}function va(o){const l={$case:o.defaultCase};for(const[d,y]of Object.entries(o.cases))l[d]=yo(y);return l}function ya(o){const l={};for(const[d,y]of Object.entries(o.props))l[d]=yo(y);return l}var Un=fn(),Ml=A(B());function Tl(o,l,d){return(0,Un.prism)(()=>{const y=(0,Un.val)(l);return Un.prism.memo("driver",()=>y?y.type==="BasicKeyframedTrack"?El(o,y,d):(o.logger.error("Track type not yet supported."),(0,Un.prism)(()=>{})):(0,Un.prism)(()=>{}),[y]).getValue()})}function El(o,l,d){return(0,Un.prism)(()=>{let y=Un.prism.ref("state",{started:!1}),T=y.current;const I=d.getValue();return(!T.started||I<T.validFrom||T.validTo<=I)&&(y.current=T=Al(o,d,l)),T.der.getValue()})}var xa=(0,Un.prism)(()=>{});function Al(o,l,d){const y=l.getValue();if(d.keyframes.length===0)return{started:!0,validFrom:-1/0,validTo:1/0,der:xa};let T=0;for(;;){const I=d.keyframes[T];if(!I)return dn.error;const k=T===d.keyframes.length-1;if(y<I.position)return T===0?dn.beforeFirstKeyframe(I):dn.error;if(I.position===y)return k?dn.lastKeyframe(I):dn.between(I,d.keyframes[T+1],l);if(T===d.keyframes.length-1)return dn.lastKeyframe(I);{const Y=T+1;if(d.keyframes[Y].position<=y){T=Y;continue}else return dn.between(I,d.keyframes[T+1],l)}}}var dn={beforeFirstKeyframe(o){return{started:!0,validFrom:-1/0,validTo:o.position,der:(0,Un.prism)(()=>({left:o.value,progression:0}))}},lastKeyframe(o){return{started:!0,validFrom:o.position,validTo:1/0,der:(0,Un.prism)(()=>({left:o.value,progression:0}))}},between(o,l,d){if(!o.connectedRight)return{started:!0,validFrom:o.position,validTo:l.position,der:(0,Un.prism)(()=>({left:o.value,progression:0}))};const y=I=>(I-o.position)/(l.position-o.position);if(!o.type||o.type==="bezier"){const I=new Ml.default(o.handles[2],o.handles[3],l.handles[0],l.handles[1]),k=(0,Un.prism)(()=>{const Y=y(d.getValue()),$=I.solveSimple(Y);return{left:o.value,right:l.value,progression:$}});return{started:!0,validFrom:o.position,validTo:l.position,der:k}}const T=(0,Un.prism)(()=>{const I=y(d.getValue()),k=Math.floor(I);return{left:o.value,right:l.value,progression:k}});return{started:!0,validFrom:o.position,validTo:l.position,der:T}},error:{started:!0,validFrom:-1/0,validTo:1/0,der:xa}};function Cr(o,l,d){const T=d.get(o);if(T&&T.override===l)return T.merged;const I=g({},o);for(const k of Object.keys(l)){const Y=l[k],$=o[k];I[k]=typeof Y=="object"&&typeof $=="object"?Cr($,Y,d):Y===void 0?$:Y}return d.set(o,{override:l,merged:I}),I}function Ir(o,l){let d=o;for(const y of l)d=d[y];return d}var Lr=fn(),ba=(o,l)=>{const d=Lr.prism.memo(o,()=>new Lr.Atom(l),[]);return d.set(l),d},Bt=fn(),xo=fn(),wl=/\s/;function Sa(o){for(var l=o.length;l--&&wl.test(o.charAt(l)););return l}var Ma=Sa,Ta=/^\s+/;function Pl(o){return o&&o.slice(0,Ma(o)+1).replace(Ta,"")}var ys=Pl,bo=NaN,Rl=/^[-+]0x[0-9a-f]+$/i,Cl=/^0b[01]+$/i,Ea=/^0o[0-7]+$/i,Il=parseInt;function Ll(o){if(typeof o=="number")return o;if(Oe(o))return bo;if(Be(o)){var l=typeof o.valueOf=="function"?o.valueOf():o;o=Be(l)?l+"":l}if(typeof o!="string")return o===0?o:+o;o=ys(o);var d=Cl.test(o);return d||Ea.test(o)?Il(o.slice(2),d?2:8):Rl.test(o)?bo:+o}var S=Ll,D=1/0,G=17976931348623157e292;function se(o){if(!o)return o===0?o:0;if(o=S(o),o===D||o===-D){var l=o<0?-1:1;return l*G}return o===o?o:0}var et=se;function It(o){var l=et(o),d=l%1;return l===l?d?l-d:l:0}var En=It;function si(o){return o}var Aa=si,or=ri(pe,"WeakMap"),Dr=or,Nd=Object.create,c_=(function(){function o(){}return function(l){if(!Be(l))return{};if(Nd)return Nd(l);o.prototype=l;var d=new o;return o.prototype=void 0,d}})(),l_=c_;function u_(o,l){var d=-1,y=o.length;for(l||(l=Array(y));++d<y;)l[d]=o[d];return l}var h_=u_;function d_(o,l){for(var d=-1,y=o==null?0:o.length;++d<y&&l(o[d],d,o)!==!1;);return o}var f_=d_;function p_(o,l,d,y){var T=!d;d||(d={});for(var I=-1,k=l.length;++I<k;){var Y=l[I],$=y?y(d[Y],o[Y],Y,d,o):void 0;$===void 0&&($=o[Y]),T?Ni(d,Y,$):_o(d,Y,$)}return d}var wa=p_,m_=9007199254740991;function g_(o){return typeof o=="number"&&o>-1&&o%1==0&&o<=m_}var Dl=g_;function __(o){return o!=null&&Dl(o.length)&&!W(o)}var Od=__,v_=Object.prototype;function y_(o){var l=o&&o.constructor,d=typeof l=="function"&&l.prototype||v_;return o===d}var Nl=y_;function x_(o,l){for(var d=-1,y=Array(o);++d<o;)y[d]=l(d);return y}var b_=x_,S_="[object Arguments]";function M_(o){return ue(o)&&E(o)==S_}var Ud=M_,Fd=Object.prototype,T_=Fd.hasOwnProperty,E_=Fd.propertyIsEnumerable,A_=Ud((function(){return arguments})())?Ud:function(o){return ue(o)&&T_.call(o,"callee")&&!E_.call(o,"callee")},Bd=A_;function w_(){return!1}var P_=w_,kd=e&&!e.nodeType&&e,zd=kd&&!0&&r&&!r.nodeType&&r,R_=zd&&zd.exports===kd,Hd=R_?pe.Buffer:void 0,C_=Hd?Hd.isBuffer:void 0,I_=C_||P_,Pa=I_,L_="[object Arguments]",D_="[object Array]",N_="[object Boolean]",O_="[object Date]",U_="[object Error]",F_="[object Function]",B_="[object Map]",k_="[object Number]",z_="[object Object]",H_="[object RegExp]",V_="[object Set]",G_="[object String]",W_="[object WeakMap]",j_="[object ArrayBuffer]",X_="[object DataView]",q_="[object Float32Array]",Y_="[object Float64Array]",K_="[object Int8Array]",$_="[object Int16Array]",Z_="[object Int32Array]",J_="[object Uint8Array]",Q_="[object Uint8ClampedArray]",ev="[object Uint16Array]",tv="[object Uint32Array]",Qt={};Qt[q_]=Qt[Y_]=Qt[K_]=Qt[$_]=Qt[Z_]=Qt[J_]=Qt[Q_]=Qt[ev]=Qt[tv]=!0,Qt[L_]=Qt[D_]=Qt[j_]=Qt[N_]=Qt[X_]=Qt[O_]=Qt[U_]=Qt[F_]=Qt[B_]=Qt[k_]=Qt[z_]=Qt[H_]=Qt[V_]=Qt[G_]=Qt[W_]=!1;function nv(o){return ue(o)&&Dl(o.length)&&!!Qt[E(o)]}var iv=nv;function rv(o){return function(l){return o(l)}}var Ol=rv,Vd=e&&!e.nodeType&&e,So=Vd&&!0&&r&&!r.nodeType&&r,sv=So&&So.exports===Vd,Ul=sv&&Je.process,ov=(function(){try{var o=So&&So.require&&So.require("util").types;return o||Ul&&Ul.binding&&Ul.binding("util")}catch{}})(),xs=ov,Gd=xs&&xs.isTypedArray,av=Gd?Ol(Gd):iv,Wd=av,cv=Object.prototype,lv=cv.hasOwnProperty;function uv(o,l){var d=Me(o),y=!d&&Bd(o),T=!d&&!y&&Pa(o),I=!d&&!y&&!T&&Wd(o),k=d||y||T||I,Y=k?b_(o.length,String):[],$=Y.length;for(var oe in o)(l||lv.call(o,oe))&&!(k&&(oe=="length"||T&&(oe=="offset"||oe=="parent")||I&&(oe=="buffer"||oe=="byteLength"||oe=="byteOffset")||vo(oe,$)))&&Y.push(oe);return Y}var jd=uv;function hv(o,l){return function(d){return o(l(d))}}var Xd=hv,dv=Xd(Object.keys,Object),fv=dv,pv=Object.prototype,mv=pv.hasOwnProperty;function gv(o){if(!Nl(o))return fv(o);var l=[];for(var d in Object(o))mv.call(o,d)&&d!="constructor"&&l.push(d);return l}var _v=gv;function vv(o){return Od(o)?jd(o):_v(o)}var Mo=vv;function yv(o){var l=[];if(o!=null)for(var d in Object(o))l.push(d);return l}var xv=yv,bv=Object.prototype,Sv=bv.hasOwnProperty;function Mv(o){if(!Be(o))return xv(o);var l=Nl(o),d=[];for(var y in o)y=="constructor"&&(l||!Sv.call(o,y))||d.push(y);return d}var Tv=Mv;function Ev(o){return Od(o)?jd(o,!0):Tv(o)}var Fl=Ev;function Av(o,l){for(var d=-1,y=l.length,T=o.length;++d<y;)o[T+d]=l[d];return o}var qd=Av,wv=Xd(Object.getPrototypeOf,Object),Bl=wv,Pv="[object Object]",Rv=Function.prototype,Cv=Object.prototype,Yd=Rv.toString,Iv=Cv.hasOwnProperty,Lv=Yd.call(Object);function Dv(o){if(!ue(o)||E(o)!=Pv)return!1;var l=Bl(o);if(l===null)return!0;var d=Iv.call(l,"constructor")&&l.constructor;return typeof d=="function"&&d instanceof d&&Yd.call(d)==Lv}var Nv=Dv;function Ov(o,l,d){var y=-1,T=o.length;l<0&&(l=-l>T?0:T+l),d=d>T?T:d,d<0&&(d+=T),T=l>d?0:d-l>>>0,l>>>=0;for(var I=Array(T);++y<T;)I[y]=o[y+l];return I}var Kd=Ov;function Uv(o,l,d){var y=o.length;return d=d===void 0?y:d,!l&&d>=y?o:Kd(o,l,d)}var Fv=Uv,Bv="\\ud800-\\udfff",kv="\\u0300-\\u036f",zv="\\ufe20-\\ufe2f",Hv="\\u20d0-\\u20ff",Vv=kv+zv+Hv,Gv="\\ufe0e\\ufe0f",Wv="\\u200d",jv=RegExp("["+Wv+Bv+Vv+Gv+"]");function Xv(o){return jv.test(o)}var kl=Xv;function qv(o){return o.split("")}var Yv=qv,$d="\\ud800-\\udfff",Kv="\\u0300-\\u036f",$v="\\ufe20-\\ufe2f",Zv="\\u20d0-\\u20ff",Jv=Kv+$v+Zv,Qv="\\ufe0e\\ufe0f",e0="["+$d+"]",zl="["+Jv+"]",Hl="\\ud83c[\\udffb-\\udfff]",t0="(?:"+zl+"|"+Hl+")",Zd="[^"+$d+"]",Jd="(?:\\ud83c[\\udde6-\\uddff]){2}",Qd="[\\ud800-\\udbff][\\udc00-\\udfff]",n0="\\u200d",ef=t0+"?",tf="["+Qv+"]?",i0="(?:"+n0+"(?:"+[Zd,Jd,Qd].join("|")+")"+tf+ef+")*",r0=tf+ef+i0,s0="(?:"+[Zd+zl+"?",zl,Jd,Qd,e0].join("|")+")",o0=RegExp(Hl+"(?="+Hl+")|"+s0+r0,"g");function a0(o){return o.match(o0)||[]}var c0=a0;function l0(o){return kl(o)?c0(o):Yv(o)}var u0=l0;function h0(o,l,d){return o===o&&(d!==void 0&&(o=o<=d?o:d),l!==void 0&&(o=o>=l?o:l)),o}var d0=h0;function f0(o,l,d){return d===void 0&&(d=l,l=void 0),d!==void 0&&(d=S(d),d=d===d?d:0),l!==void 0&&(l=S(l),l=l===l?l:0),d0(S(o),l,d)}var nf=f0;function p0(){this.__data__=new fs,this.size=0}var m0=p0;function g0(o){var l=this.__data__,d=l.delete(o);return this.size=l.size,d}var _0=g0;function v0(o){return this.__data__.get(o)}var y0=v0;function x0(o){return this.__data__.has(o)}var b0=x0,S0=200;function M0(o,l){var d=this.__data__;if(d instanceof fs){var y=d.__data__;if(!Er||y.length<S0-1)return y.push([o,l]),this.size=++d.size,this;d=this.__data__=new ps(y)}return d.set(o,l),this.size=d.size,this}var T0=M0;function bs(o){var l=this.__data__=new fs(o);this.size=l.size}bs.prototype.clear=m0,bs.prototype.delete=_0,bs.prototype.get=y0,bs.prototype.has=b0,bs.prototype.set=T0;var To=bs;function E0(o,l){return o&&wa(l,Mo(l),o)}var A0=E0;function w0(o,l){return o&&wa(l,Fl(l),o)}var P0=w0,rf=e&&!e.nodeType&&e,sf=rf&&!0&&r&&!r.nodeType&&r,R0=sf&&sf.exports===rf,of=R0?pe.Buffer:void 0,af=of?of.allocUnsafe:void 0;function C0(o,l){if(l)return o.slice();var d=o.length,y=af?af(d):new o.constructor(d);return o.copy(y),y}var I0=C0;function L0(o,l){for(var d=-1,y=o==null?0:o.length,T=0,I=[];++d<y;){var k=o[d];l(k,d,o)&&(I[T++]=k)}return I}var D0=L0;function N0(){return[]}var cf=N0,O0=Object.prototype,U0=O0.propertyIsEnumerable,lf=Object.getOwnPropertySymbols,F0=lf?function(o){return o==null?[]:(o=Object(o),D0(lf(o),function(l){return U0.call(o,l)}))}:cf,Vl=F0;function B0(o,l){return wa(o,Vl(o),l)}var k0=B0,z0=Object.getOwnPropertySymbols,H0=z0?function(o){for(var l=[];o;)qd(l,Vl(o)),o=Bl(o);return l}:cf,uf=H0;function V0(o,l){return wa(o,uf(o),l)}var G0=V0;function W0(o,l,d){var y=l(o);return Me(o)?y:qd(y,d(o))}var hf=W0;function j0(o){return hf(o,Mo,Vl)}var Gl=j0;function X0(o){return hf(o,Fl,uf)}var q0=X0,Y0=ri(pe,"DataView"),Wl=Y0,K0=ri(pe,"Promise"),jl=K0,$0=ri(pe,"Set"),Xl=$0,df="[object Map]",Z0="[object Object]",ff="[object Promise]",pf="[object Set]",mf="[object WeakMap]",gf="[object DataView]",J0=Ie(Wl),Q0=Ie(Er),ey=Ie(jl),ty=Ie(Xl),ny=Ie(Dr),Nr=E;(Wl&&Nr(new Wl(new ArrayBuffer(1)))!=gf||Er&&Nr(new Er)!=df||jl&&Nr(jl.resolve())!=ff||Xl&&Nr(new Xl)!=pf||Dr&&Nr(new Dr)!=mf)&&(Nr=function(o){var l=E(o),d=l==Z0?o.constructor:void 0,y=d?Ie(d):"";if(y)switch(y){case J0:return gf;case Q0:return df;case ey:return ff;case ty:return pf;case ny:return mf}return l});var Eo=Nr,iy=Object.prototype,ry=iy.hasOwnProperty;function sy(o){var l=o.length,d=new o.constructor(l);return l&&typeof o[0]=="string"&&ry.call(o,"index")&&(d.index=o.index,d.input=o.input),d}var oy=sy,ay=pe.Uint8Array,Ra=ay;function cy(o){var l=new o.constructor(o.byteLength);return new Ra(l).set(new Ra(o)),l}var ql=cy;function ly(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.byteLength)}var uy=ly,hy=/\w*$/;function dy(o){var l=new o.constructor(o.source,hy.exec(o));return l.lastIndex=o.lastIndex,l}var fy=dy,_f=Se?Se.prototype:void 0,vf=_f?_f.valueOf:void 0;function py(o){return vf?Object(vf.call(o)):{}}var my=py;function gy(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.length)}var _y=gy,vy="[object Boolean]",yy="[object Date]",xy="[object Map]",by="[object Number]",Sy="[object RegExp]",My="[object Set]",Ty="[object String]",Ey="[object Symbol]",Ay="[object ArrayBuffer]",wy="[object DataView]",Py="[object Float32Array]",Ry="[object Float64Array]",Cy="[object Int8Array]",Iy="[object Int16Array]",Ly="[object Int32Array]",Dy="[object Uint8Array]",Ny="[object Uint8ClampedArray]",Oy="[object Uint16Array]",Uy="[object Uint32Array]";function Fy(o,l,d){var y=o.constructor;switch(l){case Ay:return ql(o);case vy:case yy:return new y(+o);case wy:return uy(o,d);case Py:case Ry:case Cy:case Iy:case Ly:case Dy:case Ny:case Oy:case Uy:return _y(o,d);case xy:return new y;case by:case Ty:return new y(o);case Sy:return fy(o);case My:return new y;case Ey:return my(o)}}var By=Fy;function ky(o){return typeof o.constructor=="function"&&!Nl(o)?l_(Bl(o)):{}}var zy=ky,Hy="[object Map]";function Vy(o){return ue(o)&&Eo(o)==Hy}var Gy=Vy,yf=xs&&xs.isMap,Wy=yf?Ol(yf):Gy,jy=Wy,Xy="[object Set]";function qy(o){return ue(o)&&Eo(o)==Xy}var Yy=qy,xf=xs&&xs.isSet,Ky=xf?Ol(xf):Yy,$y=Ky,Zy=1,Jy=2,Qy=4,bf="[object Arguments]",ex="[object Array]",tx="[object Boolean]",nx="[object Date]",ix="[object Error]",Sf="[object Function]",rx="[object GeneratorFunction]",sx="[object Map]",ox="[object Number]",Mf="[object Object]",ax="[object RegExp]",cx="[object Set]",lx="[object String]",ux="[object Symbol]",hx="[object WeakMap]",dx="[object ArrayBuffer]",fx="[object DataView]",px="[object Float32Array]",mx="[object Float64Array]",gx="[object Int8Array]",_x="[object Int16Array]",vx="[object Int32Array]",yx="[object Uint8Array]",xx="[object Uint8ClampedArray]",bx="[object Uint16Array]",Sx="[object Uint32Array]",Yt={};Yt[bf]=Yt[ex]=Yt[dx]=Yt[fx]=Yt[tx]=Yt[nx]=Yt[px]=Yt[mx]=Yt[gx]=Yt[_x]=Yt[vx]=Yt[sx]=Yt[ox]=Yt[Mf]=Yt[ax]=Yt[cx]=Yt[lx]=Yt[ux]=Yt[yx]=Yt[xx]=Yt[bx]=Yt[Sx]=!0,Yt[ix]=Yt[Sf]=Yt[hx]=!1;function Ca(o,l,d,y,T,I){var k,Y=l&Zy,$=l&Jy,oe=l&Qy;if(d&&(k=T?d(o,y,T,I):d(o)),k!==void 0)return k;if(!Be(o))return o;var ge=Me(o);if(ge){if(k=oy(o),!Y)return h_(o,k)}else{var ve=Eo(o),Pe=ve==Sf||ve==rx;if(Pa(o))return I0(o,Y);if(ve==Mf||ve==bf||Pe&&!T){if(k=$||Pe?{}:zy(o),!Y)return $?G0(o,P0(k,o)):k0(o,A0(k,o))}else{if(!Yt[ve])return T?o:{};k=By(o,ve,Y)}}I||(I=new To);var Ye=I.get(o);if(Ye)return Ye;I.set(o,k),$y(o)?o.forEach(function(xt){k.add(Ca(xt,l,d,xt,o,I))}):jy(o)&&o.forEach(function(xt,dt){k.set(dt,Ca(xt,l,d,dt,o,I))});var ze=oe?$?q0:Gl:$?Fl:Mo,ft=ge?void 0:ze(o);return f_(ft||o,function(xt,dt){ft&&(dt=xt,xt=o[dt]),_o(k,dt,Ca(xt,l,d,dt,o,I))}),k}var Mx=Ca,Tx=1,Ex=4;function Ax(o){return Mx(o,Tx|Ex)}var wx=Ax,Px="__lodash_hash_undefined__";function Rx(o){return this.__data__.set(o,Px),this}var Cx=Rx;function Ix(o){return this.__data__.has(o)}var Lx=Ix;function Ia(o){var l=-1,d=o==null?0:o.length;for(this.__data__=new ps;++l<d;)this.add(o[l])}Ia.prototype.add=Ia.prototype.push=Cx,Ia.prototype.has=Lx;var Dx=Ia;function Nx(o,l){for(var d=-1,y=o==null?0:o.length;++d<y;)if(l(o[d],d,o))return!0;return!1}var Ox=Nx;function Ux(o,l){return o.has(l)}var Fx=Ux,Bx=1,kx=2;function zx(o,l,d,y,T,I){var k=d&Bx,Y=o.length,$=l.length;if(Y!=$&&!(k&&$>Y))return!1;var oe=I.get(o),ge=I.get(l);if(oe&&ge)return oe==l&&ge==o;var ve=-1,Pe=!0,Ye=d&kx?new Dx:void 0;for(I.set(o,l),I.set(l,o);++ve<Y;){var ze=o[ve],ft=l[ve];if(y)var xt=k?y(ft,ze,ve,l,o,I):y(ze,ft,ve,o,l,I);if(xt!==void 0){if(xt)continue;Pe=!1;break}if(Ye){if(!Ox(l,function(dt,Lt){if(!Fx(Ye,Lt)&&(ze===dt||T(ze,dt,d,y,I)))return Ye.push(Lt)})){Pe=!1;break}}else if(!(ze===ft||T(ze,ft,d,y,I))){Pe=!1;break}}return I.delete(o),I.delete(l),Pe}var Tf=zx;function Hx(o){var l=-1,d=Array(o.size);return o.forEach(function(y,T){d[++l]=[T,y]}),d}var Vx=Hx;function Gx(o){var l=-1,d=Array(o.size);return o.forEach(function(y){d[++l]=y}),d}var Wx=Gx,jx=1,Xx=2,qx="[object Boolean]",Yx="[object Date]",Kx="[object Error]",$x="[object Map]",Zx="[object Number]",Jx="[object RegExp]",Qx="[object Set]",eb="[object String]",tb="[object Symbol]",nb="[object ArrayBuffer]",ib="[object DataView]",Ef=Se?Se.prototype:void 0,Yl=Ef?Ef.valueOf:void 0;function rb(o,l,d,y,T,I,k){switch(d){case ib:if(o.byteLength!=l.byteLength||o.byteOffset!=l.byteOffset)return!1;o=o.buffer,l=l.buffer;case nb:return!(o.byteLength!=l.byteLength||!I(new Ra(o),new Ra(l)));case qx:case Yx:case Zx:return Mn(+o,+l);case Kx:return o.name==l.name&&o.message==l.message;case Jx:case eb:return o==l+"";case $x:var Y=Vx;case Qx:var $=y&jx;if(Y||(Y=Wx),o.size!=l.size&&!$)return!1;var oe=k.get(o);if(oe)return oe==l;y|=Xx,k.set(o,l);var ge=Tf(Y(o),Y(l),y,T,I,k);return k.delete(o),ge;case tb:if(Yl)return Yl.call(o)==Yl.call(l)}return!1}var sb=rb,ob=1,ab=Object.prototype,cb=ab.hasOwnProperty;function lb(o,l,d,y,T,I){var k=d&ob,Y=Gl(o),$=Y.length,oe=Gl(l),ge=oe.length;if($!=ge&&!k)return!1;for(var ve=$;ve--;){var Pe=Y[ve];if(!(k?Pe in l:cb.call(l,Pe)))return!1}var Ye=I.get(o),ze=I.get(l);if(Ye&&ze)return Ye==l&&ze==o;var ft=!0;I.set(o,l),I.set(l,o);for(var xt=k;++ve<$;){Pe=Y[ve];var dt=o[Pe],Lt=l[Pe];if(y)var Rn=k?y(Lt,dt,Pe,l,o,I):y(dt,Lt,Pe,o,l,I);if(!(Rn===void 0?dt===Lt||T(dt,Lt,d,y,I):Rn)){ft=!1;break}xt||(xt=Pe=="constructor")}if(ft&&!xt){var Wn=o.constructor,Cn=l.constructor;Wn!=Cn&&"constructor"in o&&"constructor"in l&&!(typeof Wn=="function"&&Wn instanceof Wn&&typeof Cn=="function"&&Cn instanceof Cn)&&(ft=!1)}return I.delete(o),I.delete(l),ft}var ub=lb,hb=1,Af="[object Arguments]",wf="[object Array]",La="[object Object]",db=Object.prototype,Pf=db.hasOwnProperty;function fb(o,l,d,y,T,I){var k=Me(o),Y=Me(l),$=k?wf:Eo(o),oe=Y?wf:Eo(l);$=$==Af?La:$,oe=oe==Af?La:oe;var ge=$==La,ve=oe==La,Pe=$==oe;if(Pe&&Pa(o)){if(!Pa(l))return!1;k=!0,ge=!1}if(Pe&&!ge)return I||(I=new To),k||Wd(o)?Tf(o,l,d,y,T,I):sb(o,l,$,d,y,T,I);if(!(d&hb)){var Ye=ge&&Pf.call(o,"__wrapped__"),ze=ve&&Pf.call(l,"__wrapped__");if(Ye||ze){var ft=Ye?o.value():o,xt=ze?l.value():l;return I||(I=new To),T(ft,xt,d,y,I)}}return Pe?(I||(I=new To),ub(o,l,d,y,T,I)):!1}var pb=fb;function Rf(o,l,d,y,T){return o===l?!0:o==null||l==null||!ue(o)&&!ue(l)?o!==o&&l!==l:pb(o,l,d,y,Rf,T)}var Cf=Rf,mb=1,gb=2;function _b(o,l,d,y){var T=d.length,I=T,k=!y;if(o==null)return!I;for(o=Object(o);T--;){var Y=d[T];if(k&&Y[2]?Y[1]!==o[Y[0]]:!(Y[0]in o))return!1}for(;++T<I;){Y=d[T];var $=Y[0],oe=o[$],ge=Y[1];if(k&&Y[2]){if(oe===void 0&&!($ in o))return!1}else{var ve=new To;if(y)var Pe=y(oe,ge,$,o,l,ve);if(!(Pe===void 0?Cf(ge,oe,mb|gb,y,ve):Pe))return!1}}return!0}var vb=_b;function yb(o){return o===o&&!Be(o)}var If=yb;function xb(o){for(var l=Mo(o),d=l.length;d--;){var y=l[d],T=o[y];l[d]=[y,T,If(T)]}return l}var bb=xb;function Sb(o,l){return function(d){return d==null?!1:d[o]===l&&(l!==void 0||o in Object(d))}}var Lf=Sb;function Mb(o){var l=bb(o);return l.length==1&&l[0][2]?Lf(l[0][0],l[0][1]):function(d){return d===o||vb(d,o,l)}}var Tb=Mb;function Eb(o,l){return o!=null&&l in Object(o)}var Ab=Eb;function wb(o,l,d){l=wr(l,o);for(var y=-1,T=l.length,I=!1;++y<T;){var k=hi(l[y]);if(!(I=o!=null&&d(o,k)))break;o=o[k]}return I||++y!=T?I:(T=o==null?0:o.length,!!T&&Dl(T)&&vo(k,T)&&(Me(o)||Bd(o)))}var Pb=wb;function Rb(o,l){return o!=null&&Pb(o,l,Ab)}var Cb=Rb,Ib=1,Lb=2;function Db(o,l){return me(o)&&If(l)?Lf(hi(o),l):function(d){var y=Di(d,o);return y===void 0&&y===l?Cb(d,o):Cf(l,y,Ib|Lb)}}var Nb=Db;function Ob(o){return function(l){return l==null?void 0:l[o]}}var Df=Ob;function Ub(o){return function(l){return gs(l,o)}}var Fb=Ub;function Bb(o){return me(o)?Df(hi(o)):Fb(o)}var kb=Bb;function zb(o){return typeof o=="function"?o:o==null?Aa:typeof o=="object"?Me(o)?Nb(o[0],o[1]):Tb(o):kb(o)}var Hb=zb;function Vb(o){return function(l,d,y){for(var T=-1,I=Object(l),k=y(l),Y=k.length;Y--;){var $=k[o?Y:++T];if(d(I[$],$,I)===!1)break}return l}}var Gb=Vb,Wb=Gb(),jb=Wb;function Xb(o,l){return o&&jb(o,l,Mo)}var qb=Xb,Yb=function(){return pe.Date.now()},Kl=Yb,Kb="Expected a function",$b=Math.max,Zb=Math.min;function Jb(o,l,d){var y,T,I,k,Y,$,oe=0,ge=!1,ve=!1,Pe=!0;if(typeof o!="function")throw new TypeError(Kb);l=S(l)||0,Be(d)&&(ge=!!d.leading,ve="maxWait"in d,I=ve?$b(S(d.maxWait)||0,l):I,Pe="trailing"in d?!!d.trailing:Pe);function Ye(Wt){var In=y,Qn=T;return y=T=void 0,oe=Wt,k=o.apply(Qn,In),k}function ze(Wt){return oe=Wt,Y=setTimeout(dt,l),ge?Ye(Wt):k}function ft(Wt){var In=Wt-$,Qn=Wt-oe,Si=l-In;return ve?Zb(Si,I-Qn):Si}function xt(Wt){var In=Wt-$,Qn=Wt-oe;return $===void 0||In>=l||In<0||ve&&Qn>=I}function dt(){var Wt=Kl();if(xt(Wt))return Lt(Wt);Y=setTimeout(dt,ft(Wt))}function Lt(Wt){return Y=void 0,Pe&&y?Ye(Wt):(y=T=void 0,k)}function Rn(){Y!==void 0&&clearTimeout(Y),oe=0,y=$=T=Y=void 0}function Wn(){return Y===void 0?k:Lt(Kl())}function Cn(){var Wt=Kl(),In=xt(Wt);if(y=arguments,T=this,$=Wt,In){if(Y===void 0)return ze($);if(ve)return clearTimeout(Y),Y=setTimeout(dt,l),Ye($)}return Y===void 0&&(Y=setTimeout(dt,l)),k}return Cn.cancel=Rn,Cn.flush=Wn,Cn}var Qb=Jb;function eS(o){var l=o==null?0:o.length;return l?o[l-1]:void 0}var tS=eS;function nS(o,l){return l.length<2?o:gs(o,Kd(l,0,-1))}var iS=nS;function rS(o){return typeof o=="number"&&o==En(o)}var sS=rS;function oS(o,l){var d={};return l=Hb(l),qb(o,function(y,T,I){Ni(d,T,l(y,T,I))}),d}var aS=oS;function cS(o,l){return l=wr(l,o),o=iS(o,l),o==null||delete o[hi(tS(l))]}var lS=cS,uS=9007199254740991,hS=Math.floor;function dS(o,l){var d="";if(!o||l<1||l>uS)return d;do l%2&&(d+=o),l=hS(l/2),l&&(o+=o);while(l);return d}var Nf=dS,fS=Df("length"),pS=fS,Of="\\ud800-\\udfff",mS="\\u0300-\\u036f",gS="\\ufe20-\\ufe2f",_S="\\u20d0-\\u20ff",vS=mS+gS+_S,yS="\\ufe0e\\ufe0f",xS="["+Of+"]",$l="["+vS+"]",Zl="\\ud83c[\\udffb-\\udfff]",bS="(?:"+$l+"|"+Zl+")",Uf="[^"+Of+"]",Ff="(?:\\ud83c[\\udde6-\\uddff]){2}",Bf="[\\ud800-\\udbff][\\udc00-\\udfff]",SS="\\u200d",kf=bS+"?",zf="["+yS+"]?",MS="(?:"+SS+"(?:"+[Uf,Ff,Bf].join("|")+")"+zf+kf+")*",TS=zf+kf+MS,ES="(?:"+[Uf+$l+"?",$l,Ff,Bf,xS].join("|")+")",Hf=RegExp(Zl+"(?="+Zl+")|"+ES+TS,"g");function AS(o){for(var l=Hf.lastIndex=0;Hf.test(o);)++l;return l}var wS=AS;function PS(o){return kl(o)?wS(o):pS(o)}var Vf=PS,RS=Math.ceil;function CS(o,l){l=l===void 0?" ":da(l);var d=l.length;if(d<2)return d?Nf(l,o):l;var y=Nf(l,RS(o/Vf(l)));return kl(l)?Fv(u0(y),0,o).join(""):y.slice(0,o)}var IS=CS;function LS(o,l,d){o=ms(o),l=En(l);var y=l?Vf(o):0;return l&&y<l?IS(l-y,d)+o:o}var Ao=LS;function DS(o,l){return o==null?!0:lS(o,l)}var Gf=DS,NS=5*1e3,OS=class{constructor(o){b(this,"_cache",new sr),b(this,"_keepHotUntapDebounce"),de(this,o)}get type(){return"Theatre_SheetObject_PublicAPI"}get props(){return J(this).propsP}get sheet(){return J(this).sheet.publicApi}get project(){return J(this).sheet.project.publicApi}get address(){return g({},J(this).address)}_valuesPrism(){return this._cache.get("_valuesPrism",()=>{const o=J(this);return(0,xo.prism)(()=>(0,xo.val)(o.getValues().getValue()))})}onValuesChange(o,l){return Su(this._valuesPrism(),o,l)}get value(){const o=this._valuesPrism();{if(!o.isHot){this._keepHotUntapDebounce!=null&&this._keepHotUntapDebounce.flush();const l=o.keepHot();this._keepHotUntapDebounce=Qb(()=>{l(),this._keepHotUntapDebounce=void 0},NS)}this._keepHotUntapDebounce&&this._keepHotUntapDebounce()}return o.getValue()}set initialValue(o){J(this).setInitialValue(o)}};function US(o){const l=new WeakMap;return d=>(l.has(d)||l.set(d,o(d)),l.get(d))}function Da(o){return o.type==="compound"||o.type==="enum"}function Jl(o,l){if(!o)return;const[d,...y]=l;if(d===void 0)return o;if(!Da(o))return;const T=o.type==="enum"?o.cases[d]:o.props[d];return Jl(T,y)}function FS(o){return!Da(o)}var BS=class{constructor(o,l,d){this.sheet=o,this.template=l,this.nativeObject=d,b(this,"$$isPointerToPrismProvider",!0),b(this,"address"),b(this,"publicApi"),b(this,"_initialValue",new Bt.Atom({})),b(this,"_cache",new sr),b(this,"_logger"),b(this,"_internalUtilCtx"),this._logger=o._logger.named("SheetObject",l.address.objectKey),this._logger._trace("creating object"),this._internalUtilCtx={logger:this._logger.utilFor.internal()},this.address=x(g({},l.address),{sheetInstanceId:o.address.sheetInstanceId}),this.publicApi=new OS(this)}get type(){return"Theatre_SheetObject"}getValues(){return this._cache.get("getValues()",()=>(0,Bt.prism)(()=>{const o=(0,Bt.val)(this.template.getDefaultValues()),l=(0,Bt.val)(this._initialValue.pointer),d=Bt.prism.memo("withInitialCache",()=>new WeakMap,[]),y=Cr(o,l,d),T=(0,Bt.val)(this.template.getStaticValues()),I=Bt.prism.memo("withStatics",()=>new WeakMap,[]);let Y=Cr(y,T,I),$;{const ge=Bt.prism.memo("seq",()=>this.getSequencedValues(),[]),ve=Bt.prism.memo("withSeqsCache",()=>new WeakMap,[]);$=(0,Bt.val)((0,Bt.val)(ge)),Y=Cr(Y,$,ve)}return ba("finalAtom",Y).pointer}))}getValueByPointer(o){const l=(0,Bt.val)(this.getValues()),{path:d}=(0,Bt.getPointerParts)(o);return(0,Bt.val)(Ir(l,d))}pointerToPrism(o){const{path:l}=(0,Bt.getPointerParts)(o);return(0,Bt.prism)(()=>{const d=(0,Bt.val)(this.getValues());return(0,Bt.val)(Ir(d,l))})}getSequencedValues(){return(0,Bt.prism)(()=>{const o=Bt.prism.memo("tracksToProcess",()=>this.template.getArrayOfValidSequenceTracks(),[]),l=(0,Bt.val)(o),d=new Bt.Atom({}),y=(0,Bt.val)(this.template.configPointer);return Bt.prism.effect("processTracks",()=>{const T=[];for(const{trackId:I,pathToProp:k}of l){const Y=this._trackIdToPrism(I),$=Jl(y,k),oe=$.deserializeAndSanitize,ge=$.interpolate,ve=()=>{const Ye=Y.getValue();if(!Ye)return d.setByPointer(Lt=>Ir(Lt,k),void 0);const ze=oe(Ye.left),ft=ze===void 0?$.default:ze;if(Ye.right===void 0)return d.setByPointer(Lt=>Ir(Lt,k),ft);const xt=oe(Ye.right),dt=xt===void 0?$.default:xt;return d.setByPointer(Lt=>Ir(Lt,k),ge(ft,dt,Ye.progression))},Pe=Y.onStale(ve);ve(),T.push(Pe)}return()=>{for(const I of T)I()}},[y,...l]),d.pointer})}_trackIdToPrism(o){const l=this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[o],d=this.sheet.getSequence().positionPrism;return Tl(this._internalUtilCtx,l,d)}get propsP(){return this._cache.get("propsP",()=>(0,Bt.pointer)({root:this,path:[]}))}validateValue(o,l){}setInitialValue(o){this.validateValue(this.propsP,o),this._initialValue.set(o)}};function Kt(o){return function(d,y){return o(d,y())}}var $n={_hmm:Zn(524),_todo:Zn(522),_error:Zn(521),errorDev:Zn(529),errorPublic:Zn(545),_kapow:Zn(268),_warn:Zn(265),warnDev:Zn(273),warnPublic:Zn(289),_debug:Zn(137),debugDev:Zn(145),_trace:Zn(73),traceDev:Zn(81)};function Zn(o){return Object.freeze({audience:Or(o,8)?"internal":Or(o,16)?"dev":"public",category:Or(o,4)?"troubleshooting":Or(o,2)?"todo":"general",level:Or(o,512)?512:Or(o,256)?256:Or(o,128)?128:64})}function Or(o,l){return(o&l)===l}function $t(o,l){return((l&32)===32?!0:(l&16)===16?o.dev:(l&8)===8?o.internal:!1)&&o.min<=l}var Oi={loggingConsoleStyle:!0,loggerConsoleStyle:!0,includes:Object.freeze({internal:!1,dev:!1,min:256}),filtered:function(){},include:function(){return{}},create:null,creatExt:null,named(o,l,d){return this.create({names:[...o.names,{name:l,key:d}]})},style:{bold:void 0,italic:void 0,cssMemo:new Map([["",""]]),collapseOnRE:/[a-z- ]+/g,color:void 0,collapsed(o){if(o.length<5)return o;const l=o.replace(this.collapseOnRE,"");return this.cssMemo.has(l)||this.cssMemo.set(l,this.css(o)),l},css(o){var l,d,y,T;const I=this.cssMemo.get(o);if(I)return I;let k="color:".concat((d=(l=this.color)==null?void 0:l.call(this,o))!=null?d:"hsl(".concat((o.charCodeAt(0)+o.charCodeAt(o.length-1))%360,", 100%, 60%)"));return(y=this.bold)!=null&&y.test(o)&&(k+=";font-weight:600"),(T=this.italic)!=null&&T.test(o)&&(k+=";font-style:italic"),this.cssMemo.set(o,k),k}}};function Wf(o=console,l={}){const d=x(g({},Oi),{includes:g({},Oi.includes)}),y={styled:HS.bind(d,o),noStyle:GS.bind(d,o)},T=zS.bind(d);function I(){return d.loggingConsoleStyle&&d.loggerConsoleStyle?y.styled:y.noStyle}return d.create=I(),{configureLogger(k){var Y;k==="console"?(d.loggerConsoleStyle=Oi.loggerConsoleStyle,d.create=I()):k.type==="console"?(d.loggerConsoleStyle=(Y=k.style)!=null?Y:Oi.loggerConsoleStyle,d.create=I()):k.type==="keyed"?(d.creatExt=$=>k.keyed($.names),d.create=T):k.type==="named"&&(d.creatExt=kS.bind(null,k.named),d.create=T)},configureLogging(k){var Y,$,oe,ge,ve;d.includes.dev=(Y=k.dev)!=null?Y:Oi.includes.dev,d.includes.internal=($=k.internal)!=null?$:Oi.includes.internal,d.includes.min=(oe=k.min)!=null?oe:Oi.includes.min,d.include=(ge=k.include)!=null?ge:Oi.include,d.loggingConsoleStyle=(ve=k.consoleStyle)!=null?ve:Oi.loggingConsoleStyle,d.create=I()},getLogger(){return d.create({names:[]})}}}function kS(o,l){const d=[];for(let{name:y,key:T}of l.names)d.push(T==null?y:"".concat(y," (").concat(T,")"));return o(d)}function zS(o){const l=g(g({},this.includes),this.include(o)),d=this.filtered,y=this.named.bind(this,o),T=this.creatExt(o),I=$t(l,524),k=$t(l,522),Y=$t(l,521),$=$t(l,529),oe=$t(l,545),ge=$t(l,265),ve=$t(l,268),Pe=$t(l,273),Ye=$t(l,289),ze=$t(l,137),ft=$t(l,145),xt=$t(l,73),dt=$t(l,81),Lt=I?T.error.bind(T,$n._hmm):d.bind(o,524),Rn=k?T.error.bind(T,$n._todo):d.bind(o,522),Wn=Y?T.error.bind(T,$n._error):d.bind(o,521),Cn=$?T.error.bind(T,$n.errorDev):d.bind(o,529),Wt=oe?T.error.bind(T,$n.errorPublic):d.bind(o,545),In=ve?T.warn.bind(T,$n._kapow):d.bind(o,268),Qn=ge?T.warn.bind(T,$n._warn):d.bind(o,265),Si=Pe?T.warn.bind(T,$n.warnDev):d.bind(o,273),Hr=Ye?T.warn.bind(T,$n.warnPublic):d.bind(o,273),Vr=ze?T.debug.bind(T,$n._debug):d.bind(o,137),Gr=ft?T.debug.bind(T,$n.debugDev):d.bind(o,145),Wr=xt?T.trace.bind(T,$n._trace):d.bind(o,73),jr=dt?T.trace.bind(T,$n.traceDev):d.bind(o,81),ln={_hmm:Lt,_todo:Rn,_error:Wn,errorDev:Cn,errorPublic:Wt,_kapow:In,_warn:Qn,warnDev:Si,warnPublic:Hr,_debug:Vr,debugDev:Gr,_trace:Wr,traceDev:jr,lazy:{_hmm:I?Kt(Lt):Lt,_todo:k?Kt(Rn):Rn,_error:Y?Kt(Wn):Wn,errorDev:$?Kt(Cn):Cn,errorPublic:oe?Kt(Wt):Wt,_kapow:ve?Kt(In):In,_warn:ge?Kt(Qn):Qn,warnDev:Pe?Kt(Si):Si,warnPublic:Ye?Kt(Hr):Hr,_debug:ze?Kt(Vr):Vr,debugDev:ft?Kt(Gr):Gr,_trace:xt?Kt(Wr):Wr,traceDev:dt?Kt(jr):jr},named:y,utilFor:{internal(){return{debug:ln._debug,error:ln._error,warn:ln._warn,trace:ln._trace,named(ei,Zt){return ln.named(ei,Zt).utilFor.internal()}}},dev(){return{debug:ln.debugDev,error:ln.errorDev,warn:ln.warnDev,trace:ln.traceDev,named(ei,Zt){return ln.named(ei,Zt).utilFor.dev()}}},public(){return{error:ln.errorPublic,warn:ln.warnPublic,debug(ei,Zt){ln._warn('(public "debug" filtered out) '.concat(ei),Zt)},trace(ei,Zt){ln._warn('(public "trace" filtered out) '.concat(ei),Zt)},named(ei,Zt){return ln.named(ei,Zt).utilFor.public()}}}}};return ln}function HS(o,l){const d=g(g({},this.includes),this.include(l)),y=[];let T="";for(let $=0;$<l.names.length;$++){const{name:oe,key:ge}=l.names[$];if(T+=" %c".concat(oe),y.push(this.style.css(oe)),ge!=null){const ve="%c#".concat(ge);T+=ve,y.push(this.style.css(ve))}}const I=this.filtered,k=this.named.bind(this,l),Y=[T,...y];return jf(I,l,d,o,Y,VS(Y),k)}function VS(o){const l=o.slice(0);for(let d=1;d<l.length;d++)l[d]+=";background-color:#e0005a;padding:2px;color:white";return l}function GS(o,l){const d=g(g({},this.includes),this.include(l));let y="";for(let Y=0;Y<l.names.length;Y++){const{name:$,key:oe}=l.names[Y];y+=" ".concat($),oe!=null&&(y+="#".concat(oe))}const T=this.filtered,I=this.named.bind(this,l),k=[y];return jf(T,l,d,o,k,k,I)}function jf(o,l,d,y,T,I,k){const Y=$t(d,524),$=$t(d,522),oe=$t(d,521),ge=$t(d,529),ve=$t(d,545),Pe=$t(d,265),Ye=$t(d,268),ze=$t(d,273),ft=$t(d,289),xt=$t(d,137),dt=$t(d,145),Lt=$t(d,73),Rn=$t(d,81),Wn=Y?y.error.bind(y,...T):o.bind(l,524),Cn=$?y.error.bind(y,...T):o.bind(l,522),Wt=oe?y.error.bind(y,...T):o.bind(l,521),In=ge?y.error.bind(y,...T):o.bind(l,529),Qn=ve?y.error.bind(y,...T):o.bind(l,545),Si=Ye?y.warn.bind(y,...I):o.bind(l,268),Hr=Pe?y.warn.bind(y,...T):o.bind(l,265),Vr=ze?y.warn.bind(y,...T):o.bind(l,273),Gr=ft?y.warn.bind(y,...T):o.bind(l,273),Wr=xt?y.info.bind(y,...T):o.bind(l,137),jr=dt?y.info.bind(y,...T):o.bind(l,145),ln=Lt?y.debug.bind(y,...T):o.bind(l,73),ei=Rn?y.debug.bind(y,...T):o.bind(l,81),Zt={_hmm:Wn,_todo:Cn,_error:Wt,errorDev:In,errorPublic:Qn,_kapow:Si,_warn:Hr,warnDev:Vr,warnPublic:Gr,_debug:Wr,debugDev:jr,_trace:ln,traceDev:ei,lazy:{_hmm:Y?Kt(Wn):Wn,_todo:$?Kt(Cn):Cn,_error:oe?Kt(Wt):Wt,errorDev:ge?Kt(In):In,errorPublic:ve?Kt(Qn):Qn,_kapow:Ye?Kt(Si):Si,_warn:Pe?Kt(Hr):Hr,warnDev:ze?Kt(Vr):Vr,warnPublic:ft?Kt(Gr):Gr,_debug:xt?Kt(Wr):Wr,debugDev:dt?Kt(jr):jr,_trace:Lt?Kt(ln):ln,traceDev:Rn?Kt(ei):ei},named:k,utilFor:{internal(){return{debug:Zt._debug,error:Zt._error,warn:Zt._warn,trace:Zt._trace,named(Bi,ki){return Zt.named(Bi,ki).utilFor.internal()}}},dev(){return{debug:Zt.debugDev,error:Zt.errorDev,warn:Zt.warnDev,trace:Zt.traceDev,named(Bi,ki){return Zt.named(Bi,ki).utilFor.dev()}}},public(){return{error:Zt.errorPublic,warn:Zt.warnPublic,debug(Bi,ki){Zt._warn('(public "debug" filtered out) '.concat(Bi),ki)},trace(Bi,ki){Zt._warn('(public "trace" filtered out) '.concat(Bi),ki)},named(Bi,ki){return Zt.named(Bi,ki).utilFor.public()}}}}};return Zt}var Xf=Wf(console,{});Xf.configureLogging({dev:!0,min:64});var Na=Xf.getLogger().named("Theatre.js (default logger)").utilFor.dev(),qf=new WeakMap;function WS(o){const l=qf.get(o);if(l)return l;const d=new Map;return qf.set(o,d),Yf([],o,d),d}function Yf(o,l,d){for(const[y,T]of Object.entries(l.props))if(!Da(T)){const I=[...o,y];d.set(JSON.stringify(I),d.size),Kf(I,T,d)}for(const[y,T]of Object.entries(l.props))if(Da(T)){const I=[...o,y];d.set(JSON.stringify(I),d.size),Kf(I,T,d)}}function Kf(o,l,d){if(l.type==="compound")Yf(o,l,d);else{if(l.type==="enum")throw new Error("Enums aren't supported yet");d.set(JSON.stringify(o),d.size)}}function $f(o){return typeof o=="object"&&o!==null&&Object.keys(o).length===0}var jS=class{constructor(o,l,d,y,T){this.sheetTemplate=o,b(this,"address"),b(this,"type","Theatre_SheetObjectTemplate"),b(this,"_config"),b(this,"_temp_actions_atom"),b(this,"_cache",new sr),b(this,"project"),b(this,"pointerToSheetState"),b(this,"pointerToStaticOverrides"),this.address=x(g({},o.address),{objectKey:l}),this._config=new hn.Atom(y),this._temp_actions_atom=new hn.Atom(T),this.project=o.project,this.pointerToSheetState=this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId],this.pointerToStaticOverrides=this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey]}get staticConfig(){return this._config.get()}get configPointer(){return this._config.pointer}get _temp_actions(){return this._temp_actions_atom.get()}get _temp_actionsPointer(){return this._temp_actions_atom.pointer}createInstance(o,l,d){return this._config.set(d),new BS(o,this,l)}reconfigure(o){this._config.set(o)}_temp_setActions(o){this._temp_actions_atom.set(o)}getDefaultValues(){return this._cache.get("getDefaultValues()",()=>(0,hn.prism)(()=>{const o=(0,hn.val)(this.configPointer);return Sl(o)}))}getStaticValues(){return this._cache.get("getStaticValues",()=>(0,hn.prism)(()=>{var o;const l=(o=(0,hn.val)(this.pointerToStaticOverrides))!=null?o:{};return(0,hn.val)(this.configPointer).deserializeAndSanitize(l)||{}}))}getArrayOfValidSequenceTracks(){return this._cache.get("getArrayOfValidSequenceTracks",()=>(0,hn.prism)(()=>{const o=this.project.pointers.historic.sheetsById[this.address.sheetId],l=(0,hn.val)(o.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath);if(!l)return re;const d=[];if(!l)return re;const y=(0,hn.val)(this.configPointer),T=Object.entries(l);for(const[k,Y]of T){const $=XS(k);if(!$)continue;const oe=Jl(y,$);oe&&FS(oe)&&d.push({pathToProp:$,trackId:Y})}const I=WS(y);return d.sort((k,Y)=>{const $=k.pathToProp,oe=Y.pathToProp,ge=I.get(JSON.stringify($)),ve=I.get(JSON.stringify(oe));return ge>ve?1:-1}),d.length===0?re:d}))}getMapOfValidSequenceTracks_forStudio(){return this._cache.get("getMapOfValidSequenceTracks_forStudio",()=>(0,hn.prism)(()=>{const o=(0,hn.val)(this.getArrayOfValidSequenceTracks());let l={};for(const{pathToProp:d,trackId:y}of o)vs(l,d,y);return l}))}getStaticButNotSequencedOverrides(){return this._cache.get("getStaticButNotSequencedOverrides",()=>(0,hn.prism)(()=>{const o=(0,hn.val)(this.getStaticValues()),l=(0,hn.val)(this.getArrayOfValidSequenceTracks()),d=wx(o);for(const{pathToProp:y}of l){Gf(d,y);let T=y.slice(0,-1);for(;T.length>0;){const I=pa(d,T);if(!$f(I))break;Gf(d,T),T=T.slice(0,-1)}}if(!$f(d))return d}))}getDefaultsAtPointer(o){const{path:l}=(0,hn.getPointerParts)(o),d=this.getDefaultValues().getValue();return pa(d,l)}};function XS(o){try{return JSON.parse(o)}catch{Na.warn("property ".concat(JSON.stringify(o)," cannot be parsed. Skipping."));return}}var Zf=fn(),qS=US(o=>JSON.stringify(o));A(O());var YS=class extends Error{},wo=class extends YS{},Jf=fn(),KS=fn(),$S=fn(),yn=fn();function ar(){let o,l;const d=new Promise((T,I)=>{o=k=>{T(k),y.status="resolved"},l=k=>{I(k),y.status="rejected"}}),y={resolve:o,reject:l,promise:d,status:"pending"};return y}var ZS=()=>{},Oa=ZS,JS=fn(),QS=class{constructor(){b(this,"_stopPlayCallback",Oa),b(this,"_state",new JS.Atom({position:0,playing:!1})),b(this,"statePointer"),this.statePointer=this._state.pointer}destroy(){}pause(){this._stopPlayCallback(),this.playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.setByPointer(l=>l.position,o)}getCurrentPosition(){return this._state.get().position}get playing(){return this._state.get().playing}set playing(o){this._state.setByPointer(l=>l.playing,o)}play(o,l,d,y,T){this.playing&&this.pause(),this.playing=!0;const I=l[1]-l[0];{const Pe=this.getCurrentPosition();Pe<l[0]||Pe>l[1]?y==="normal"||y==="alternate"?this._updatePositionInState(l[0]):(y==="reverse"||y==="alternateReverse")&&this._updatePositionInState(l[1]):y==="normal"||y==="alternate"?Pe===l[1]&&this._updatePositionInState(l[0]):Pe===l[0]&&this._updatePositionInState(l[1])}const k=ar(),Y=T.time,$=I*o;let oe=this.getCurrentPosition()-l[0];(y==="reverse"||y==="alternateReverse")&&(oe=l[1]-this.getCurrentPosition());const ge=Pe=>{const ze=Math.max(Pe-Y,0)/1e3,ft=Math.min(ze*d+oe,$);if(ft!==$){const xt=Math.floor(ft/I);let dt=ft/I%1*I;if(y!=="normal")if(y==="reverse")dt=I-dt;else{const Lt=xt%2===0;y==="alternate"?Lt||(dt=I-dt):Lt&&(dt=I-dt)}this._updatePositionInState(dt+l[0]),ve()}else{if(y==="normal")this._updatePositionInState(l[1]);else if(y==="reverse")this._updatePositionInState(l[0]);else{const xt=(o-1)%2===0;y==="alternate"?xt?this._updatePositionInState(l[1]):this._updatePositionInState(l[0]):xt?this._updatePositionInState(l[0]):this._updatePositionInState(l[1])}this.playing=!1,k.resolve(!0)}};this._stopPlayCallback=()=>{T.offThisOrNextTick(ge),T.offNextTick(ge),this.playing&&k.resolve(!1)};const ve=()=>T.onNextTick(ge);return T.onThisOrNextTick(ge),k.promise}playDynamicRange(o,l){this.playing&&this.pause(),this.playing=!0;const d=ar(),y=o.keepHot();d.promise.then(y,y);let T=l.time;const I=Y=>{const $=Math.max(Y-T,0);T=Y;const oe=$/1e3,ge=this.getCurrentPosition(),ve=o.getValue();if(ge<ve[0]||ge>ve[1])this.gotoPosition(ve[0]);else{let Pe=ge+oe;Pe>ve[1]&&(Pe=ve[0]+(Pe-ve[1])),this.gotoPosition(Pe)}k()};this._stopPlayCallback=()=>{l.offThisOrNextTick(I),l.offNextTick(I),d.resolve(!1)};const k=()=>l.onNextTick(I);return l.onThisOrNextTick(I),d.promise}},eM=fn(),tM="__TheatreJS_StudioBundle",Ql="__TheatreJS_CoreBundle",nM="__TheatreJS_Notifications",Ua=o=>(...l)=>{var d;switch(o){case"success":{Na.debug(l.slice(0,2).join(`
`));break}case"info":{Na.debug(l.slice(0,2).join(`
`));break}case"warning":{Na.warn(l.slice(0,2).join(`
`));break}}return typeof window<"u"?(d=window[nM])==null?void 0:d.notify[o](...l):void 0},Ss={warning:Ua("warning"),success:Ua("success"),info:Ua("info"),error:Ua("error")};typeof window<"u"&&(window.addEventListener("error",o=>{Ss.error("An error occurred","<pre>".concat(o.message,`</pre>

See **console** for details.`))}),window.addEventListener("unhandledrejection",o=>{Ss.error("An error occurred","<pre>".concat(o.reason,`</pre>

See **console** for details.`))}));var iM=class{constructor(o,l,d){this._decodedBuffer=o,this._audioContext=l,this._nodeDestination=d,b(this,"_mainGain"),b(this,"_state",new eM.Atom({position:0,playing:!1})),b(this,"statePointer"),b(this,"_stopPlayCallback",Oa),this.statePointer=this._state.pointer,this._mainGain=this._audioContext.createGain(),this._mainGain.connect(this._nodeDestination)}playDynamicRange(o,l){const d=ar();this._playing&&this.pause(),this._playing=!0;let y;const T=()=>{y==null||y(),y=this._loopInRange(o.getValue(),l).stop},I=o.onStale(T);return T(),this._stopPlayCallback=()=>{y==null||y(),I(),d.resolve(!1)},d.promise}_loopInRange(o,l){let y=this.getCurrentPosition();const T=o[1]-o[0];y<o[0]||y>o[1]?this._updatePositionInState(o[0]):y===o[1]&&this._updatePositionInState(o[0]),y=this.getCurrentPosition();const I=this._audioContext.createBufferSource();I.buffer=this._decodedBuffer,I.connect(this._mainGain),I.playbackRate.value=1,I.loop=!0,I.loopStart=o[0],I.loopEnd=o[1];const k=l.time;let Y=y-o[0];I.start(0,y);const $=ve=>{let ft=(Math.max(ve-k,0)/1e3*1+Y)/T%1*T;this._updatePositionInState(ft+o[0]),oe()},oe=()=>l.onNextTick($);return l.onThisOrNextTick($),{stop:()=>{I.stop(),I.disconnect(),l.offThisOrNextTick($),l.offNextTick($)}}}get _playing(){return this._state.get().playing}set _playing(o){this._state.setByPointer(l=>l.playing,o)}destroy(){}pause(){this._stopPlayCallback(),this._playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.reduce(l=>x(g({},l),{position:o}))}getCurrentPosition(){return this._state.get().position}play(o,l,d,y,T){this._playing&&this.pause(),this._playing=!0;let I=this.getCurrentPosition();const k=l[1]-l[0];if(y!=="normal")throw new wo('Audio-controlled sequences can only be played in the "normal" direction. '+"'".concat(y,"' given."));I<l[0]||I>l[1]?this._updatePositionInState(l[0]):I===l[1]&&this._updatePositionInState(l[0]),I=this.getCurrentPosition();const Y=ar(),$=this._audioContext.createBufferSource();$.buffer=this._decodedBuffer,$.connect(this._mainGain),$.playbackRate.value=d,o>1e3&&(Ss.warning("Can't play sequences with audio more than 1000 times","The sequence will still play, but only 1000 times. The `iterationCount: ".concat(o,"` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),[{url:"https://www.theatrejs.com/docs/latest/manual/audio",title:"Using Audio"},{url:"https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",title:"Audio API"}]),o=1e3),o>1&&($.loop=!0,$.loopStart=l[0],$.loopEnd=l[1]);const oe=T.time;let ge=I-l[0];const ve=k*o;$.start(0,I,ve-ge);const Pe=ft=>{const dt=Math.max(ft-oe,0)/1e3,Lt=Math.min(dt*d+ge,ve);if(Lt!==ve){let Rn=Lt/k%1*k;this._updatePositionInState(Rn+l[0]),ze()}else this._updatePositionInState(l[1]),this._playing=!1,Ye(),Y.resolve(!0)},Ye=()=>{$.stop(),$.disconnect()};this._stopPlayCallback=()=>{Ye(),T.offThisOrNextTick(Pe),T.offNextTick(Pe),this._playing&&Y.resolve(!1)};const ze=()=>T.onNextTick(Pe);return T.onThisOrNextTick(Pe),Y.promise}},rM=fn(),Qf=0;function eu(o){var l;const d=k=>{y.tick(k)},y=new rM.Ticker({onActive(){var k;(k=o==null?void 0:o.start)==null||k.call(o)},onDormant(){var k;(k=o==null?void 0:o.stop)==null||k.call(o)}}),T={tick:d,id:Qf++,name:(l=o==null?void 0:o.name)!=null?l:"CustomRafDriver-".concat(Qf),type:"Theatre_RafDriver_PublicAPI"},I={type:"Theatre_RafDriver_PrivateAPI",publicApi:T,ticker:y,start:o==null?void 0:o.start,stop:o==null?void 0:o.stop};return de(T,I),T}function sM(){let o=null;const y=eu({name:"DefaultCoreRafDriver",start:()=>{if(typeof window<"u"){const T=I=>{y.tick(I),o=window.requestAnimationFrame(T)};o=window.requestAnimationFrame(T)}else y.tick(0),setTimeout(()=>y.tick(1),0)},stop:()=>{typeof window<"u"&&o!==null&&window.cancelAnimationFrame(o)}});return y}var Fa;function ep(){return Fa||oM(sM()),Fa}function tp(){return ep().ticker}function oM(o){if(Fa)throw new Error("`setCoreRafDriver()` is already called.");Fa=J(o)}var aM=class{get type(){return"Theatre_Sequence_PublicAPI"}constructor(o){de(this,o)}play(o){const l=J(this);if(l._project.isReady()){const d=o!=null&&o.rafDriver?J(o.rafDriver).ticker:tp();return l.play(o??{},d)}else{const d=ar();return d.resolve(!0),d.promise}}pause(){J(this).pause()}get position(){return J(this).position}set position(o){J(this).position=o}__experimental_getKeyframes(o){return J(this).getKeyframesOfSimpleProp(o)}async attachAudio(o){const{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:T}=await cM(o),I=new iM(y,l,T);return J(this).replacePlaybackController(I),{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:T}}get pointer(){return J(this).pointer}};async function cM(o){function l(){if(o.audioContext)return Promise.resolve(o.audioContext);const oe=new AudioContext;return oe.state==="running"||typeof window>"u"?Promise.resolve(oe):new Promise(ge=>{const ve=()=>{oe.resume().catch(ze=>{console.error(ze)})},Pe=["mousedown","keydown","touchstart"],Ye={capture:!0,passive:!1};Pe.forEach(ze=>{window.addEventListener(ze,ve,Ye)}),oe.addEventListener("statechange",()=>{oe.state==="running"&&(Pe.forEach(ze=>{window.removeEventListener(ze,ve,Ye)}),ge(oe))})})}async function d(){if(o.source instanceof AudioBuffer)return o.source;const oe=ar();if(typeof o.source!="string")throw new Error("Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer.");let ge;try{ge=await fetch(o.source)}catch(ze){throw console.error(ze),new Error("Could not fetch '".concat(o.source,"'. Network error logged above."))}let ve;try{ve=await ge.arrayBuffer()}catch(ze){throw console.error(ze),new Error("Could not read '".concat(o.source,"' as an arrayBuffer."))}(await y).decodeAudioData(ve,oe.resolve,oe.reject);let Ye;try{Ye=await oe.promise}catch(ze){throw console.error(ze),new Error("Could not decode ".concat(o.source," as an audio file."))}return Ye}const y=l(),T=d(),[I,k]=await Promise.all([y,T]),Y=o.destinationNode||I.destination,$=I.createGain();return $.connect(Y),{audioContext:I,decodedBuffer:k,gainNode:$,destinationNode:Y}}var lM=uM("Theatre_SheetObject");function uM(o){return l=>typeof l=="object"&&!!l&&l.type===o}var hM=class{constructor(o,l,d,y,T){this._project=o,this._sheet=l,this._lengthD=d,this._subUnitsPerUnitD=y,b(this,"address"),b(this,"publicApi"),b(this,"_playbackControllerBox"),b(this,"_prismOfStatePointer"),b(this,"_positionD"),b(this,"_positionFormatterD"),b(this,"_playableRangeD"),b(this,"pointer",(0,$S.pointer)({root:this,path:[]})),b(this,"$$isPointerToPrismProvider",!0),b(this,"_logger"),b(this,"closestGridPosition",I=>{const Y=1/this.subUnitsPerUnit;return parseFloat((Math.round(I/Y)*Y).toFixed(3))}),this._logger=o._logger.named("Sheet",l.address.sheetId).named("Instance",l.address.sheetInstanceId),this.address=x(g({},this._sheet.address),{sequenceName:"default"}),this.publicApi=new aM(this),this._playbackControllerBox=new KS.Atom(T??new QS),this._prismOfStatePointer=(0,yn.prism)(()=>this._playbackControllerBox.prism.getValue().statePointer),this._positionD=(0,yn.prism)(()=>{const I=this._prismOfStatePointer.getValue();return(0,yn.val)(I.position)}),this._positionFormatterD=(0,yn.prism)(()=>{const I=(0,yn.val)(this._subUnitsPerUnitD);return new dM(I)})}get type(){return"Theatre_Sequence"}pointerToPrism(o){const{path:l}=(0,Jf.getPointerParts)(o);if(l.length===0)return(0,yn.prism)(()=>({length:(0,yn.val)(this.pointer.length),playing:(0,yn.val)(this.pointer.playing),position:(0,yn.val)(this.pointer.position),subUnitsPerUnit:(0,yn.val)(this.pointer.subUnitsPerUnit)}));if(l.length>1)return(0,yn.prism)(()=>{});const[d]=l;return d==="length"?this._lengthD:d==="subUnitsPerUnit"?this._subUnitsPerUnitD:d==="position"?this._positionD:d==="playing"?(0,yn.prism)(()=>(0,yn.val)(this._prismOfStatePointer.getValue().playing)):(0,yn.prism)(()=>{})}getKeyframesOfSimpleProp(o){const{path:l,root:d}=(0,Jf.getPointerParts)(o);if(!lM(d))throw new wo("Argument prop must be a pointer to a SheetObject property");const y=(0,yn.val)(this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[d.address.objectKey]);if(!y)return[];const{trackData:T,trackIdByPropPath:I}=y,k=qS(l),Y=I[k];if(!Y)return[];const $=T[Y];return $?$.keyframes:[]}get positionFormatter(){return this._positionFormatterD.getValue()}get prismOfStatePointer(){return this._prismOfStatePointer}get length(){return this._lengthD.getValue()}get positionPrism(){return this._positionD}get position(){return this._playbackControllerBox.get().getCurrentPosition()}get subUnitsPerUnit(){return this._subUnitsPerUnitD.getValue()}get positionSnappedToGrid(){return this.closestGridPosition(this.position)}set position(o){let l=o;this.pause(),l>this.length&&(l=this.length);const d=this.length;this._playbackControllerBox.get().gotoPosition(l>d?d:l)}getDurationCold(){return this._lengthD.getValue()}get playing(){return(0,yn.val)(this._playbackControllerBox.get().statePointer.playing)}_makeRangeFromSequenceTemplate(){return(0,yn.prism)(()=>[0,(0,yn.val)(this._lengthD)])}playDynamicRange(o,l){return this._playbackControllerBox.get().playDynamicRange(o,l)}async play(o,l){const d=this.length,y=o&&o.range?o.range:[0,d],T=o&&typeof o.iterationCount=="number"?o.iterationCount:1,I=o&&typeof o.rate<"u"?o.rate:1,k=o&&o.direction?o.direction:"normal";return await this._play(T,[y[0],y[1]],I,k,l)}_play(o,l,d,y,T){return this._playbackControllerBox.get().play(o,l,d,y,T)}pause(){this._playbackControllerBox.get().pause()}replacePlaybackController(o){this.pause();const l=this._playbackControllerBox.get();this._playbackControllerBox.set(o);const d=l.getCurrentPosition();l.destroy(),o.gotoPosition(d)}},dM=class{constructor(o){this._fps=o}formatSubUnitForGrid(o){const l=o%1,d=1/this._fps;return Math.round(l/d)+"f"}formatFullUnitForGrid(o){let l=o,d="";if(l>=Ms){const T=Math.floor(l/Ms);d+=T+"h",l=l%Ms}if(l>=Fr){const T=Math.floor(l/Fr);d+=T+"m",l=l%Fr}if(l>=Ur){const T=Math.floor(l/Ur);d+=T+"s",l=l%Ur}const y=1/this._fps;if(l>=y){const T=Math.floor(l/y);d+=T+"f",l=l%y}return d.length===0?"0s":d}formatForPlayhead(o){let l=o,d="";if(l>=Ms){const T=Math.floor(l/Ms);d+=Ao(T.toString(),2,"0")+"h",l=l%Ms}if(l>=Fr){const T=Math.floor(l/Fr);d+=Ao(T.toString(),2,"0")+"m",l=l%Fr}else d.length>0&&(d+="00m");if(l>=Ur){const T=Math.floor(l/Ur);d+=Ao(T.toString(),2,"0")+"s",l=l%Ur}else d+="00s";const y=1/this._fps;if(l>=y){const T=Math.round(l/y);d+=Ao(T.toString(),2,"0")+"f",l=l%y}else l/y>.98?(d+=Ao("1",2,"0")+"f",l=l%y):d+="00f";return d.length===0?"00s00f":d}formatBasic(o){return o.toFixed(2)+"s"}},Ur=1,Fr=Ur*60,Ms=Fr*60,tu={};v(tu,{boolean:()=>cp,compound:()=>iu,file:()=>xM,image:()=>SM,number:()=>ap,rgba:()=>wM,string:()=>lp,stringLiteral:()=>LM});function np(o,l){return o.length<=l?o:o.substr(0,l-3)+"..."}var fM=o=>typeof o=="string"?'string("'.concat(np(o,10),'")'):typeof o=="number"?"number(".concat(np(String(o),10),")"):o===null?"null":o===void 0?"undefined":typeof o=="boolean"?String(o):Array.isArray(o)?"array":typeof o=="object"?"object":"unknown",ip=fM;function pM(o,{removeAlphaIfOpaque:l=!1}={}){const d=(o.a*255|256).toString(16).slice(1),y=(o.r*255|256).toString(16).slice(1)+(o.g*255|256).toString(16).slice(1)+(o.b*255|256).toString(16).slice(1)+(l&&d==="ff"?"":d);return"#".concat(y)}function nu(o){return x(g({},o),{toString(){return pM(this,{removeAlphaIfOpaque:!0})}})}function mM(o){return Object.fromEntries(Object.entries(o).map(([l,d])=>[l,nf(d,0,1)]))}function gM(o){function l(d){return d>=.0031308?1.055*d**(1/2.4)-.055:12.92*d}return mM({r:l(o.r),g:l(o.g),b:l(o.b),a:o.a})}function rp(o){function l(d){return d>=.04045?((d+.055)/(1+.055))**2.4:d/12.92}return{r:l(o.r),g:l(o.g),b:l(o.b),a:o.a}}function sp(o){let l=.4122214708*o.r+.5363325363*o.g+.0514459929*o.b,d=.2119034982*o.r+.6806995451*o.g+.1073969566*o.b,y=.0883024619*o.r+.2817188376*o.g+.6299787005*o.b,T=Math.cbrt(l),I=Math.cbrt(d),k=Math.cbrt(y);return{L:.2104542553*T+.793617785*I-.0040720468*k,a:1.9779984951*T-2.428592205*I+.4505937099*k,b:.0259040371*T+.7827717662*I-.808675766*k,alpha:o.a}}function _M(o){let l=o.L+.3963377774*o.a+.2158037573*o.b,d=o.L-.1055613458*o.a-.0638541728*o.b,y=o.L-.0894841775*o.a-1.291485548*o.b,T=l*l*l,I=d*d*d,k=y*y*y;return{r:4.0767416621*T-3.3077115913*I+.2309699292*k,g:-1.2684380046*T+2.6097574011*I-.3413193965*k,b:-.0041960863*T-.7034186147*I+1.707614701*k,a:o.alpha}}var Ui=Symbol("TheatrePropType_Basic");function op(o){return typeof o=="object"&&!!o&&o[Ui]==="TheatrePropType"}function vM(o){if(typeof o=="number")return ap(o);if(typeof o=="boolean")return cp(o);if(typeof o=="string")return lp(o);if(typeof o=="object"&&o){if(op(o))return o;if(Nv(o))return iu(o);throw new wo("This value is not a valid prop type: ".concat(ip(o)))}else throw new wo("This value is not a valid prop type: ".concat(ip(o)))}function yM(o){const l={};for(const d of Object.keys(o)){const y=o[d];op(y)?l[d]=y:l[d]=vM(y)}return l}var iu=(o,l={})=>{const d=yM(o),y=new WeakMap;return{type:"compound",props:d,valueType:null,[Ui]:"TheatrePropType",label:l.label,default:aS(d,I=>I.default),deserializeAndSanitize:I=>{if(typeof I!="object"||!I)return;if(y.has(I))return y.get(I);const k={};let Y=!1;for(const[$,oe]of Object.entries(d))if(Object.prototype.hasOwnProperty.call(I,$)){const ge=oe.deserializeAndSanitize(I[$]);ge!=null&&(Y=!0,k[$]=ge)}if(y.set(I,k),Y)return k}}},xM=(o,l={})=>{const d=(y,T,I)=>{var k;return{type:"file",id:((k=l.interpolate)!=null?k:Po)(y.id,T.id,I)}};return{type:"file",default:{type:"file",id:o},valueType:null,[Ui]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:bM}},bM=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="file"&&(l=!1),!!l)return o},SM=(o,l={})=>{const d=(y,T,I)=>{var k;return{type:"image",id:((k=l.interpolate)!=null?k:Po)(y.id,T.id,I)}};return{type:"image",default:{type:"image",id:o},valueType:null,[Ui]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:MM}},MM=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="image"&&(l=!1),!!l)return o},ap=(o,l={})=>{var d;return x(g({type:"number",valueType:0,default:o,[Ui]:"TheatrePropType"},l||{}),{label:l.label,nudgeFn:(d=l.nudgeFn)!=null?d:DM,nudgeMultiplier:typeof l.nudgeMultiplier=="number"?l.nudgeMultiplier:void 0,interpolate:AM,deserializeAndSanitize:TM(l.range)})},TM=o=>o?l=>{if(typeof l=="number"&&isFinite(l))return nf(l,o[0],o[1])}:EM,EM=o=>typeof o=="number"&&isFinite(o)?o:void 0,AM=(o,l,d)=>o+d*(l-o),wM=(o={r:0,g:0,b:0,a:1},l={})=>{const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return{type:"rgba",valueType:null,default:nu(d),[Ui]:"TheatrePropType",label:l.label,interpolate:RM,deserializeAndSanitize:PM}},PM=o=>{if(!o)return;let l=!0;for(const y of["r","g","b","a"])(!Object.prototype.hasOwnProperty.call(o,y)||typeof o[y]!="number")&&(l=!1);if(!l)return;const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return nu(d)},RM=(o,l,d)=>{const y=sp(rp(o)),T=sp(rp(l)),I={L:(1-d)*y.L+d*T.L,a:(1-d)*y.a+d*T.a,b:(1-d)*y.b+d*T.b,alpha:(1-d)*y.alpha+d*T.alpha},k=gM(_M(I));return nu(k)},cp=(o,l={})=>{var d;return{type:"boolean",default:o,valueType:null,[Ui]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:CM}},CM=o=>typeof o=="boolean"?o:void 0;function Po(o){return o}var lp=(o,l={})=>{var d;return{type:"string",default:o,valueType:null,[Ui]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:IM}};function IM(o){return typeof o=="string"?o:void 0}function LM(o,l,d={}){var y,T;return{type:"stringLiteral",default:o,valuesAndLabels:g({},l),[Ui]:"TheatrePropType",valueType:null,as:(y=d.as)!=null?y:"menu",label:d.label,interpolate:(T=d.interpolate)!=null?T:Po,deserializeAndSanitize(I){if(typeof I=="string"&&Object.prototype.hasOwnProperty.call(l,I))return I}}}var DM=({config:o,deltaX:l,deltaFraction:d,magnitude:y})=>{var T;const{range:I}=o;return!o.nudgeMultiplier&&I&&!I.includes(1/0)&&!I.includes(-1/0)?d*(I[1]-I[0])*y:l*y*((T=o.nudgeMultiplier)!=null?T:1)},NM=o=>o.replace(/^[\s\/]*/,"").replace(/[\s\/]*$/,"").replace(/\s*\/\s*/g," / ");function Ba(o,l){return NM(o)}A(H());var OM=class{get type(){return"Theatre_Sheet_PublicAPI"}constructor(o){de(this,o)}object(o,l,d){const y=J(this),T=Ba(o),I=y.getObject(T),k=null,Y=d==null?void 0:d.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;if(I)return Y&&I.template._temp_setActions(Y),I.publicApi;{const $=iu(l);return y.createObject(T,k,$,Y).publicApi}}__experimental_getExistingObject(o){const l=J(this),d=Ba(o),y=l.getObject(d);return y==null?void 0:y.publicApi}get sequence(){return J(this).getSequence().publicApi}get project(){return J(this).project.publicApi}get address(){return g({},J(this).address)}detachObject(o){const l=J(this),d=Ba(o);if(!l.getObject(d)){Ss.warning(`Couldn't delete object "`.concat(d,'"'),'There is no object with key "'.concat(d,`".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(d,'")` with the correct key.')),console.warn('Object key "'.concat(d,'" does not exist.'));return}l.deleteObject(d)}},Ro=fn(),UM=class{constructor(o,l){this.template=o,this.instanceId=l,b(this,"_objects",new Ro.Atom({})),b(this,"_sequence"),b(this,"address"),b(this,"publicApi"),b(this,"project"),b(this,"objectsP",this._objects.pointer),b(this,"type","Theatre_Sheet"),b(this,"_logger"),this._logger=o.project._logger.named("Sheet",l),this._logger._trace("creating sheet"),this.project=o.project,this.address=x(g({},o.address),{sheetInstanceId:this.instanceId}),this.publicApi=new OM(this)}createObject(o,l,d,y={}){const I=this.template.getObjectTemplate(o,l,d,y).createInstance(this,l,d);return this._objects.setByPointer(k=>k[o],I),I}getObject(o){return this._objects.get()[o]}deleteObject(o){this._objects.reduce(l=>{const d=g({},l);return delete d[o],d})}getSequence(){if(!this._sequence){const o=(0,Ro.prism)(()=>{const d=(0,Ro.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length);return FM(d)}),l=(0,Ro.prism)(()=>{const d=(0,Ro.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit);return BM(d)});this._sequence=new hM(this.template.project,this,o,l)}return this._sequence}},FM=o=>typeof o=="number"&&isFinite(o)&&o>0?o:10,BM=o=>typeof o=="number"&&sS(o)&&o>=1&&o<=1e3?o:30,kM=class{constructor(o,l){this.project=o,b(this,"type","Theatre_SheetTemplate"),b(this,"address"),b(this,"_instances",new Zf.Atom({})),b(this,"instancesP",this._instances.pointer),b(this,"_objectTemplates",new Zf.Atom({})),b(this,"objectTemplatesP",this._objectTemplates.pointer),this.address=x(g({},o.address),{sheetId:l})}getInstance(o){let l=this._instances.get()[o];return l||(l=new UM(this,o),this._instances.setByPointer(d=>d[o],l)),l}getObjectTemplate(o,l,d,y){let T=this._objectTemplates.get()[o];return T||(T=new jS(this,o,l,d,y),this._objectTemplates.setByPointer(I=>I[o],T)),T}},ru=fn(),up=fn(),zM=o=>new Promise(l=>setTimeout(l,o)),HM=zM;function oi(o){for(var l=arguments.length,d=Array(l>1?l-1:0),y=1;y<l;y++)d[y-1]=arguments[y];throw Error("[Immer] minified error nr: "+o+(d.length?" "+d.map(function(T){return"'"+T+"'"}).join(","):"")+". Find the full error at: https://bit.ly/3cXEKWf")}function Br(o){return!!o&&!!o[Gn]}function kr(o){return!!o&&((function(l){if(!l||typeof l!="object")return!1;var d=Object.getPrototypeOf(l);if(d===null)return!0;var y=Object.hasOwnProperty.call(d,"constructor")&&d.constructor;return y===Object||typeof y=="function"&&Function.toString.call(y)===$M})(o)||Array.isArray(o)||!!o[xp]||!!o.constructor[xp]||ou(o)||au(o))}function VM(o){return Br(o)||oi(23,o),o[Gn].t}function Co(o,l,d){d===void 0&&(d=!1),Ts(o)===0?(d?Object.keys:yu)(o).forEach(function(y){d&&typeof y=="symbol"||l(y,o[y],o)}):o.forEach(function(y,T){return l(T,y,o)})}function Ts(o){var l=o[Gn];return l?l.i>3?l.i-4:l.i:Array.isArray(o)?1:ou(o)?2:au(o)?3:0}function su(o,l){return Ts(o)===2?o.has(l):Object.prototype.hasOwnProperty.call(o,l)}function GM(o,l){return Ts(o)===2?o.get(l):o[l]}function hp(o,l,d){var y=Ts(o);y===2?o.set(l,d):y===3?(o.delete(l),o.add(d)):o[l]=d}function WM(o,l){return o===l?o!==0||1/o==1/l:o!=o&&l!=l}function ou(o){return YM&&o instanceof Map}function au(o){return KM&&o instanceof Set}function zr(o){return o.o||o.t}function cu(o){if(Array.isArray(o))return Array.prototype.slice.call(o);var l=ZM(o);delete l[Gn];for(var d=yu(l),y=0;y<d.length;y++){var T=d[y],I=l[T];I.writable===!1&&(I.writable=!0,I.configurable=!0),(I.get||I.set)&&(l[T]={configurable:!0,writable:!0,enumerable:I.enumerable,value:o[T]})}return Object.create(Object.getPrototypeOf(o),l)}function lu(o,l){return l===void 0&&(l=!1),uu(o)||Br(o)||!kr(o)||(Ts(o)>1&&(o.set=o.add=o.clear=o.delete=jM),Object.freeze(o),l&&Co(o,function(d,y){return lu(y,!0)},!0)),o}function jM(){oi(2)}function uu(o){return o==null||typeof o!="object"||Object.isFrozen(o)}function Fi(o){var l=JM[o];return l||oi(18,o),l}function dp(){return Io}function hu(o,l){l&&(Fi("Patches"),o.u=[],o.s=[],o.v=l)}function ka(o){du(o),o.p.forEach(XM),o.p=null}function du(o){o===Io&&(Io=o.l)}function fp(o){return Io={p:[],l:Io,h:o,m:!0,_:0}}function XM(o){var l=o[Gn];l.i===0||l.i===1?l.j():l.O=!0}function fu(o,l){l._=l.p.length;var d=l.p[0],y=o!==void 0&&o!==d;return l.h.g||Fi("ES5").S(l,o,y),y?(d[Gn].P&&(ka(l),oi(4)),kr(o)&&(o=za(l,o),l.l||Ha(l,o)),l.u&&Fi("Patches").M(d[Gn],o,l.u,l.s)):o=za(l,d,[]),ka(l),l.u&&l.v(l.u,l.s),o!==yp?o:void 0}function za(o,l,d){if(uu(l))return l;var y=l[Gn];if(!y)return Co(l,function(I,k){return pp(o,y,l,I,k,d)},!0),l;if(y.A!==o)return l;if(!y.P)return Ha(o,y.t,!0),y.t;if(!y.I){y.I=!0,y.A._--;var T=y.i===4||y.i===5?y.o=cu(y.k):y.o;Co(y.i===3?new Set(T):T,function(I,k){return pp(o,y,T,I,k,d)}),Ha(o,T,!1),d&&o.u&&Fi("Patches").R(y,d,o.u,o.s)}return y.o}function pp(o,l,d,y,T,I){if(Br(T)){var k=za(o,T,I&&l&&l.i!==3&&!su(l.D,y)?I.concat(y):void 0);if(hp(d,y,k),!Br(k))return;o.m=!1}if(kr(T)&&!uu(T)){if(!o.h.F&&o._<1)return;za(o,T),l&&l.A.l||Ha(o,T)}}function Ha(o,l,d){d===void 0&&(d=!1),o.h.F&&o.m&&lu(l,d)}function pu(o,l){var d=o[Gn];return(d?zr(d):o)[l]}function mp(o,l){if(l in o)for(var d=Object.getPrototypeOf(o);d;){var y=Object.getOwnPropertyDescriptor(d,l);if(y)return y;d=Object.getPrototypeOf(d)}}function mu(o){o.P||(o.P=!0,o.l&&mu(o.l))}function gu(o){o.o||(o.o=cu(o.t))}function _u(o,l,d){var y=ou(l)?Fi("MapSet").N(l,d):au(l)?Fi("MapSet").T(l,d):o.g?(function(T,I){var k=Array.isArray(T),Y={i:k?1:0,A:I?I.A:dp(),P:!1,I:!1,D:{},l:I,t:T,k:null,o:null,j:null,C:!1},$=Y,oe=Va;k&&($=[Y],oe=Ga);var ge=Proxy.revocable($,oe),ve=ge.revoke,Pe=ge.proxy;return Y.k=Pe,Y.j=ve,Pe})(l,d):Fi("ES5").J(l,d);return(d?d.A:dp()).p.push(y),y}function qM(o){return Br(o)||oi(22,o),(function l(d){if(!kr(d))return d;var y,T=d[Gn],I=Ts(d);if(T){if(!T.P&&(T.i<4||!Fi("ES5").K(T)))return T.t;T.I=!0,y=gp(d,I),T.I=!1}else y=gp(d,I);return Co(y,function(k,Y){T&&GM(T.t,k)===Y||hp(y,k,l(Y))}),I===3?new Set(y):y})(o)}function gp(o,l){switch(l){case 2:return new Map(o);case 3:return Array.from(o)}return cu(o)}var _p,Io,vu=typeof Symbol<"u"&&typeof Symbol("x")=="symbol",YM=typeof Map<"u",KM=typeof Set<"u",vp=typeof Proxy<"u"&&Proxy.revocable!==void 0&&typeof Reflect<"u",yp=vu?Symbol.for("immer-nothing"):((_p={})["immer-nothing"]=!0,_p),xp=vu?Symbol.for("immer-draftable"):"__$immer_draftable",Gn=vu?Symbol.for("immer-state"):"__$immer_state",$M=""+Object.prototype.constructor,yu=typeof Reflect<"u"&&Reflect.ownKeys?Reflect.ownKeys:Object.getOwnPropertySymbols!==void 0?function(o){return Object.getOwnPropertyNames(o).concat(Object.getOwnPropertySymbols(o))}:Object.getOwnPropertyNames,ZM=Object.getOwnPropertyDescriptors||function(o){var l={};return yu(o).forEach(function(d){l[d]=Object.getOwnPropertyDescriptor(o,d)}),l},JM={},Va={get:function(o,l){if(l===Gn)return o;var d=zr(o);if(!su(d,l))return(function(T,I,k){var Y,$=mp(I,k);return $?"value"in $?$.value:(Y=$.get)===null||Y===void 0?void 0:Y.call(T.k):void 0})(o,d,l);var y=d[l];return o.I||!kr(y)?y:y===pu(o.t,l)?(gu(o),o.o[l]=_u(o.A.h,y,o)):y},has:function(o,l){return l in zr(o)},ownKeys:function(o){return Reflect.ownKeys(zr(o))},set:function(o,l,d){var y=mp(zr(o),l);if(y!=null&&y.set)return y.set.call(o.k,d),!0;if(!o.P){var T=pu(zr(o),l),I=T==null?void 0:T[Gn];if(I&&I.t===d)return o.o[l]=d,o.D[l]=!1,!0;if(WM(d,T)&&(d!==void 0||su(o.t,l)))return!0;gu(o),mu(o)}return o.o[l]===d&&typeof d!="number"&&(d!==void 0||l in o.o)||(o.o[l]=d,o.D[l]=!0,!0)},deleteProperty:function(o,l){return pu(o.t,l)!==void 0||l in o.t?(o.D[l]=!1,gu(o),mu(o)):delete o.D[l],o.o&&delete o.o[l],!0},getOwnPropertyDescriptor:function(o,l){var d=zr(o),y=Reflect.getOwnPropertyDescriptor(d,l);return y&&{writable:!0,configurable:o.i!==1||l!=="length",enumerable:y.enumerable,value:d[l]}},defineProperty:function(){oi(11)},getPrototypeOf:function(o){return Object.getPrototypeOf(o.t)},setPrototypeOf:function(){oi(12)}},Ga={};Co(Va,function(o,l){Ga[o]=function(){return arguments[0]=arguments[0][0],l.apply(this,arguments)}}),Ga.deleteProperty=function(o,l){return Va.deleteProperty.call(this,o[0],l)},Ga.set=function(o,l,d){return Va.set.call(this,o[0],l,d,o[0])};var QM=(function(){function o(d){var y=this;this.g=vp,this.F=!0,this.produce=function(T,I,k){if(typeof T=="function"&&typeof I!="function"){var Y=I;I=T;var $=y;return function(Ye){var ze=this;Ye===void 0&&(Ye=Y);for(var ft=arguments.length,xt=Array(ft>1?ft-1:0),dt=1;dt<ft;dt++)xt[dt-1]=arguments[dt];return $.produce(Ye,function(Lt){var Rn;return(Rn=I).call.apply(Rn,[ze,Lt].concat(xt))})}}var oe;if(typeof I!="function"&&oi(6),k!==void 0&&typeof k!="function"&&oi(7),kr(T)){var ge=fp(y),ve=_u(y,T,void 0),Pe=!0;try{oe=I(ve),Pe=!1}finally{Pe?ka(ge):du(ge)}return typeof Promise<"u"&&oe instanceof Promise?oe.then(function(Ye){return hu(ge,k),fu(Ye,ge)},function(Ye){throw ka(ge),Ye}):(hu(ge,k),fu(oe,ge))}if(!T||typeof T!="object")return(oe=I(T))===yp?void 0:(oe===void 0&&(oe=T),y.F&&lu(oe,!0),oe);oi(21,T)},this.produceWithPatches=function(T,I){return typeof T=="function"?function($){for(var oe=arguments.length,ge=Array(oe>1?oe-1:0),ve=1;ve<oe;ve++)ge[ve-1]=arguments[ve];return y.produceWithPatches($,function(Pe){return T.apply(void 0,[Pe].concat(ge))})}:[y.produce(T,I,function($,oe){k=$,Y=oe}),k,Y];var k,Y},typeof(d==null?void 0:d.useProxies)=="boolean"&&this.setUseProxies(d.useProxies),typeof(d==null?void 0:d.autoFreeze)=="boolean"&&this.setAutoFreeze(d.autoFreeze)}var l=o.prototype;return l.createDraft=function(d){kr(d)||oi(8),Br(d)&&(d=qM(d));var y=fp(this),T=_u(this,d,void 0);return T[Gn].C=!0,du(y),T},l.finishDraft=function(d,y){var T=d&&d[Gn],I=T.A;return hu(I,y),fu(void 0,I)},l.setAutoFreeze=function(d){this.F=d},l.setUseProxies=function(d){d&&!vp&&oi(20),this.g=d},l.applyPatches=function(d,y){var T;for(T=y.length-1;T>=0;T--){var I=y[T];if(I.path.length===0&&I.op==="replace"){d=I.value;break}}var k=Fi("Patches").$;return Br(d)?k(d,y):this.produce(d,function(Y){return k(Y,y.slice(T+1))})},o})(),Jn=new QM;Jn.produce,Jn.produceWithPatches.bind(Jn),Jn.setAutoFreeze.bind(Jn),Jn.setUseProxies.bind(Jn),Jn.applyPatches.bind(Jn),Jn.createDraft.bind(Jn),Jn.finishDraft.bind(Jn);var eT={currentProjectStateDefinitionVersion:"0.4.0"},xu=eT;async function tT(o,l,d){await HM(0),o.transaction(({drafts:y})=>{var T;const I=l.address.projectId;y.ephemeral.coreByProject[I]={lastExportedObject:null,loadingState:{type:"loading"}},y.ahistoric.coreByProject[I]={ahistoricStuff:""};function k(){y.ephemeral.coreByProject[I].loadingState={type:"loaded"},y.historic.coreByProject[I]={sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]}}function Y(ve){y.ephemeral.coreByProject[I].loadingState={type:"loaded"},y.historic.coreByProject[I]=ve}function $(){y.ephemeral.coreByProject[I].loadingState={type:"loaded"}}function oe(ve){y.ephemeral.coreByProject[I].loadingState={type:"browserStateIsNotBasedOnDiskState",onDiskState:ve}}const ge=(T=VM(y.historic))==null?void 0:T.coreByProject[l.address.projectId];ge?d&&ge.revisionHistory.indexOf(d.revisionHistory[0])==-1?oe(d):$():d?Y(d):k()})}function bp(){}function Sp(o){var l,d;const y=(l=o==null?void 0:o.logging)!=null&&l.internal?(d=o.logging.min)!=null?d:256:1/0,T=y<=128,I=y<=512,k=Wf(void 0,{_debug:T?console.debug.bind(console,"_coreLogger(TheatreInternalLogger) debug"):bp,_error:I?console.error.bind(console,"_coreLogger(TheatreInternalLogger) error"):bp});if(o){const{logger:Y,logging:$}=o;Y&&k.configureLogger(Y),$?k.configureLogging($):k.configureLogging({dev:!1})}return k.getLogger().named("Theatre")}var nT=class{constructor(o,l={},d){this.config=l,this.publicApi=d,b(this,"pointers"),b(this,"_pointerProxies"),b(this,"address"),b(this,"_studioReadyDeferred"),b(this,"_assetStorageReadyDeferred"),b(this,"_readyPromise"),b(this,"_sheetTemplates",new up.Atom({})),b(this,"sheetTemplatesP",this._sheetTemplates.pointer),b(this,"_studio"),b(this,"assetStorage"),b(this,"type","Theatre_Project"),b(this,"_logger");var y;this._logger=Sp({logging:{dev:!0}}).named("Project",o),this._logger.traceDev("creating project"),this.address={projectId:o};const T=new up.Atom({ahistoric:{ahistoricStuff:""},historic:(y=l.state)!=null?y:{sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]},ephemeral:{loadingState:{type:"loaded"},lastExportedObject:null}});this._assetStorageReadyDeferred=ar(),this.assetStorage={getAssetUrl:I=>{var k;return"".concat((k=l.assets)==null?void 0:k.baseUrl,"/").concat(I)},createAsset:()=>{throw new Error("Please wait for Project.ready to use assets.")}},this._pointerProxies={historic:new ru.PointerProxy(T.pointer.historic),ahistoric:new ru.PointerProxy(T.pointer.ahistoric),ephemeral:new ru.PointerProxy(T.pointer.ephemeral)},this.pointers={historic:this._pointerProxies.historic.pointer,ahistoric:this._pointerProxies.ahistoric.pointer,ephemeral:this._pointerProxies.ephemeral.pointer},ae.add(o,this),this._studioReadyDeferred=ar(),this._readyPromise=Promise.all([this._studioReadyDeferred.promise,this._assetStorageReadyDeferred.promise]).then(()=>{}),l.state?setTimeout(()=>{this._studio||(this._studioReadyDeferred.resolve(void 0),this._assetStorageReadyDeferred.resolve(void 0),this._logger._trace("ready deferred resolved with no state"))},0):typeof window>"u"?console.error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. ')+"You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"):setTimeout(()=>{if(!this._studio)throw new Error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. This is fine ')+"while you are using @theatre/core along with @theatre/studio. But since @theatre/studio "+'is not loaded, the state of project "'.concat(o,`" will be empty.

`)+`To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`)},1e3)}attachToStudio(o){if(this._studio){if(this._studio!==o)throw new Error("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));console.warn("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));return}this._studio=o,o.initialized.then(async()=>{var l;await tT(o,this,this.config.state),this._pointerProxies.historic.setPointer(o.atomP.historic.coreByProject[this.address.projectId]),this._pointerProxies.ahistoric.setPointer(o.atomP.ahistoric.coreByProject[this.address.projectId]),this._pointerProxies.ephemeral.setPointer(o.atomP.ephemeral.coreByProject[this.address.projectId]),await o.createAssetStorage(this,(l=this.config.assets)==null?void 0:l.baseUrl).then(d=>{this.assetStorage=d,this._assetStorageReadyDeferred.resolve(void 0)}),this._studioReadyDeferred.resolve(void 0)}).catch(l=>{throw console.error(l),l})}get isAttachedToStudio(){return!!this._studio}get ready(){return this._readyPromise}isReady(){return this._studioReadyDeferred.status==="resolved"&&this._assetStorageReadyDeferred.status==="resolved"}getOrCreateSheet(o,l="default"){let d=this._sheetTemplates.get()[o];return d||(d=new kM(this,o),this._sheetTemplates.reduce(y=>x(g({},y),{[o]:d}))),d.getInstance(l)}},iT=class{get type(){return"Theatre_Project_PublicAPI"}constructor(o,l={}){de(this,new nT(o,l,this))}get ready(){return J(this).ready}get isReady(){return J(this).isReady()}get address(){return g({},J(this).address)}getAssetUrl(o){if(!this.isReady){console.error("Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`.");return}return o.id?J(this).assetStorage.getAssetUrl(o.id):void 0}sheet(o,l="default"){const d=Ba(o);return J(this).getOrCreateSheet(d,l).publicApi}};A(H());var Mp=fn(),bu=fn();function Tp(o,l={}){const d=ae.get(o);if(d)return d.publicApi;const T=Sp().named("Project",o);return l.state?(sT(o,l.state),T._debug("deep validated config.state on disk")):T._debug("no config.state"),new iT(o,l)}var rT=(o,l)=>{if(Array.isArray(l)||l==null||l.definitionVersion!==xu.currentProjectStateDefinitionVersion)throw new wo("Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(o),", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state"))},sT=(o,l)=>{rT(o,l)};function Su(o,l,d){const y=d?J(d).ticker:tp();if((0,Mp.isPointer)(o))return(0,bu.pointerToPrism)(o).onChange(y,l,!0);if((0,bu.isPrism)(o))return o.onChange(y,l,!0);throw new Error("Called onChange(p) where p is neither a pointer nor a prism.")}function Ep(o){if((0,Mp.isPointer)(o))return(0,bu.pointerToPrism)(o).getValue();throw new Error("Called val(p) where p is not a pointer.")}var oT=class{constructor(){b(this,"_studio")}get type(){return"Theatre_CoreBundle"}get version(){return"0.7.2"}getBitsForStudio(o,l){if(this._studio)throw new Error("@theatre/core is already attached to @theatre/studio");this._studio=o;const d={projectsP:ae.atom.pointer.projects,privateAPI:J,coreExports:P,getCoreRafDriver:ep};l(d)}};aT();function aT(){if(typeof window>"u")return;const o=window[Ql];if(typeof o<"u")throw typeof o=="object"&&o&&typeof o.version=="string"?new Error(`It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
1. You might have two separate versions of Theatre.js in node_modules.
2. Or this might be a bundling misconfiguration, in case you're using a bundler like Webpack/ESBuild/Rollup.

Note that it **is okay** to import '@theatre/core' multiple times. But those imports should point to the same module.`):new Error("The variable window.".concat(Ql," seems to be already set by a module other than @theatre/core."));const l=new oT;window[Ql]=l;const d=window[tM];d&&d!==null&&d.type==="Theatre_StudioBundle"&&d.registerCoreBundle(l)}/*! Bundled license information:

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
		*/})(Yo,Yo.exports)),Yo.exports}var on=FC();let ch=null,sd=null;const i_=new Map;function BC(){return ch=on.getProject("HumanBody Theatre"),sd=ch.sheet("Main"),{project:ch,sheet:sd}}function Ld(){return sd}function kC(r,e){const t=r.object("Camera",{position:on.types.compound({x:on.types.number(e.position.x,{range:[-50,50]}),y:on.types.number(e.position.y,{range:[-10,20]}),z:on.types.number(e.position.z,{range:[-50,50]})}),fov:on.types.number(e.fov,{range:[10,120]})});return t.onValuesChange(n=>{e.position.set(n.position.x,n.position.y,n.position.z),e.fov=n.fov,e.updateProjectionMatrix()}),i_.set("Camera",t),t}function Sc(r,e,t){const n={position:on.types.compound({x:on.types.number(t.position.x,{range:[-20,20]}),y:on.types.number(t.position.y,{range:[0,20]}),z:on.types.number(t.position.z,{range:[-20,20]})}),intensity:on.types.number(t.intensity,{range:[0,100]}),color:on.types.rgba({r:t.color.r,g:t.color.g,b:t.color.b,a:1})},i=r.object(e,n);return i.onValuesChange(s=>{t.position.set(s.position.x,s.position.y,s.position.z),t.intensity=s.intensity,t.color.setRGB(s.color.r,s.color.g,s.color.b)}),i_.set(e,i),i}function Dd(r,e,t){const n=r.object(e,{position:on.types.compound({x:on.types.number(t.position.x,{range:[-20,20]}),y:on.types.number(t.position.y,{range:[-5,10]}),z:on.types.number(t.position.z,{range:[-20,20]})}),rotation:on.types.compound({x:on.types.number(0,{range:[-180,180]}),y:on.types.number(0,{range:[-180,180]}),z:on.types.number(0,{range:[-180,180]})}),scale:on.types.number(1,{range:[.01,10]})});return n.onValuesChange(i=>{t.position.set(i.position.x,i.position.y,i.position.z),t.rotation.set(i.rotation.x*Math.PI/180,i.rotation.y*Math.PI/180,i.rotation.z*Math.PI/180),t.scale.setScalar(i.scale)}),n}function rg(r,e){if(e===HT)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),r;if(e===Qh||e===Tg){let t=r.getIndex();if(t===null){const a=[],c=r.getAttribute("position");if(c!==void 0){for(let u=0;u<c.count;u++)a.push(u);r.setIndex(a),t=r.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),r}const n=t.count-2,i=[];if(e===Qh)for(let a=1;a<=n;a++)i.push(t.getX(0)),i.push(t.getX(a)),i.push(t.getX(a+1));else for(let a=0;a<n;a++)a%2===0?(i.push(t.getX(a)),i.push(t.getX(a+1)),i.push(t.getX(a+2))):(i.push(t.getX(a+2)),i.push(t.getX(a+1)),i.push(t.getX(a)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const s=r.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),r}class zC extends us{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new jC(t)}),this.register(function(t){return new XC(t)}),this.register(function(t){return new tI(t)}),this.register(function(t){return new nI(t)}),this.register(function(t){return new iI(t)}),this.register(function(t){return new YC(t)}),this.register(function(t){return new KC(t)}),this.register(function(t){return new $C(t)}),this.register(function(t){return new ZC(t)}),this.register(function(t){return new WC(t)}),this.register(function(t){return new JC(t)}),this.register(function(t){return new qC(t)}),this.register(function(t){return new eI(t)}),this.register(function(t){return new QC(t)}),this.register(function(t){return new VC(t)}),this.register(function(t){return new rI(t)}),this.register(function(t){return new sI(t)})}load(e,t,n,i){const s=this;let a;if(this.resourcePath!=="")a=this.resourcePath;else if(this.path!==""){const h=Zo.extractUrlBase(e);a=Zo.resolveURL(h,this.path)}else a=Zo.extractUrlBase(e);this.manager.itemStart(e);const c=function(h){i?i(h):console.error(h),s.manager.itemError(e),s.manager.itemEnd(e)},u=new wd(this.manager);u.setPath(this.path),u.setResponseType("arraybuffer"),u.setRequestHeader(this.requestHeader),u.setWithCredentials(this.withCredentials),u.load(e,function(h){try{s.parse(h,a,function(f){t(f),s.manager.itemEnd(e)},c)}catch(f){c(f)}},n,c)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s;const a={},c={},u=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(u.decode(new Uint8Array(e,0,4))===r_){try{a[St.KHR_BINARY_GLTF]=new oI(e)}catch(p){i&&i(p);return}s=JSON.parse(a[St.KHR_BINARY_GLTF].content)}else s=JSON.parse(u.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const h=new yI(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});h.fileLoader.setRequestHeader(this.requestHeader);for(let f=0;f<this.pluginCallbacks.length;f++){const p=this.pluginCallbacks[f](h);p.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),c[p.name]=p,a[p.name]=!0}if(s.extensionsUsed)for(let f=0;f<s.extensionsUsed.length;++f){const p=s.extensionsUsed[f],m=s.extensionsRequired||[];switch(p){case St.KHR_MATERIALS_UNLIT:a[p]=new GC;break;case St.KHR_DRACO_MESH_COMPRESSION:a[p]=new aI(s,this.dracoLoader);break;case St.KHR_TEXTURE_TRANSFORM:a[p]=new cI;break;case St.KHR_MESH_QUANTIZATION:a[p]=new lI;break;default:m.indexOf(p)>=0&&c[p]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+p+'".')}}h.setExtensions(a),h.setPlugins(c),h.parse(n,i)}parseAsync(e,t){const n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}}function HC(){let r={};return{get:function(e){return r[e]},add:function(e,t){r[e]=t},remove:function(e){delete r[e]},removeAll:function(){r={}}}}const St={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class VC{constructor(e){this.parser=e,this.name=St.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){const s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let i=t.cache.get(n);if(i)return i;const s=t.json,u=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e];let h;const f=new $e(16777215);u.color!==void 0&&f.setRGB(u.color[0],u.color[1],u.color[2],Hn);const p=u.range!==void 0?u.range:0;switch(u.type){case"directional":h=new Cc(f),h.target.position.set(0,0,-1),h.add(h.target);break;case"point":h=new $g(f),h.distance=p;break;case"spot":h=new YR(f),h.distance=p,u.spot=u.spot||{},u.spot.innerConeAngle=u.spot.innerConeAngle!==void 0?u.spot.innerConeAngle:0,u.spot.outerConeAngle=u.spot.outerConeAngle!==void 0?u.spot.outerConeAngle:Math.PI/4,h.angle=u.spot.outerConeAngle,h.penumbra=1-u.spot.innerConeAngle/u.spot.outerConeAngle,h.target.position.set(0,0,-1),h.add(h.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+u.type)}return h.position.set(0,0,0),h.decay=2,qi(h,u),u.intensity!==void 0&&(h.intensity=u.intensity),h.name=t.createUniqueName(u.name||"light_"+e),i=Promise.resolve(h),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,s=n.json.nodes[e],c=(s.extensions&&s.extensions[this.name]||{}).light;return c===void 0?null:this._loadLight(c).then(function(u){return n._getNodeRef(t.cache,c,u)})}}class GC{constructor(){this.name=St.KHR_MATERIALS_UNLIT}getMaterialType(){return ui}extendParams(e,t,n){const i=[];e.color=new $e(1,1,1),e.opacity=1;const s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){const a=s.baseColorFactor;e.color.setRGB(a[0],a[1],a[2],Hn),e.opacity=a[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,bn))}return Promise.all(i)}}class WC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}}class jC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];if(a.clearcoatFactor!==void 0&&(t.clearcoat=a.clearcoatFactor),a.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",a.clearcoatTexture)),a.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=a.clearcoatRoughnessFactor),a.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",a.clearcoatRoughnessTexture)),a.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",a.clearcoatNormalTexture)),a.clearcoatNormalTexture.scale!==void 0)){const c=a.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new tt(c,c)}return Promise.all(s)}}class XC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.dispersion=s.dispersion!==void 0?s.dispersion:0,Promise.resolve()}}class qC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.iridescenceFactor!==void 0&&(t.iridescence=a.iridescenceFactor),a.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",a.iridescenceTexture)),a.iridescenceIor!==void 0&&(t.iridescenceIOR=a.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),a.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=a.iridescenceThicknessMinimum),a.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=a.iridescenceThicknessMaximum),a.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",a.iridescenceThicknessTexture)),Promise.all(s)}}class YC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[];t.sheenColor=new $e(0,0,0),t.sheenRoughness=0,t.sheen=1;const a=i.extensions[this.name];if(a.sheenColorFactor!==void 0){const c=a.sheenColorFactor;t.sheenColor.setRGB(c[0],c[1],c[2],Hn)}return a.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=a.sheenRoughnessFactor),a.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",a.sheenColorTexture,bn)),a.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",a.sheenRoughnessTexture)),Promise.all(s)}}class KC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.transmissionFactor!==void 0&&(t.transmission=a.transmissionFactor),a.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",a.transmissionTexture)),Promise.all(s)}}class $C{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.thickness=a.thicknessFactor!==void 0?a.thicknessFactor:0,a.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",a.thicknessTexture)),t.attenuationDistance=a.attenuationDistance||1/0;const c=a.attenuationColor||[1,1,1];return t.attenuationColor=new $e().setRGB(c[0],c[1],c[2],Hn),Promise.all(s)}}class ZC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}}class JC{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.specularIntensity=a.specularFactor!==void 0?a.specularFactor:1,a.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",a.specularTexture));const c=a.specularColorFactor||[1,1,1];return t.specularColor=new $e().setRGB(c[0],c[1],c[2],Hn),a.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",a.specularColorTexture,bn)),Promise.all(s)}}class QC{constructor(e){this.parser=e,this.name=St.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return t.bumpScale=a.bumpFactor!==void 0?a.bumpFactor:1,a.bumpTexture!==void 0&&s.push(n.assignTexture(t,"bumpMap",a.bumpTexture)),Promise.all(s)}}class eI{constructor(e){this.parser=e,this.name=St.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Pi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.anisotropyStrength!==void 0&&(t.anisotropy=a.anisotropyStrength),a.anisotropyRotation!==void 0&&(t.anisotropyRotation=a.anisotropyRotation),a.anisotropyTexture!==void 0&&s.push(n.assignTexture(t,"anisotropyMap",a.anisotropyTexture)),Promise.all(s)}}class tI{constructor(e){this.parser=e,this.name=St.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;const s=i.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,a)}}class nI{constructor(e){this.parser=e,this.name=St.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class iI{constructor(e){this.parser=e,this.name=St.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class rI{constructor(e){this.name=St.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),a=this.parser.options.meshoptDecoder;if(!a||!a.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(c){const u=i.byteOffset||0,h=i.byteLength||0,f=i.count,p=i.byteStride,m=new Uint8Array(c,u,h);return a.decodeGltfBufferAsync?a.decodeGltfBufferAsync(f,p,m,i.mode,i.filter).then(function(g){return g.buffer}):a.ready.then(function(){const g=new ArrayBuffer(f*p);return a.decodeGltfBuffer(new Uint8Array(g),f,p,m,i.mode,i.filter),g})})}else return null}}class sI{constructor(e){this.name=St.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const i=t.meshes[n.mesh];for(const h of i.primitives)if(h.mode!==ci.TRIANGLES&&h.mode!==ci.TRIANGLE_STRIP&&h.mode!==ci.TRIANGLE_FAN&&h.mode!==void 0)return null;const a=n.extensions[this.name].attributes,c=[],u={};for(const h in a)c.push(this.parser.getDependency("accessor",a[h]).then(f=>(u[h]=f,u[h])));return c.length<1?null:(c.push(this.parser.createNodeMesh(e)),Promise.all(c).then(h=>{const f=h.pop(),p=f.isGroup?f.children:[f],m=h[0].count,g=[];for(const x of p){const M=new ot,v=new F,_=new en,A=new F(1,1,1),w=new LR(x.geometry,x.material,m);for(let b=0;b<m;b++)u.TRANSLATION&&v.fromBufferAttribute(u.TRANSLATION,b),u.ROTATION&&_.fromBufferAttribute(u.ROTATION,b),u.SCALE&&A.fromBufferAttribute(u.SCALE,b),w.setMatrixAt(b,M.compose(v,_,A));for(const b in u)if(b==="_COLOR_0"){const B=u[b];w.instanceColor=new nd(B.array,B.itemSize,B.normalized)}else b!=="TRANSLATION"&&b!=="ROTATION"&&b!=="SCALE"&&x.geometry.setAttribute(b,u[b]);Jt.prototype.copy.call(w,x),this.parser.assignFinalMaterial(w),g.push(w)}return f.isGroup?(f.clear(),f.add(...g),f):g[0]}))}}const r_="glTF",Vo=12,sg={JSON:1313821514,BIN:5130562};class oI{constructor(e){this.name=St.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Vo),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==r_)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const i=this.header.length-Vo,s=new DataView(e,Vo);let a=0;for(;a<i;){const c=s.getUint32(a,!0);a+=4;const u=s.getUint32(a,!0);if(a+=4,u===sg.JSON){const h=new Uint8Array(e,Vo+a,c);this.content=n.decode(h)}else if(u===sg.BIN){const h=Vo+a;this.body=e.slice(h,h+c)}a+=c}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class aI{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=St.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,c={},u={},h={};for(const f in a){const p=od[f]||f.toLowerCase();c[p]=a[f]}for(const f in e.attributes){const p=od[f]||f.toLowerCase();if(a[f]!==void 0){const m=n.accessors[e.attributes[f]],g=Ks[m.componentType];h[p]=g.name,u[p]=m.normalized===!0}}return t.getDependency("bufferView",s).then(function(f){return new Promise(function(p,m){i.decodeDracoFile(f,function(g){for(const x in g.attributes){const M=g.attributes[x],v=u[x];v!==void 0&&(M.normalized=v)}p(g)},c,h,Hn,m)})})}}class cI{constructor(){this.name=St.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class lI{constructor(){this.name=St.KHR_MESH_QUANTIZATION}}class s_ extends sa{constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let a=0;a!==i;a++)t[a]=n[s+a];return t}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=c*2,h=c*3,f=i-t,p=(n-t)/f,m=p*p,g=m*p,x=e*h,M=x-h,v=-2*g+3*m,_=g-m,A=1-v,w=_-m+p;for(let b=0;b!==c;b++){const B=a[M+b+c],U=a[M+b+u]*f,O=a[x+b+c],H=a[x+b]*f;s[b]=A*B+w*U+v*O+_*H}return s}}const uI=new en;class hI extends s_{interpolate_(e,t,n,i){const s=super.interpolate_(e,t,n,i);return uI.fromArray(s).normalize().toArray(s),s}}const ci={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},Ks={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},og={9728:zn,9729:ii,9984:pg,9985:Mc,9986:Go,9987:Yi},ag={33071:yr,33648:Dc,10497:Qs},lh={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},od={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},gr={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},dI={CUBICSPLINE:void 0,LINEAR:ea,STEP:Qo},uh={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function fI(r){return r.DefaultMaterial===void 0&&(r.DefaultMaterial=new as({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:Ji})),r.DefaultMaterial}function Qr(r,e,t){for(const n in t.extensions)r[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function qi(r,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(r.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function pI(r,e,t){let n=!1,i=!1,s=!1;for(let h=0,f=e.length;h<f;h++){const p=e[h];if(p.POSITION!==void 0&&(n=!0),p.NORMAL!==void 0&&(i=!0),p.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(r);const a=[],c=[],u=[];for(let h=0,f=e.length;h<f;h++){const p=e[h];if(n){const m=p.POSITION!==void 0?t.getDependency("accessor",p.POSITION):r.attributes.position;a.push(m)}if(i){const m=p.NORMAL!==void 0?t.getDependency("accessor",p.NORMAL):r.attributes.normal;c.push(m)}if(s){const m=p.COLOR_0!==void 0?t.getDependency("accessor",p.COLOR_0):r.attributes.color;u.push(m)}}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u)]).then(function(h){const f=h[0],p=h[1],m=h[2];return n&&(r.morphAttributes.position=f),i&&(r.morphAttributes.normal=p),s&&(r.morphAttributes.color=m),r.morphTargetsRelative=!0,r})}function mI(r,e){if(r.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)r.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(r.morphTargetInfluences.length===t.length){r.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)r.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function gI(r){let e;const t=r.extensions&&r.extensions[St.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+hh(t.attributes):e=r.indices+":"+hh(r.attributes)+":"+r.mode,r.targets!==void 0)for(let n=0,i=r.targets.length;n<i;n++)e+=":"+hh(r.targets[n]);return e}function hh(r){let e="";const t=Object.keys(r).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+r[t[n]]+";";return e}function ad(r){switch(r){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function _I(r){return r.search(/\.jpe?g($|\?)/i)>0||r.search(/^data\:image\/jpeg/)===0?"image/jpeg":r.search(/\.webp($|\?)/i)>0||r.search(/^data\:image\/webp/)===0?"image/webp":r.search(/\.ktx2($|\?)/i)>0||r.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const vI=new ot;class yI{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new HC,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=-1,s=!1,a=-1;if(typeof navigator<"u"){const c=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(c)===!0;const u=c.match(/Version\/(\d+)/);i=n&&u?parseInt(u[1],10):-1,s=c.indexOf("Firefox")>-1,a=s?c.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&i<17||s&&a<98?this.textureLoader=new XR(this.options.manager):this.textureLoader=new JR(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new wd(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(a){return a._markDefs&&a._markDefs()}),Promise.all(this._invokeAll(function(a){return a.beforeRoot&&a.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(a){const c={scene:a[0][i.scene||0],scenes:a[0],animations:a[1],cameras:a[2],asset:i.asset,parser:n,userData:{}};return Qr(s,c,i),qi(c,i),Promise.all(n._invokeAll(function(u){return u.afterRoot&&u.afterRoot(c)})).then(function(){for(const u of c.scenes)u.updateMatrixWorld();e(c)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){const a=t[i].joints;for(let c=0,u=a.length;c<u;c++)e[a[c]].isBone=!0}for(let i=0,s=e.length;i<s;i++){const a=e[i];a.mesh!==void 0&&(this._addNodeRef(this.meshCache,a.mesh),a.skin!==void 0&&(n[a.mesh].isSkinnedMesh=!0)),a.camera!==void 0&&this._addNodeRef(this.cameraCache,a.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const i=n.clone(),s=(a,c)=>{const u=this.associations.get(a);u!=null&&this.associations.set(c,u);for(const[h,f]of a.children.entries())s(f,c.children[h])};return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const i=e(t[n]);if(i)return i}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let i=0;i<t.length;i++){const s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){const n=e+":"+t;let i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,a){return n.getDependency(e,a)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[St.KHR_BINARY_GLTF].body);const i=this.options;return new Promise(function(s,a){n.load(Zo.resolveURL(t.uri,i.path),s,void 0,function(){a(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){const t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){const a=lh[i.type],c=Ks[i.componentType],u=i.normalized===!0,h=new c(i.count*a);return Promise.resolve(new an(h,a,u))}const s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(a){const c=a[0],u=lh[i.type],h=Ks[i.componentType],f=h.BYTES_PER_ELEMENT,p=f*u,m=i.byteOffset||0,g=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,x=i.normalized===!0;let M,v;if(g&&g!==p){const _=Math.floor(m/g),A="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count;let w=t.cache.get(A);w||(M=new h(c,_*g,i.count*g/f),w=new PR(M,g/f),t.cache.add(A,w)),v=new Td(w,u,m%g/f,x)}else c===null?M=new h(i.count*u):M=new h(c,m,i.count*u),v=new an(M,u,x);if(i.sparse!==void 0){const _=lh.SCALAR,A=Ks[i.sparse.indices.componentType],w=i.sparse.indices.byteOffset||0,b=i.sparse.values.byteOffset||0,B=new A(a[1],w,i.sparse.count*_),U=new h(a[2],b,i.sparse.count*u);c!==null&&(v=new an(v.array.slice(),v.itemSize,v.normalized)),v.normalized=!1;for(let O=0,H=B.length;O<H;O++){const L=B[O];if(v.setX(L,U[O*u]),u>=2&&v.setY(L,U[O*u+1]),u>=3&&v.setZ(L,U[O*u+2]),u>=4&&v.setW(L,U[O*u+3]),u>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}v.normalized=x}return v})}loadTexture(e){const t=this.json,n=this.options,s=t.textures[e].source,a=t.images[s];let c=this.textureLoader;if(a.uri){const u=n.manager.getHandler(a.uri);u!==null&&(c=u)}return this.loadTextureImage(e,s,c)}loadTextureImage(e,t,n){const i=this,s=this.json,a=s.textures[e],c=s.images[t],u=(c.uri||c.bufferView)+":"+a.sampler;if(this.textureCache[u])return this.textureCache[u];const h=this.loadImageSource(t,n).then(function(f){f.flipY=!1,f.name=a.name||c.name||"",f.name===""&&typeof c.uri=="string"&&c.uri.startsWith("data:image/")===!1&&(f.name=c.uri);const m=(s.samplers||{})[a.sampler]||{};return f.magFilter=og[m.magFilter]||ii,f.minFilter=og[m.minFilter]||Yi,f.wrapS=ag[m.wrapS]||Qs,f.wrapT=ag[m.wrapT]||Qs,f.generateMipmaps=!f.isCompressedTexture&&f.minFilter!==zn&&f.minFilter!==ii,i.associations.set(f,{textures:e}),f}).catch(function(){return null});return this.textureCache[u]=h,h}loadImageSource(e,t){const n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(p=>p.clone());const a=i.images[e],c=self.URL||self.webkitURL;let u=a.uri||"",h=!1;if(a.bufferView!==void 0)u=n.getDependency("bufferView",a.bufferView).then(function(p){h=!0;const m=new Blob([p],{type:a.mimeType});return u=c.createObjectURL(m),u});else if(a.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const f=Promise.resolve(u).then(function(p){return new Promise(function(m,g){let x=m;t.isImageBitmapLoader===!0&&(x=function(M){const v=new Sn(M);v.needsUpdate=!0,m(v)}),t.load(Zo.resolveURL(p,s.path),x,void 0,g)})}).then(function(p){return h===!0&&c.revokeObjectURL(u),qi(p,a),p.userData.mimeType=a.mimeType||_I(a.uri),p}).catch(function(p){throw console.error("THREE.GLTFLoader: Couldn't load texture",u),p});return this.sourceCache[e]=f,f}assignTexture(e,t,n,i){const s=this;return this.getDependency("texture",n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),s.extensions[St.KHR_TEXTURE_TRANSFORM]){const c=n.extensions!==void 0?n.extensions[St.KHR_TEXTURE_TRANSFORM]:void 0;if(c){const u=s.associations.get(a);a=s.extensions[St.KHR_TEXTURE_TRANSFORM].extendTexture(a,c),s.associations.set(a,u)}}return i!==void 0&&(a.colorSpace=i),e[t]=a,a})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){const c="PointsMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Xg,Ai.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,u.sizeAttenuation=!1,this.cache.add(c,u)),n=u}else if(e.isLine){const c="LineBasicMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Gc,Ai.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,this.cache.add(c,u)),n=u}if(i||s||a){let c="ClonedMaterial:"+n.uuid+":";i&&(c+="derivative-tangents:"),s&&(c+="vertex-colors:"),a&&(c+="flat-shading:");let u=this.cache.get(c);u||(u=n.clone(),s&&(u.vertexColors=!0),a&&(u.flatShading=!0),i&&(u.normalScale&&(u.normalScale.y*=-1),u.clearcoatNormalScale&&(u.clearcoatNormalScale.y*=-1)),this.cache.add(c,u),this.associations.set(u,this.associations.get(n))),n=u}e.material=n}getMaterialType(){return as}loadMaterial(e){const t=this,n=this.json,i=this.extensions,s=n.materials[e];let a;const c={},u=s.extensions||{},h=[];if(u[St.KHR_MATERIALS_UNLIT]){const p=i[St.KHR_MATERIALS_UNLIT];a=p.getMaterialType(),h.push(p.extendParams(c,s,t))}else{const p=s.pbrMetallicRoughness||{};if(c.color=new $e(1,1,1),c.opacity=1,Array.isArray(p.baseColorFactor)){const m=p.baseColorFactor;c.color.setRGB(m[0],m[1],m[2],Hn),c.opacity=m[3]}p.baseColorTexture!==void 0&&h.push(t.assignTexture(c,"map",p.baseColorTexture,bn)),c.metalness=p.metallicFactor!==void 0?p.metallicFactor:1,c.roughness=p.roughnessFactor!==void 0?p.roughnessFactor:1,p.metallicRoughnessTexture!==void 0&&(h.push(t.assignTexture(c,"metalnessMap",p.metallicRoughnessTexture)),h.push(t.assignTexture(c,"roughnessMap",p.metallicRoughnessTexture))),a=this._invokeOne(function(m){return m.getMaterialType&&m.getMaterialType(e)}),h.push(Promise.all(this._invokeAll(function(m){return m.extendMaterialParams&&m.extendMaterialParams(e,c)})))}s.doubleSided===!0&&(c.side=Xn);const f=s.alphaMode||uh.OPAQUE;if(f===uh.BLEND?(c.transparent=!0,c.depthWrite=!1):(c.transparent=!1,f===uh.MASK&&(c.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&a!==ui&&(h.push(t.assignTexture(c,"normalMap",s.normalTexture)),c.normalScale=new tt(1,1),s.normalTexture.scale!==void 0)){const p=s.normalTexture.scale;c.normalScale.set(p,p)}if(s.occlusionTexture!==void 0&&a!==ui&&(h.push(t.assignTexture(c,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(c.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&a!==ui){const p=s.emissiveFactor;c.emissive=new $e().setRGB(p[0],p[1],p[2],Hn)}return s.emissiveTexture!==void 0&&a!==ui&&h.push(t.assignTexture(c,"emissiveMap",s.emissiveTexture,bn)),Promise.all(h).then(function(){const p=new a(c);return s.name&&(p.name=s.name),qi(p,s),t.associations.set(p,{materials:e}),s.extensions&&Qr(i,p,s),p})}createUniqueName(e){const t=Ot.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,i=this.primitiveCache;function s(c){return n[St.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(c,t).then(function(u){return cg(u,c,t)})}const a=[];for(let c=0,u=e.length;c<u;c++){const h=e[c],f=gI(h),p=i[f];if(p)a.push(p.promise);else{let m;h.extensions&&h.extensions[St.KHR_DRACO_MESH_COMPRESSION]?m=s(h):m=cg(new mn,h,t),i[f]={primitive:h,promise:m},a.push(m)}}return Promise.all(a)}loadMesh(e){const t=this,n=this.json,i=this.extensions,s=n.meshes[e],a=s.primitives,c=[];for(let u=0,h=a.length;u<h;u++){const f=a[u].material===void 0?fI(this.cache):this.getDependency("material",a[u].material);c.push(f)}return c.push(t.loadGeometries(a)),Promise.all(c).then(function(u){const h=u.slice(0,u.length-1),f=u[u.length-1],p=[];for(let g=0,x=f.length;g<x;g++){const M=f[g],v=a[g];let _;const A=h[g];if(v.mode===ci.TRIANGLES||v.mode===ci.TRIANGLE_STRIP||v.mode===ci.TRIANGLE_FAN||v.mode===void 0)_=s.isSkinnedMesh===!0?new Gg(M,A):new Ee(M,A),_.isSkinnedMesh===!0&&_.normalizeSkinWeights(),v.mode===ci.TRIANGLE_STRIP?_.geometry=rg(_.geometry,Tg):v.mode===ci.TRIANGLE_FAN&&(_.geometry=rg(_.geometry,Qh));else if(v.mode===ci.LINES)_=new jg(M,A);else if(v.mode===ci.LINE_STRIP)_=new mi(M,A);else if(v.mode===ci.LINE_LOOP)_=new DR(M,A);else if(v.mode===ci.POINTS)_=new NR(M,A);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+v.mode);Object.keys(_.geometry.morphAttributes).length>0&&mI(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),qi(_,s),v.extensions&&Qr(i,_,v),t.assignFinalMaterial(_),p.push(_)}for(let g=0,x=p.length;g<x;g++)t.associations.set(p[g],{meshes:e,primitives:g});if(p.length===1)return s.extensions&&Qr(i,p[0],s),p[0];const m=new $i;s.extensions&&Qr(i,m,s),t.associations.set(m,{meshes:e});for(let g=0,x=p.length;g<x;g++)m.add(p[g]);return m})}loadCamera(e){let t;const n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new kn(wg.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new bd(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),qi(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this._loadNodeShallow(t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){const s=i.pop(),a=i,c=[],u=[];for(let h=0,f=a.length;h<f;h++){const p=a[h];if(p){c.push(p);const m=new ot;s!==null&&m.fromArray(s.array,h*16),u.push(m)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[h])}return new ia(c,u)})}loadAnimation(e){const t=this.json,n=this,i=t.animations[e],s=i.name?i.name:"animation_"+e,a=[],c=[],u=[],h=[],f=[];for(let p=0,m=i.channels.length;p<m;p++){const g=i.channels[p],x=i.samplers[g.sampler],M=g.target,v=M.node,_=i.parameters!==void 0?i.parameters[x.input]:x.input,A=i.parameters!==void 0?i.parameters[x.output]:x.output;M.node!==void 0&&(a.push(this.getDependency("node",v)),c.push(this.getDependency("accessor",_)),u.push(this.getDependency("accessor",A)),h.push(x),f.push(M))}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u),Promise.all(h),Promise.all(f)]).then(function(p){const m=p[0],g=p[1],x=p[2],M=p[3],v=p[4],_=[];for(let A=0,w=m.length;A<w;A++){const b=m[A],B=g[A],U=x[A],O=M[A],H=v[A];if(b===void 0)continue;b.updateMatrix&&b.updateMatrix();const L=n._createAnimationTracks(b,B,U,O,H);if(L)for(let P=0;P<L.length;P++)_.push(L[P])}return new Bc(s,void 0,_)})}createNodeMesh(e){const t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){const a=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&a.traverse(function(c){if(c.isMesh)for(let u=0,h=i.weights.length;u<h;u++)c.morphTargetInfluences[u]=i.weights[u]}),a})}loadNode(e){const t=this.json,n=this,i=t.nodes[e],s=n._loadNodeShallow(e),a=[],c=i.children||[];for(let h=0,f=c.length;h<f;h++)a.push(n.getDependency("node",c[h]));const u=i.skin===void 0?Promise.resolve(null):n.getDependency("skin",i.skin);return Promise.all([s,Promise.all(a),u]).then(function(h){const f=h[0],p=h[1],m=h[2];m!==null&&f.traverse(function(g){g.isSkinnedMesh&&g.bind(m,vI)});for(let g=0,x=p.length;g<x;g++)f.add(p[g]);return f})}_loadNodeShallow(e){const t=this.json,n=this.extensions,i=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const s=t.nodes[e],a=s.name?i.createUniqueName(s.name):"",c=[],u=i._invokeOne(function(h){return h.createNodeMesh&&h.createNodeMesh(e)});return u&&c.push(u),s.camera!==void 0&&c.push(i.getDependency("camera",s.camera).then(function(h){return i._getNodeRef(i.cameraCache,s.camera,h)})),i._invokeAll(function(h){return h.createNodeAttachment&&h.createNodeAttachment(e)}).forEach(function(h){c.push(h)}),this.nodeCache[e]=Promise.all(c).then(function(h){let f;if(s.isBone===!0?f=new Vc:h.length>1?f=new $i:h.length===1?f=h[0]:f=new Jt,f!==h[0])for(let p=0,m=h.length;p<m;p++)f.add(h[p]);if(s.name&&(f.userData.name=s.name,f.name=a),qi(f,s),s.extensions&&Qr(n,f,s),s.matrix!==void 0){const p=new ot;p.fromArray(s.matrix),f.applyMatrix4(p)}else s.translation!==void 0&&f.position.fromArray(s.translation),s.rotation!==void 0&&f.quaternion.fromArray(s.rotation),s.scale!==void 0&&f.scale.fromArray(s.scale);return i.associations.has(f)||i.associations.set(f,{}),i.associations.get(f).nodes=e,f}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],i=this,s=new $i;n.name&&(s.name=i.createUniqueName(n.name)),qi(s,n),n.extensions&&Qr(t,s,n);const a=n.nodes||[],c=[];for(let u=0,h=a.length;u<h;u++)c.push(i.getDependency("node",a[u]));return Promise.all(c).then(function(u){for(let f=0,p=u.length;f<p;f++)s.add(u[f]);const h=f=>{const p=new Map;for(const[m,g]of i.associations)(m instanceof Ai||m instanceof Sn)&&p.set(m,g);return f.traverse(m=>{const g=i.associations.get(m);g!=null&&p.set(m,g)}),p};return i.associations=h(s),s})}_createAnimationTracks(e,t,n,i,s){const a=[],c=e.name?e.name:e.uuid,u=[];gr[s.path]===gr.weights?e.traverse(function(m){m.morphTargetInfluences&&u.push(m.name?m.name:m.uuid)}):u.push(c);let h;switch(gr[s.path]){case gr.weights:h=ro;break;case gr.rotation:h=cs;break;case gr.position:case gr.scale:h=ls;break;default:switch(n.itemSize){case 1:h=ro;break;case 2:case 3:default:h=ls;break}break}const f=i.interpolation!==void 0?dI[i.interpolation]:ea,p=this._getArrayFromAccessor(n);for(let m=0,g=u.length;m<g;m++){const x=new h(u[m]+"."+gr[s.path],t.array,p,f);i.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(x),a.push(x)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=ad(t.constructor),i=new Float32Array(t.length);for(let s=0,a=t.length;s<a;s++)i[s]=t[s]*n;t=i}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const i=this instanceof cs?hI:s_;return new i(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function xI(r,e,t){const n=e.attributes,i=new er;if(n.POSITION!==void 0){const c=t.json.accessors[n.POSITION],u=c.min,h=c.max;if(u!==void 0&&h!==void 0){if(i.set(new F(u[0],u[1],u[2]),new F(h[0],h[1],h[2])),c.normalized){const f=ad(Ks[c.componentType]);i.min.multiplyScalar(f),i.max.multiplyScalar(f)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const s=e.targets;if(s!==void 0){const c=new F,u=new F;for(let h=0,f=s.length;h<f;h++){const p=s[h];if(p.POSITION!==void 0){const m=t.json.accessors[p.POSITION],g=m.min,x=m.max;if(g!==void 0&&x!==void 0){if(u.setX(Math.max(Math.abs(g[0]),Math.abs(x[0]))),u.setY(Math.max(Math.abs(g[1]),Math.abs(x[1]))),u.setZ(Math.max(Math.abs(g[2]),Math.abs(x[2]))),m.normalized){const M=ad(Ks[m.componentType]);u.multiplyScalar(M)}c.max(u)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(c)}r.boundingBox=i;const a=new wi;i.getCenter(a.center),a.radius=i.min.distanceTo(i.max)/2,r.boundingSphere=a}function cg(r,e,t){const n=e.attributes,i=[];function s(a,c){return t.getDependency("accessor",a).then(function(u){r.setAttribute(c,u)})}for(const a in n){const c=od[a]||a.toLowerCase();c in r.attributes||i.push(s(n[a],c))}if(e.indices!==void 0&&!r.index){const a=t.getDependency("accessor",e.indices).then(function(c){r.setIndex(c)});i.push(a)}return wt.workingColorSpace!==Hn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${wt.workingColorSpace}" not supported.`),qi(r,e),xI(r,e,t),Promise.all(i).then(function(){return e.targets!==void 0?pI(r,e.targets,t):r})}const o_=new zC,bI=new t_;let so=0;async function SI(r,e){return new Promise((t,n)=>{o_.load(r,i=>{const s=i.scene;e.add(s),s.traverse(u=>{u.isMesh&&(u.castShadow=!0,u.receiveShadow=!0)}),so++;const a=`Asset ${so}`,c=Ld();c&&Dd(c,a,s),t(s)},void 0,i=>n(i))})}async function MI(r,e){const t=URL.createObjectURL(r);try{return await SI(t,e)}finally{URL.revokeObjectURL(t)}}const TI=[{color:13935988,roughness:.55,metalness:0},{color:13935988,roughness:.55,metalness:0},{color:1118481,roughness:.8,metalness:0},{color:657930,roughness:.1,metalness:0},{color:16052456,roughness:.2,metalness:0},{color:16052456,roughness:.05,metalness:0,opacity:.3,transparent:!0},{color:4881051,roughness:.15,metalness:0},{color:11885162,roughness:.7,metalness:0},{color:15789280,roughness:.3,metalness:0},{color:14723210,roughness:.4,metalness:0},{color:14723210,roughness:.4,metalness:0}];function Lc(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Float32Array(t.buffer)}function a_(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Uint32Array(t.buffer)}function cd(r){for(let e=0;e<r.length;e+=3){const t=r[e+1],n=r[e+2];r[e+1]=n,r[e+2]=-t}}function EI(r){const e=Lc(r.vertices),t=a_(r.faces);cd(e);const n=new mn,i=new an(e,3),s=new an(t,1);if(n.setAttribute("position",i),n.setIndex(s),r.uvs){const f=Lc(r.uvs);n.setAttribute("uv",new an(f,2))}if(r.normals){const f=Lc(r.normals);cd(f),n.setAttribute("normal",new an(f,3))}else n.computeVertexNormals();const a=TI.map(f=>new as({color:f.color,roughness:f.roughness,metalness:f.metalness,side:Xn,transparent:f.transparent||!1,opacity:f.opacity!==void 0?f.opacity:1})),c=r.groups||[];let u;if(s&&c.length>0){for(const f of c)n.addGroup(f.start,f.count,f.materialIndex);u=new Ee(n,a)}else u=new Ee(n,a[0]);u.castShadow=!0,u.receiveShadow=!0;const h=new $i;return h.add(u),h}async function dh(r,e,t){const n=new URLSearchParams;if(e.body_type&&n.set("body_type",e.body_type),e.morphs&&typeof e.morphs=="object")for(const[m,g]of Object.entries(e.morphs))g!=null&&n.set(`morph_${m}`,String(g));if(e.user_morphs&&typeof e.user_morphs=="object")for(const[m,g]of Object.entries(e.user_morphs))g!=null&&n.set(`morph_${m}`,String(g));const i=["age","mass","tone","height"],s=e.meta||{};for(const m of i){const g=s[m]??e[`meta_${m}`];g!=null&&n.set(`meta_${m}`,String(g))}const a=`/api/character/mesh/?${n.toString()}`,c=await fetch(a);if(!c.ok)throw new Error(`Character mesh API error: ${c.status}`);const u=await c.json(),h=EI(u);if(r.add(h),h.userData.bodyType=e.body_type||"Female_Caucasian",h.userData.morphs={...e.morphs||{},...e.user_morphs||{}},h.userData.meta={...e.meta||{}},h.userData.presetName=t,e.hair_style&&e.hair_style.url)try{const m=await AI(e.hair_style.url);m.userData.isHair=!0,m.traverse(g=>{g.isMesh&&(g.userData.isHair=!0)}),h.add(m),console.log("✓ Hair loaded:",e.hair_style.name)}catch(m){console.error("Failed to load hair:",m)}if(e.garments&&Array.isArray(e.garments))for(const m of e.garments)try{const g=await wI(m,e.body_type);g.userData.isGarment=!0,h.add(g),console.log("✓ Garment loaded:",m.id)}catch(g){console.error("Failed to load garment:",m.id,g)}so++;const f=t||`Character ${so}`,p=Ld();return p&&Dd(p,f,h),h}async function AI(r){return new Promise((e,t)=>{o_.load(r,n=>{const i=n.scene;i.traverse(s=>{if(s.isMesh&&(s.castShadow=!0,s.receiveShadow=!0,s.material)){if(s.material.color){const a=s.material.color;a.r>.9&&a.g>.9&&a.b>.9&&s.material.color.setRGB(.1,.08,.06)}s.material.roughness===void 0&&(s.material.roughness=.8),s.material.metalness===void 0&&(s.material.metalness=0)}}),e(i)},void 0,n=>t(n))})}async function wI(r,e){const{id:t,offset:n=.006,stiffness:i=.8,color:s=[.3,.35,.5],roughness:a=.8,metalness:c=0}=r,u=s[0]??.3,h=s[1]??.35,f=s[2]??.5,p=`garment_id=${encodeURIComponent(t)}&body_type=${encodeURIComponent(e)}&offset=${n}&stiffness=${i}&color_r=${u.toFixed(3)}&color_g=${h.toFixed(3)}&color_b=${f.toFixed(3)}`,m=await fetch(`/api/character/garment/fit/?${p}`);if(!m.ok)throw new Error(`Garment fit API error: ${m.status}`);const g=await m.json();if(g.error)throw new Error(g.error);const x=Lc(g.vertices);cd(x);const M=a_(g.faces),v=new mn;v.setAttribute("position",new an(x,3)),v.setIndex(new an(M,1)),v.computeVertexNormals();const _=new $e(g.color[0],g.color[1],g.color[2]),A=new as({color:_,roughness:a,metalness:c,side:Xn,polygonOffset:!0,polygonOffsetFactor:-1,polygonOffsetUnit:-1}),w=new Ee(v,A);return w.castShadow=!0,w.receiveShadow=!0,w.userData.garmentId=t,w.userData.offset=n,w.userData.stiffness=i,w.userData.originalColor=[u,h,f],w.userData.roughness=a,w.userData.metalness=c,w.name=t,w}function PI(r,e,t){const n=bI.parse(r),i=new dC(n.skeleton.bones[0]);i.skeleton=n.skeleton,i.visible=!0,i.userData.isRig=!0,i.renderOrder=999,i.material&&(i.material.depthTest=!1,i.material.depthWrite=!1);const s=n.skeleton.bones[0];s.userData.isRig=!0,e.add(s),e.add(i);const a=new Zg(s),c=a.clipAction(n.clip);c.setLoop(gd),c.play(),c.paused=!0,so++;const u=Ld();u&&Dd(u,t||`BVH ${so}`,s);const h=n.clip.duration||1;return{mixer:a,action:c,skeleton:i,clip:n.clip,rootBone:s,duration:h}}class RI{constructor(e){this._canvas=e,this._recorder=null,this._chunks=[]}start(e=30){const t=this._canvas.captureStream(e);this._chunks=[];const n=MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm;codecs=vp8";this._recorder=new MediaRecorder(t,{mimeType:n,videoBitsPerSecond:8e6}),this._recorder.ondataavailable=i=>{i.data.size>0&&this._chunks.push(i.data)},this._recorder.start()}stop(){return new Promise(e=>{this._recorder.onstop=()=>{const t=new Blob(this._chunks,{type:"video/webm"});this._chunks=[],e(t)},this._recorder.stop()})}get isRecording(){var e;return((e=this._recorder)==null?void 0:e.state)==="recording"}async stopAndDownload(e="theatre-export.webm"){const t=await this.stop(),n=URL.createObjectURL(t),i=document.createElement("a");i.href=n,i.download=e,i.click(),URL.revokeObjectURL(n)}}async function CI(){const r=await fetch("/api/character/scenes/");if(!r.ok)throw new Error(`Scene list error: ${r.status}`);return(await r.json()).scenes||[]}async function II(r){const e=await fetch(`/api/character/scene/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Scene load error: ${e.status}`);return e.json()}async function LI(r,e){const t=await fetch("/api/character/scene/save/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:r,data:e})});if(!t.ok){const n=await t.json().catch(()=>({}));throw new Error(n.error||`Scene save error: ${t.status}`)}return t.json()}async function DI(){const r=await fetch("/api/character/models/");if(!r.ok)throw new Error(`Model list error: ${r.status}`);return(await r.json()).presets||[]}async function lg(r){const e=await fetch(`/api/character/model/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Model load error: ${e.status}`);return e.json()}async function NI(){const r=await fetch("/api/character/animations/");if(!r.ok)throw new Error(`Animation list error: ${r.status}`);return(await r.json()).categories||{}}async function OI(r,e){const t=`/api/character/bvh/${encodeURIComponent(r)}/${encodeURIComponent(e)}/`,n=await fetch(t);if(!n.ok)throw new Error(`BVH load error: ${n.status}`);return n.text()}const fh={ballet_stage:{name:"Ballet Stage",description:"Warme Spotlights, theatralisch dunkel",camera:{position:{x:0,y:1.6,z:5},fov:35},lights:{spotLeft:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:-3,y:6,z:3}},spotRight:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:3,y:6,z:3}},backLight:{intensity:25,color:{r:.4,g:.267,b:.667},position:{x:0,y:5,z:-4}}}},studio_bright:{name:"Studio Bright",description:"Helle, gleichmäßige Beleuchtung für Details",camera:{position:{x:0,y:1.6,z:4},fov:40},lights:{spotLeft:{intensity:80,color:{r:1,g:1,b:1},position:{x:-2,y:5,z:4}},spotRight:{intensity:80,color:{r:1,g:1,b:1},position:{x:2,y:5,z:4}},backLight:{intensity:30,color:{r:.9,g:.95,b:1},position:{x:0,y:4,z:-3}}}},cinematic_moody:{name:"Cinematic Moody",description:"Dramatisches Film-noir-Licht, starke Schatten",camera:{position:{x:2,y:1.4,z:4},fov:28},lights:{spotLeft:{intensity:15,color:{r:1,g:.8,b:.6},position:{x:-4,y:7,z:2}},spotRight:{intensity:2,color:{r:.6,g:.7,b:.9},position:{x:4,y:3,z:3}},backLight:{intensity:10,color:{r:.3,g:.5,b:1},position:{x:1,y:6,z:-5}}}},fashion_show:{name:"Fashion Show",description:"Laufsteg-Beleuchtung, kühles Weiß von oben",camera:{position:{x:0,y:1.2,z:6},fov:50},lights:{spotLeft:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:-2,y:8,z:2}},spotRight:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:2,y:8,z:2}},backLight:{intensity:5,color:{r:1,g:1,b:1},position:{x:0,y:3,z:-2}}}},sunset_warm:{name:"Sunset Warm",description:"Goldene Stunde, warmes Orange-Gold",camera:{position:{x:-1,y:1.5,z:4.5},fov:42},lights:{spotLeft:{intensity:14,color:{r:1,g:.7,b:.4},position:{x:-5,y:4,z:3}},spotRight:{intensity:6,color:{r:1,g:.85,b:.7},position:{x:3,y:5,z:2}},backLight:{intensity:8,color:{r:.8,g:.4,b:.6},position:{x:2,y:5,z:-4}}}}};function ph(r,e,t,n){console.log(`[Preset] Applying: ${r.name}`),e.position.set(r.camera.position.x,r.camera.position.y,r.camera.position.z),e.fov=r.camera.fov,e.updateProjectionMatrix(),n&&(n.target.set(0,.9,0),n.update()),mh(t.spotLeft,r.lights.spotLeft),mh(t.spotRight,r.lights.spotRight),mh(t.backLight,r.lights.backLight),console.log(`✓ Preset "${r.name}" applied (direct Three.js)`)}function mh(r,e){r&&(r.intensity=e.intensity,r.color.setRGB(e.color.r,e.color.g,e.color.b),r.position.set(e.position.x,e.position.y,e.position.z))}window.addEventListener("DOMContentLoaded",()=>{const r=document.getElementById("theatre-canvas");if(!r){console.error("theatre-canvas not found");return}const{scene:e,camera:t,renderer:n,controls:i,lights:s,lightIcons:a,transformControls:c}=UC(r);window.scene=e,window.lights=s,window.lightIcons=a,window.transformControls=c,window.activeMixer=null,window.isPlaying=!1,window.currentTime=0,window.animDuration=1;const u=new Jg,h=new tt;let f=null,p=null;const m=[];let g=null,x=null;async function M(){try{const[R,z]=await Promise.all([fetch("/api/character/skeleton/"),fetch("/api/character/skin-weights/")]);R.ok&&(g=await R.json()),z.ok&&(x=await z.json()),console.log("✓ Loaded skeleton and skin weights")}catch(R){console.warn("Failed to load skeleton/weights:",R)}}M();function v(R,z,K,ie){const xe=new t_().parse(R),we=new Zg(z),Ie=we.clipAction(xe.clip);Ie.setLoop(gd),Ie.play(),Ie.paused=!0;const nt=xe.clip.duration||1;return console.log("✓ BVH animation loaded on SkinnedMesh:",ie,nt+"s"),{mixer:we,action:Ie,duration:nt}}function _(R){if(!g||!x)return console.warn("Cannot convert to SkinnedMesh: skeleton/weights not loaded"),null;if(R.userData.isSkinnedMesh)return console.log("Already a SkinnedMesh"),R.userData.skinnedMesh;const z=R.children.find(Xe=>Xe.isMesh);if(!z)return console.warn("No mesh found in character group"),null;console.log("Converting to SkinnedMesh...");const K=z.geometry.clone(),ie=K.attributes.position.count,ye=new Float32Array(ie*4),xe=new Float32Array(ie*4);for(let Xe=0;Xe<ie;Xe++){const yt=x.indices[Xe]||[0,0,0,0],On=x.weights[Xe]||[1,0,0,0];ye[Xe*4+0]=yt[0],ye[Xe*4+1]=yt[1],ye[Xe*4+2]=yt[2],ye[Xe*4+3]=yt[3],xe[Xe*4+0]=On[0],xe[Xe*4+1]=On[1],xe[Xe*4+2]=On[2],xe[Xe*4+3]=On[3]}K.setAttribute("skinIndex",new Xt(ye,4)),K.setAttribute("skinWeight",new Xt(xe,4));const we=[],Ie=[];for(const Xe of g.bones){const yt=new Vc;yt.name=Xe.name,yt.position.fromArray(Xe.position),yt.quaternion.fromArray(Xe.quaternion),yt.scale.fromArray(Xe.scale),we.push(yt);const On=new ot;Xe.inverse&&On.fromArray(Xe.inverse),Ie.push(On)}for(let Xe=0;Xe<g.bones.length;Xe++){const yt=g.bones[Xe].parent;yt>=0&&we[yt].add(we[Xe])}const nt=new ia(we,Ie),Et=we[0],qt=z.material,Ke=new Gg(K,qt);Ke.castShadow=!0,Ke.receiveShadow=!0,Ke.add(Et),Ke.bind(nt);const ct=z.position.clone(),Gt=z.rotation.clone(),Rt=z.scale.clone();return R.remove(z),Ke.position.copy(ct),Ke.rotation.copy(Gt),Ke.scale.copy(Rt),R.add(Ke),R.userData.isSkinnedMesh=!0,R.userData.skinnedMesh=Ke,R.userData.skeleton=nt,R.userData.rootBone=Et,console.log("✓ Converted to SkinnedMesh with",we.length,"bones"),Ke}r.addEventListener("click",R=>{const z=r.getBoundingClientRect();h.x=(R.clientX-z.left)/z.width*2-1,h.y=-((R.clientY-z.top)/z.height)*2+1,u.setFromCamera(h,t);const K=[a.spotLeftIcon,a.spotRightIcon,a.backLightIcon],ie=u.intersectObjects(K,!0);if(ie.length>0){let xe=ie[0].object;for(;xe.parent&&!xe.userData.light;)xe=xe.parent;if(xe.userData.light){f=xe,p=null,c.attach(xe),console.log("✓ Licht ausgewählt:",xe.userData.light),Be(xe.userData.light);return}}const ye=u.intersectObjects(m,!0);if(ye.length>0){const xe=ye[0].object;if(xe.userData.isGarment){p=null,f=null,c.attach(xe),console.log("✓ Garment ausgewählt:",xe.name),Ze(xe);return}let we=xe;for(;we.parent&&!we.userData.isCharacter;)we=we.parent;if(we.userData.isCharacter){p=we,f=null,c.attach(we),console.log("✓ Character ausgewählt:",we.userData.presetName),Ne(we);return}}c.detach(),f=null,p=null,W()});const{sheet:A}=BC();kC(A,t),Sc(A,"Spot Left",s.spotLeft),Sc(A,"Spot Right",s.spotRight),Sc(A,"Back Light",s.backLight);const w=new RI(n.domElement);let b=null,B=null;const U=new QR;document.querySelectorAll(".menu-item").forEach(R=>{const z=R.querySelector(".menu-dropdown");z&&(R.addEventListener("click",K=>{K.stopPropagation(),document.querySelectorAll(".menu-item").forEach(ie=>ie.classList.remove("active")),R.classList.toggle("active")}),z.addEventListener("click",K=>{K.stopPropagation()}))}),document.addEventListener("click",()=>{document.querySelectorAll(".menu-item").forEach(R=>R.classList.remove("active"))}),document.querySelectorAll("[data-preset]").forEach(R=>{R.addEventListener("click",()=>{const z=R.getAttribute("data-preset"),K=fh[z];K?(ph(K,t,s,i),console.log("✓ Applied preset:",K.name),document.querySelectorAll(".menu-item").forEach(ie=>ie.classList.remove("active"))):console.error("Preset not found:",z)})}),document.querySelectorAll(".panel-tab").forEach(R=>{R.addEventListener("click",()=>{const z=R.getAttribute("data-tab");document.querySelectorAll(".panel-tab").forEach(ie=>ie.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ie=>ie.classList.remove("active")),R.classList.add("active");const K=document.getElementById(z);K&&K.classList.add("active")})});const O=document.getElementById("btn-translate-mode"),H=document.getElementById("btn-rotate-mode"),L=document.getElementById("btn-toggle-lights");O&&O.addEventListener("click",()=>{c.setMode("translate"),O.classList.add("active"),H.classList.remove("active")}),H&&H.addEventListener("click",()=>{c.setMode("rotate"),H.classList.add("active"),O.classList.remove("active")});let P=!0;L&&L.addEventListener("click",()=>{P=!P,Object.values(a).forEach(R=>{R.visible=P}),P?L.classList.add("active"):L.classList.remove("active")});const V=document.getElementById("btn-toggle-model");let ee=!0;V&&V.addEventListener("click",()=>{ee=!ee,e.traverse(R=>{R.isMesh&&!R.userData.isGarment&&!R.userData.isHair&&!R.userData.isRig&&(R.visible=ee)}),V.classList.toggle("active",ee)});const Q=document.getElementById("btn-toggle-clothes");let ae=!0;Q&&Q.addEventListener("click",()=>{ae=!ae,e.traverse(R=>{R.isMesh&&(R.userData.isGarment||R.userData.isHair)&&(R.visible=ae)}),Q.classList.toggle("active",ae)});const ce=document.getElementById("btn-toggle-rig");let J=!1;ce&&ce.addEventListener("click",()=>{J=!J,e.traverse(R=>{(R.isSkeletonHelper||R.userData.isRig)&&(R.visible=J)}),ce.classList.toggle("active",J)});const de=document.getElementById("btn-play-animation");de&&de.addEventListener("click",()=>{const R=document.getElementById("btnPlayPause");R&&R.click()});function re(R){const z=document.getElementById(R);z&&(z.style.display="flex")}function _e(R){const z=document.getElementById(R);z&&(z.style.display="none")}document.querySelectorAll("[data-close-modal]").forEach(R=>{R.addEventListener("click",()=>{var z;(z=R.closest(".theatre-modal-overlay"))==null||z.style.removeProperty("display")})}),document.querySelectorAll(".theatre-modal-overlay").forEach(R=>{R.addEventListener("click",z=>{z.target===R&&R.style.removeProperty("display")})});const Me=document.getElementById("menu-scene-load");Me&&Me.addEventListener("click",async()=>{const R=document.getElementById("scene-list-body");R.innerHTML='<div class="loading-msg">Lade Scenes...</div>',re("modal-scene-load");try{const z=await CI();if(z.length===0){R.innerHTML='<div class="loading-msg">Keine Scenes gefunden.</div>';return}R.innerHTML="";for(const K of z){const ie=document.createElement("div");ie.style.cssText="padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;",ie.innerHTML=`<span>${K.label||K.name}</span>`,ie.addEventListener("click",()=>Ue(K.name)),ie.addEventListener("mouseenter",()=>ie.style.background="rgba(124, 92, 191, 0.2)"),ie.addEventListener("mouseleave",()=>ie.style.background=""),R.appendChild(ie)}}catch(z){R.innerHTML=`<div class="loading-msg">Fehler: ${z.message}</div>`}});async function Ue(R){_e("modal-scene-load");try{const z=await II(R);if(console.log("Scene loaded:",R,z),z.characters&&Array.isArray(z.characters))for(const K of z.characters){const ie=await dh(e,K,K.name||R);ie.userData.isCharacter=!0,ie.userData.presetName=K.name||R,ie.userData.bodyType=K.body_type||"Unknown",m.push(ie)}}catch(z){console.error("Scene load error:",z),alert("Scene laden fehlgeschlagen: "+z.message)}}const Je=document.getElementById("menu-scene-save"),pt=document.getElementById("scene-save-btn"),le=document.getElementById("scene-save-name");Je&&Je.addEventListener("click",()=>{re("modal-scene-save"),le&&(le.value="",le.focus())}),pt&&le&&(pt.addEventListener("click",async()=>{const R=le.value.trim();if(R){pt.disabled=!0,pt.textContent="Speichere...";try{const z={camera:{position:t.position.toArray(),fov:t.fov,target:i.target.toArray()},lights:{spotLeft:{position:s.spotLeft.position.toArray(),intensity:s.spotLeft.intensity,color:"#"+s.spotLeft.color.getHexString()},spotRight:{position:s.spotRight.position.toArray(),intensity:s.spotRight.intensity,color:"#"+s.spotRight.color.getHexString()},backLight:{position:s.backLight.position.toArray(),intensity:s.backLight.intensity,color:"#"+s.backLight.color.getHexString()}},characters:[]},K=await LI(R,z);console.log("Scene saved:",K),_e("modal-scene-save")}catch(z){console.error("Scene save error:",z),alert("Scene speichern fehlgeschlagen: "+z.message)}pt.disabled=!1,pt.textContent="Speichern"}}),le.addEventListener("keydown",R=>{R.key==="Enter"&&pt.click()}));const pe=document.getElementById("model-list"),Fe=document.getElementById("menu-model-load");async function Se(){try{const R=await DI();if(R.length===0){pe.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';return}pe.innerHTML="";for(const z of R){const K=document.createElement("div");K.className="anim-item",K.textContent=z.label||z.name,K.addEventListener("click",async()=>{try{const ie=await lg(z.name),ye=await dh(e,ie,z.name);ye.userData.isCharacter=!0,ye.userData.presetName=z.name,ye.userData.bodyType=ie.body_type||"Unknown",m.push(ye),console.log("Model loaded:",z.name),document.querySelectorAll("#model-list .anim-item").forEach(xe=>xe.classList.remove("active")),K.classList.add("active")}catch(ie){console.error("Model load error:",ie),alert("Modell laden fehlgeschlagen: "+ie.message)}}),pe.appendChild(K)}}catch(R){pe.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${R.message}</div>`}}Se(),Fe&&Fe.addEventListener("click",()=>{document.querySelectorAll(".panel-tab").forEach(K=>K.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(K=>K.classList.remove("active"));const R=document.querySelector('[data-tab="tab-models"]'),z=document.getElementById("tab-models");R&&R.classList.add("active"),z&&z.classList.add("active")});const qe=document.getElementById("anim-tree");async function it(){try{const R=await NI(),z=Object.keys(R);if(z.length===0){qe.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';return}qe.innerHTML="";for(const K of z){const ie=R[K],ye=document.createElement("div");ye.className="anim-cat";const xe=document.createElement("div");xe.className="anim-cat-header",xe.innerHTML=`<i class="fas fa-chevron-right"></i> ${K} (${ie.length})`,xe.addEventListener("click",()=>{ye.classList.toggle("open")}),ye.appendChild(xe);const we=document.createElement("div");we.className="anim-cat-body";for(const Ie of ie){const nt=document.createElement("div");nt.className="anim-item",nt.textContent=Ie.name,nt.addEventListener("click",async()=>{await at(Ie.category,Ie.name),document.querySelectorAll("#anim-tree .anim-item").forEach(Et=>Et.classList.remove("active")),nt.classList.add("active")}),we.appendChild(nt)}ye.appendChild(we),qe.appendChild(ye)}}catch(R){qe.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${R.message}</div>`}}async function at(R,z){try{const K=await OI(R,z);let ie=null;p&&(ie=_(p));const{mixer:ye,action:xe,duration:we}=ie?v(K,ie,e,`${R}/${z}`):PI(K,e,`${R}/${z}`);b&&b.stopAllAction(),b=ye,B=xe,window.activeMixer=b,Ae(we),ue=!1,fe=0,he=we,window.isPlaying=!1,window.currentTime=0,window.animDuration=we,ht(),console.log("Animation loaded:",R,z,we)}catch(K){console.error("Animation load error:",K),alert("Animation laden fehlgeschlagen: "+K.message)}}it();const Pt=document.getElementById("menu-add-glb"),lt=document.getElementById("glb-file-input");Pt&&lt&&(Pt.addEventListener("click",()=>lt.click()),lt.addEventListener("change",async()=>{const R=lt.files[0];if(R){try{await MI(R,e)}catch(z){console.error("GLB load error:",z),alert("Fehler beim Laden der GLB-Datei: "+z.message)}lt.value=""}})),document.querySelectorAll("[data-preset]").forEach(R=>{R.addEventListener("click",()=>{const z=R.getAttribute("data-preset"),K=fh[z];K?(ph(K,t,s,i),console.log("✓ Applied preset:",K.name)):console.error("Preset not found:",z)})});const zt=document.getElementById("menu-add-light");let X=0;zt&&zt.addEventListener("click",()=>{X++;const R=new $g(16777215,1,15);R.position.set((Math.random()-.5)*6,2+Math.random()*3,(Math.random()-.5)*6),e.add(R);const z=new Ee(new ra(.08,8,8),new ui({color:16776960}));R.add(z),Sc(A,`Light ${X}`,R)});const rn=document.getElementById("menu-export-video");rn&&rn.addEventListener("click",async()=>{w.isRecording?(rn.innerHTML='<i class="fas fa-file-video"></i> Export Video',await w.stopAndDownload()):(w.start(30),rn.innerHTML='<i class="fas fa-stop"></i> Stop Recording')});const ut=document.getElementById("btnPlayPause"),mt=document.getElementById("btnStop"),We=document.getElementById("btnFrameBack"),Tt=document.getElementById("btnFrameFwd"),ke=document.getElementById("timelineSlider"),N=document.getElementById("timeCurrent"),E=document.getElementById("timeDuration"),Z=document.getElementById("playIcon");let ue=!1,fe=0,he=1,Oe=1;function Ae(R){he=R||1,E.textContent=Le(he),ke.max=he}function Le(R){const z=Math.floor(R/60),K=Math.floor(R%60);return`${String(z).padStart(2,"0")}:${String(K).padStart(2,"0")}`}function ht(){N.textContent=Le(fe),ke.value=fe,Z&&(Z.className=ue?"fas fa-pause":"fas fa-play")}function me(R){!b||!B||(fe=Math.max(0,Math.min(R,he)),B.time=fe,b.update(0),ht())}ut&&ut.addEventListener("click",()=>{b&&(ue=!ue,window.isPlaying=ue,ue&&B?(B.paused=!1,B.play()):B&&(B.paused=!0),ht())}),mt&&mt.addEventListener("click",()=>{b&&(ue=!1,fe=0,me(0),B&&(B.stop(),B.paused=!0),ht())}),We&&We.addEventListener("click",()=>{me(fe-1/30)}),Tt&&Tt.addEventListener("click",()=>{me(fe+1/30)}),ke&&(ke.addEventListener("mousedown",()=>{}),ke.addEventListener("mouseup",()=>{}),ke.addEventListener("input",()=>{const R=parseFloat(ke.value);me(R)})),document.querySelectorAll(".speed-btn").forEach(R=>{R.addEventListener("click",()=>{const z=parseFloat(R.getAttribute("data-speed"));Oe=z,b&&(b.timeScale=z),document.querySelectorAll(".speed-btn").forEach(K=>K.classList.remove("active")),R.classList.add("active")})}),document.addEventListener("keydown",R=>{R.target.tagName!=="INPUT"&&(R.code==="Space"?(R.preventDefault(),ut&&ut.click()):R.code==="ArrowLeft"?(R.preventDefault(),We&&We.click()):R.code==="ArrowRight"&&(R.preventDefault(),Tt&&Tt.click()))});async function De(){try{const R=await fetch("/api/settings/theatre/");if(!R.ok)return;const z=await R.json();if(z.preset){const K=fh[z.preset];K&&(ph(K,t,s,i),console.log("✓ Auto-applied preset:",K.name))}if(z.model)try{const K=await lg(z.model),ie=await dh(e,K,z.model);if(ie.userData.isCharacter=!0,ie.userData.presetName=z.model,ie.userData.bodyType=K.body_type||"Unknown",m.push(ie),console.log("✓ Auto-loaded model:",z.model),z.animation){const[ye,xe]=z.animation.split("/");ye&&xe&&(await at(ye,xe),console.log("✓ Auto-loaded animation:",z.animation))}}catch(K){console.warn("Auto-load model/animation failed:",K)}}catch(R){console.warn("Failed to load Theatre defaults:",R)}}setTimeout(De,500);function Be(R){document.querySelectorAll(".panel-tab").forEach(Xe=>Xe.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Xe=>Xe.classList.remove("active"));const z=document.querySelector('[data-tab="tab-properties"]'),K=document.getElementById("tab-properties");z&&z.classList.add("active"),K&&K.classList.add("active");const ie=document.getElementById("properties-content");if(!ie)return;const ye=R===s.spotLeft?"Spot Left":R===s.spotRight?"Spot Right":R===s.backLight?"Back Light":"Light",xe="#"+R.color.getHexString();ie.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${ye}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${R.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${R.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${xe}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${R.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${R.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${R.position.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="light-rot-x" value="${(R.rotation.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(R.rotation.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(R.rotation.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const we=document.getElementById("light-intensity"),Ie=document.getElementById("light-intensity-value"),nt=document.getElementById("light-color"),Et=document.getElementById("light-pos-x"),qt=document.getElementById("light-pos-y"),Ke=document.getElementById("light-pos-z");if(we&&(we.oninput=Xe=>{R.intensity=parseFloat(Xe.target.value),Ie.textContent=R.intensity.toFixed(1)}),nt&&(nt.oninput=Xe=>{R.color.setHex(parseInt(Xe.target.value.substring(1),16)),f&&f.children.forEach(yt=>{yt.material&&(yt.material.color.copy(R.color),yt.material.emissive&&yt.material.emissive.copy(R.color))})}),Et&&qt&&Ke){const Xe=()=>{R.position.set(parseFloat(Et.value),parseFloat(qt.value),parseFloat(Ke.value)),f&&(f.position.copy(R.position),f.lookAt(R.target.position))};Et.oninput=Xe,qt.oninput=Xe,Ke.oninput=Xe}const ct=document.getElementById("light-rot-x"),Gt=document.getElementById("light-rot-y"),Rt=document.getElementById("light-rot-z");if(ct&&Gt&&Rt){const Xe=()=>{R.rotation.set(parseFloat(ct.value)*Math.PI/180,parseFloat(Gt.value)*Math.PI/180,parseFloat(Rt.value)*Math.PI/180),f&&f.rotation.copy(R.rotation)};ct.oninput=Xe,Gt.oninput=Xe,Rt.oninput=Xe}}function Ze(R){document.querySelectorAll(".panel-tab").forEach(Xe=>Xe.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Xe=>Xe.classList.remove("active"));const z=document.querySelector('[data-tab="tab-properties"]'),K=document.getElementById("tab-properties");z&&z.classList.add("active"),K&&K.classList.add("active");const ie=document.getElementById("properties-content");if(!ie)return;const ye=R.userData.garmentId||R.name||"Garment",xe=R.material,Ie="#"+xe.color.getHexString(),nt=xe.roughness??.8,Et=xe.metalness??0;ie.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-tshirt"></i> ${ye}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="garment-color" value="${Ie}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Roughness: <span id="garment-roughness-value">${nt.toFixed(2)}</span>
                    </label>
                    <input type="range" id="garment-roughness" min="0" max="1" step="0.01" value="${nt}"
                           style="width:100%;cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Metalness: <span id="garment-metalness-value">${Et.toFixed(2)}</span>
                    </label>
                    <input type="range" id="garment-metalness" min="0" max="1" step="0.01" value="${Et}"
                           style="width:100%;cursor:pointer;" />
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Änderungen wirken sofort
                </div>
            </div>
        `;const qt=document.getElementById("garment-color"),Ke=document.getElementById("garment-roughness"),ct=document.getElementById("garment-roughness-value"),Gt=document.getElementById("garment-metalness"),Rt=document.getElementById("garment-metalness-value");qt&&(qt.oninput=Xe=>{xe.color.setHex(parseInt(Xe.target.value.substring(1),16))}),Ke&&ct&&(Ke.oninput=Xe=>{const yt=parseFloat(Xe.target.value);xe.roughness=yt,ct.textContent=yt.toFixed(2)}),Gt&&Rt&&(Gt.oninput=Xe=>{const yt=parseFloat(Xe.target.value);xe.metalness=yt,Rt.textContent=yt.toFixed(2)})}function Ne(R){document.querySelectorAll(".panel-tab").forEach(Rt=>Rt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Rt=>Rt.classList.remove("active"));const z=document.querySelector('[data-tab="tab-properties"]'),K=document.getElementById("tab-properties");z&&z.classList.add("active"),K&&K.classList.add("active");const ie=document.getElementById("properties-content");if(!ie)return;const ye=R.userData.presetName||"Character",xe=R.userData.bodyType||"Unknown",we=R.position,Ie=R.rotation;ie.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${ye}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${xe}</span>
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
                            <input type="number" id="char-pos-x" value="${we.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-pos-y" value="${we.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-pos-z" value="${we.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="char-rot-x" value="${(Ie.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(Ie.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(Ie.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const nt=document.getElementById("char-pos-x"),Et=document.getElementById("char-pos-y"),qt=document.getElementById("char-pos-z");if(nt&&Et&&qt){const Rt=()=>{R.position.set(parseFloat(nt.value),parseFloat(Et.value),parseFloat(qt.value))};nt.oninput=Rt,Et.oninput=Rt,qt.oninput=Rt}const Ke=document.getElementById("char-rot-x"),ct=document.getElementById("char-rot-y"),Gt=document.getElementById("char-rot-z");if(Ke&&ct&&Gt){const Rt=()=>{R.rotation.set(parseFloat(Ke.value)*Math.PI/180,parseFloat(ct.value)*Math.PI/180,parseFloat(Gt.value)*Math.PI/180)};Ke.oninput=Rt,ct.oninput=Rt,Gt.oninput=Rt}_t(R),Ct(R)}function _t(R){const z=document.getElementById("meta-sliders-container");if(!z)return;const K={age:{min:-1,max:1,label:"Alter",step:.01},mass:{min:-1,max:1,label:"Gewicht",step:.01},tone:{min:-1,max:1,label:"Muskeltonus",step:.01},height:{min:-1,max:1,label:"Höhe",step:.01}},ie=R.userData.meta||{age:0,mass:0,tone:0,height:0};let ye="";for(const[xe,we]of Object.entries(K)){const Ie=ie[xe]||0,nt=we.min,Et=we.max;ye+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${we.label}</span>
                        <span id="meta-${xe}-value" style="color:var(--text);">${Ie.toFixed(2)}</span>
                    </div>
                    <input type="range" id="meta-${xe}" min="${nt}" max="${Et}" step="${we.step}" value="${Ie}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}z.innerHTML=ye;for(const xe of Object.keys(K)){const we=document.getElementById(`meta-${xe}`),Ie=document.getElementById(`meta-${xe}-value`);we&&Ie&&(we.oninput=async()=>{const nt=parseFloat(we.value);Ie.textContent=nt.toFixed(2),ie[xe]=nt,R.userData.meta=ie,await st(R)})}}async function st(R){try{let Et=function(Ke){const ct=atob(Ke),Gt=new Uint8Array(ct.length);for(let Rt=0;Rt<ct.length;Rt++)Gt[Rt]=ct.charCodeAt(Rt);return new Float32Array(Gt.buffer)};var z=Et;const K=new URLSearchParams;K.set("body_type",R.userData.bodyType||"Female_Caucasian");const ie=R.userData.morphs||{};for(const[Ke,ct]of Object.entries(ie))ct!=null&&K.set(`morph_${Ke}`,String(ct));const ye=R.userData.meta||{};for(const[Ke,ct]of Object.entries(ye))ct!=null&&K.set(`meta_${Ke}`,String(ct));const xe=`/api/character/mesh/?${K.toString()}`,we=await fetch(xe);if(!we.ok)throw new Error(`Character mesh API error: ${we.status}`);const Ie=await we.json(),nt=R.children.find(Ke=>Ke.isMesh&&!Ke.userData.isHair&&!Ke.userData.isGarment);if(!nt){console.warn("Could not find body mesh to update");return}const qt=Et(Ie.vertices);for(let Ke=0;Ke<qt.length;Ke+=3){const ct=qt[Ke+1],Gt=qt[Ke+2];qt[Ke+1]=Gt,qt[Ke+2]=-ct}if(nt.geometry.attributes.position.array.set(qt),nt.geometry.attributes.position.needsUpdate=!0,Ie.normals){const Ke=Et(Ie.normals);for(let ct=0;ct<Ke.length;ct+=3){const Gt=Ke[ct+1],Rt=Ke[ct+2];Ke[ct+1]=Rt,Ke[ct+2]=-Gt}nt.geometry.attributes.normal.array.set(Ke),nt.geometry.attributes.normal.needsUpdate=!0}else nt.geometry.computeVertexNormals();console.log("✓ Character mesh reloaded")}catch(K){console.error("Failed to reload character mesh:",K)}}function Ct(R){const z=document.getElementById("morph-sliders-container");if(!z)return;const K=R.userData.morphs||{};if(Object.keys(K).length===0){z.innerHTML='<div style="font-size:0.75rem;color:var(--text-muted);text-align:center;padding:10px;">Keine Morphs</div>';return}let ie='<div style="max-height:300px;overflow-y:auto;padding-right:4px;">';for(const[ye,xe]of Object.entries(K)){const we=xe||0;ie+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${ye}</span>
                        <span id="morph-${ye}-value" style="color:var(--text);">${we.toFixed(2)}</span>
                    </div>
                    <input type="range" id="morph-${ye}" min="0" max="1" step="0.01" value="${we}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}ie+="</div>",z.innerHTML=ie;for(const ye of Object.keys(K)){const xe=document.getElementById(`morph-${ye}`),we=document.getElementById(`morph-${ye}-value`);xe&&we&&(xe.oninput=async()=>{const Ie=parseFloat(xe.value);we.textContent=Ie.toFixed(2),K[ye]=Ie,R.userData.morphs=K,await st(R)})}}function W(){const R=document.getElementById("properties-content");R&&(R.innerHTML=`
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `)}function Te(){requestAnimationFrame(Te);const R=U.getDelta();if(b&&ue&&(b.update(R*Oe),fe=B?B.time:0,fe>=he&&(fe=0,B&&(B.time=0)),ht()),f&&f.userData.light){const z=f.userData.light;z.position.copy(f.position),f.lookAt(z.target.position)}i.update(),n.render(e,t)}Te()});
