/* ============ MAISDOT CLASSROOM ============
   Inséré seulement dans classroom-eleve.html et classroom-professeur.html (build.py). CLS_MODE = "eleve" | "prof".
   Élève : identité fixée à la première ouverture, travaux envoyés au professeur en .json signé, correction reçue en .json signé.
   Professeur : groupe de 30 élèves au plus, réception des envois, correction acquis / non acquis par étape, retour signé.
   Signature : HMAC-SHA256 avec le code du groupe (détecte un fichier modifié à la main ou venu d'un autre groupe ;
   ce n'est pas une protection absolue, le code étant connu des élèves). Le corrigé VIENNE est retiré de la version élève au build. */
const CLS=CLS_MODE,CLS_MAX=30,CLS_V=1;
/* ---------- SHA-256 / HMAC (pur JS : fonctionne en file:// sur Intradef) ---------- */
const SHA_K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
function sha256b(bytes){const l=bytes.length,n=((l+9+63)>>6)<<6,m=new Uint8Array(n);m.set(bytes);m[l]=0x80;const bl=l*8;
 for(let i=0;i<8;i++)m[n-1-i]=Math.floor(bl/Math.pow(2,8*i))&255;
 const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],W=new Array(64),r=(x,k)=>(x>>>k)|(x<<(32-k));
 for(let o=0;o<n;o+=64){for(let t=0;t<16;t++)W[t]=(m[o+4*t]<<24)|(m[o+4*t+1]<<16)|(m[o+4*t+2]<<8)|m[o+4*t+3];
  for(let t=16;t<64;t++){const s0=r(W[t-15],7)^r(W[t-15],18)^(W[t-15]>>>3),s1=r(W[t-2],17)^r(W[t-2],19)^(W[t-2]>>>10);W[t]=(W[t-16]+s0+W[t-7]+s1)|0;}
  let [a,b,c,d,e,f,g,h]=H;
  for(let t=0;t<64;t++){const S1=r(e,6)^r(e,11)^r(e,25),ch=(e&f)^(~e&g),t1=(h+S1+ch+SHA_K[t]+W[t])|0,S0=r(a,2)^r(a,13)^r(a,22),mj=(a&b)^(a&c)^(b&c),t2=(S0+mj)|0;h=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0;}
  H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+c)|0;H[3]=(H[3]+d)|0;H[4]=(H[4]+e)|0;H[5]=(H[5]+f)|0;H[6]=(H[6]+g)|0;H[7]=(H[7]+h)|0;}
 const out=new Uint8Array(32);H.forEach((x,i)=>{out[4*i]=x>>>24;out[4*i+1]=(x>>>16)&255;out[4*i+2]=(x>>>8)&255;out[4*i+3]=x&255;});return out;}
const u8=s=>new TextEncoder().encode(s),hex=b=>[...b].map(x=>x.toString(16).padStart(2,"0")).join("");
function hmac(key,msg){let k=u8(key);if(k.length>64)k=sha256b(k);const K=new Uint8Array(64);K.set(k);
 const ip=K.map(x=>x^0x36),op=K.map(x=>x^0x5c),mb=u8(msg),a=new Uint8Array(64+mb.length);a.set(ip);a.set(mb,64);
 const ih=sha256b(a),b=new Uint8Array(96);b.set(op);b.set(ih,64);return hex(sha256b(b));}
function canon(o){if(Array.isArray(o))return "["+o.map(canon).join(",")+"]";
 if(o&&typeof o==="object")return "{"+Object.keys(o).sort().filter(k=>o[k]!==undefined).map(k=>JSON.stringify(k)+":"+canon(o[k])).join(",")+"}";
 return JSON.stringify(o===undefined?null:o);}
function sign(o,code){const c=Object.assign({},o);delete c.sig;return hmac(codeNorm(code),canon(c));}
function sigOk(o,code){return !!o&&typeof o.sig==="string"&&o.sig===sign(o,code);}
/* ---------- Code du groupe : 5 blocs de 4 caractères, le 1er = identifiant du groupe, le dernier caractère = clé de contrôle ---------- */
const CA="ABCDEFGHJKMNPQRSTUVWXYZ23456789";
function codeNorm(c){return String(c||"").toUpperCase().replace(/[^A-Z0-9]/g,"");}
function codeChk(s){let t=0;for(let i=0;i<s.length;i++)t=(t*7+CA.indexOf(s[i])+1)%CA.length;return CA[t];}
function codeNew(){const r=new Uint32Array(19);crypto.getRandomValues(r);let s=[...r].map(x=>CA[x%CA.length]).join("");s+=codeChk(s);return s.match(/.{4}/g).join("-");}
function codeValid(c){const s=codeNorm(c);return s.length===20&&[...s].every(x=>CA.includes(x))&&codeChk(s.slice(0,19))===s[19];}
function codeFmt(c){return codeNorm(c).match(/.{1,4}/g).join("-");}
function gidOf(c){return codeNorm(c).slice(0,4);}
function idTxt(id){return id?[id.grade,String(id.nom||"").toUpperCase(),id.prenom].filter(Boolean).join(" "):"";}
function fsafe(s){return String(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[^A-Za-z0-9]+/g,"_").replace(/^_|_$/g,"");}
function dtxt(iso){try{return new Date(iso).toLocaleString(LANG==="ar"?"ar":LANG==="fr"?"fr-FR":LANG,{dateStyle:"short",timeStyle:"short"});}catch(e){return iso;}}
function readJsonFile(f){return new Promise(res=>{const r=new FileReader();r.onload=()=>{try{res(JSON.parse(r.result));}catch(e){res(null);}};r.onerror=()=>res(null);r.readAsText(f);});}
function clsMsg(id,h){const e=document.getElementById(id);if(e)e.innerHTML=h;}
const CLS_ST=document.createElement("style");CLS_ST.textContent=`
.cls-id{font-weight:600}.cls-a{color:var(--vert);font-weight:600}.cls-na{color:var(--rouge);font-weight:600}.cls-ne{color:var(--gris)}
.cls-bn{border-left:4px solid var(--rouge);background:var(--rouge-c);padding:10px 14px;border-radius:0 6px 6px 0;margin:10px 0}
.cls-bn.ok{border-color:var(--vert);background:var(--vert-c)}
.cls-grid{display:grid;grid-template-columns:1fr;gap:12px}.cls-grid>div{min-width:0}
.cls-col{border:1px solid var(--argent-c);border-radius:6px;padding:8px 12px;background:#fff}.cls-col h4{margin:4px 0 8px}
.cls-cor{border-color:var(--vert);background:#F6FAF7}.cls-cor summary{cursor:pointer;padding:6px 0}
.cls-ev{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center;margin-top:10px}
.cls-ev label{display:inline-flex;align-items:center;gap:6px;min-height:36px;cursor:pointer}
.cls-drop{border:2px dashed var(--argent);border-radius:8px;padding:18px;text-align:center;margin:10px 0}.cls-drop.on{background:var(--ambre-c);border-color:var(--ambre)}
.cls-code{font-family:Consolas,monospace;font-size:1.3em;letter-spacing:.05em;background:var(--argent-c);padding:6px 10px;border-radius:5px;display:inline-block}
.cls-flag{color:var(--ambre);font-weight:600}.cls-nav-na{color:var(--rouge);font-weight:700;margin-inline-start:4px}
@media (max-width:820px){.cls-grid{grid-template-columns:1fr}}`;document.head.appendChild(CLS_ST);

/* ---------- Extraction des travaux d'un état S (réutilise casData : mêmes règles que « Créer un cas ») ---------- */
function workOf(D){const keep=S;S=Object.assign({quiz:{},v:{},tab:{},tcidr:[],frise:[]},D||{});let r;try{r=casData("","","").corrige;}finally{S=keep;}return r;}
let CORR_VIENNE=null;
function corrVienne(){if(!CORR_VIENNE)CORR_VIENNE=workOf(demoTr(JSON.parse(JSON.stringify(DEMO))));return CORR_VIENNE;}
function workBody(m,c){if(!c)return "";const V=c.v||{},T=c.tab||{};let b="";
 (m.apply||[]).forEach(x=>{
  if(x.t==="fields"&&V[x.id])x.f.forEach(f=>{const v=V[x.id][f.k];if(v!=null&&v!=="")b+=`<p><b>${esc(f.l)}</b><br>${esc(v).replace(/\n/g,"<br>")}</p>`;});
  if(x.t==="tiers"&&V.tiers)b+=`<p><b>${esc("Tiers-temps")}</b><br>${esc([V.tiers.r,V.tiers.c,V.tiers.m].filter(Boolean).join(" · "))}</p>`;
  const tb=blkTab(x);if(tb&&T[tb.id])b+=`${tb.l?`<h4>${esc(tb.l)}</h4>`:""}${roTable(tb.cols,T[tb.id])}`;});
 if(Array.isArray(c.tcidr)&&c.tcidr.length)b+=`<h4>TCIDR</h4>${roTable([{k:"y",l:"Type"},{k:"l",l:"Libellé"},{k:"fo",l:"Fonction opérationnelle"}],c.tcidr)}`;
 if(Array.isArray(c.frise)&&c.frise.length)b+=`<h4>Frise chronologique</h4>${roTable([{k:"g",l:"GDH / repère"},{k:"e",l:"Événement ou tâche"}],c.frise.slice().sort((a,z)=>gdhCmp(a.g,z.g)))}`;
 return b;}
/* Textes longs saisis (pour repérer des travaux identiques entre élèves) */
function longTexts(D){const out=new Set(),add=v=>{const t=String(v||"").toLowerCase().replace(/\s+/g," ").trim();if(t.length>=40)out.add(t);};
 M.forEach(m=>(m.apply||[]).forEach(b=>{if(b.t==="fields")b.f.forEach(f=>add(((D.v||{})[b.id]||{})[f.k]));
  const t=blkTab(b);if(t)((D.tab||{})[t.id]||[]).forEach(r=>t.cols.forEach(c=>{if(!c.ro)add(r[c.k]);}));}));
 (D.tcidr||[]).forEach(r=>add(r.l));(D.frise||[]).forEach(r=>add(r.e));return out;}

/* Journal de saisie (nombre de modifications et de collages par bloc), joint aux envois */
function clsLog(bid,paste){if(CLS!=="eleve"||!S.cls)return;const L=S.cls.log=S.cls.log||{},x=L[bid]=L[bid]||{n:0,p:0,t0:Date.now()};x.n++;if(paste)x.p++;x.t1=Date.now();}
let CLS_PASTE=0;document.addEventListener("paste",e=>{if(e.target.closest&&e.target.closest("#main"))CLS_PASTE=Date.now();},true);
{const sv=setv,sc=setc;
 setv=function(id,k,v){if(CLS==="eleve")clsLog(id,Date.now()-CLS_PASTE<1500);sv(id,k,v);};
 setc=function(t,i,k,v){if(CLS==="eleve")clsLog(t,Date.now()-CLS_PASTE<1500);sc(t,i,k,v);};}
/* Examens blancs : chaque tentative est conservée pour l'envoi */
{const ef=exFinish;exFinish=function(x){const had=EX&&EX.res;ef(x);
 if(CLS==="eleve"&&!had&&EX&&EX.res&&S.cls&&Object.keys(EX.ans).length){(S.cls.ex=S.cls.ex||[]).push({sc:EX.sc||"tout",pct:EX.res.pct,dur:EX.res.dur,exp:!!EX.res.expired,date:new Date().toISOString(),per:EX.res.per});save();}};}
const KINDS={};

/* ======================= VERSION ÉLÈVE ======================= */
const GRADES=["SLT","LTN","CNE","CDT","LCL","COL","ASP","ADJ","ADC","MAJ","SGT","SCH"];
function clsIdForm(){const v=(S.cls&&S.cls.draft)||{};
 return `<h2>MaisDot Classroom – première ouverture</h2>
 <div class="card"><p>Ce fichier est <b>personnel</b>. Renseigne ton identité et le <b>code du groupe</b> donné par ton professeur. Ces informations accompagnent chacun de tes envois ; elles ne pourront plus être modifiées sans effacer tes travaux.</p>
 <div class="fld"><label for="ciG">Grade</label><input id="ciG" list="ciGl" autocomplete="off" value="${esc(v.grade||"")}"><datalist id="ciGl">${GRADES.map(g=>`<option value="${g}">`).join("")}</datalist></div>
 <div class="fld"><label for="ciN">Nom</label><input id="ciN" autocomplete="family-name" value="${esc(v.nom||"")}"></div>
 <div class="fld"><label for="ciP">Prénom</label><input id="ciP" autocomplete="given-name" value="${esc(v.prenom||"")}"></div>
 <div class="fld"><label for="ciM">Numéro matricule</label><input id="ciM" autocomplete="off" inputmode="numeric" value="${esc(v.mat||"")}"></div>
 <div class="fld"><label for="ciC">Code du groupe</label><div class="h">5 blocs de 4 caractères, par exemple ABCD-EFGH-JKLM-NPQR-STUV.</div><input id="ciC" autocomplete="off" value="${esc(v.code||"")}"></div>
 <div class="rowb"><button class="btn" onclick="clsIdCheck()">Valider mon identité</button></div><div id="ciMsg" role="status"></div></div>
 <p class="ref">Tes données restent sur ce poste et dans les fichiers que tu envoies à ton professeur. Rien n’est transmis en ligne.</p>`;}
function clsIdVals(){const g=id=>(document.getElementById(id)||{}).value||"";return {grade:g("ciG").trim(),nom:g("ciN").trim(),prenom:g("ciP").trim(),mat:g("ciM").replace(/\s+/g,"").trim(),code:g("ciC").trim()};}
function clsIdCheck(){const v=clsIdVals();S.cls=Object.assign(S.cls||{},{draft:v});
 const err=[];if(!v.grade)err.push("Grade manquant.");if(!v.nom)err.push("Nom manquant.");if(!v.prenom)err.push("Prénom manquant.");
 if(!/^[A-Za-z0-9-]{4,20}$/.test(v.mat))err.push("Matricule invalide (4 à 20 chiffres ou lettres).");if(!codeValid(v.code))err.push("Code du groupe invalide : vérifie chaque caractère.");
 if(err.length)return clsMsg("ciMsg",err.map(e=>`<p class="warn">${esc(e)}</p>`).join(""));
 openModal(`<h3>Confirmer mon identité</h3><p><b>${esc(idTxt(v))}</b></p><p>Matricule : <b>${esc(v.mat)}</b></p><p>Groupe : <b>${esc(codeFmt(v.code))}</b></p><p>Après confirmation, ces informations ne pourront plus être modifiées sans effacer tes travaux.</p><div class="rowb"><button class="btn" onclick="clsIdSave()">Confirmer</button></div>`);}
function clsIdSave(){const v=clsIdVals().grade?clsIdVals():S.cls.draft;closeModal();
 S.cls={id:{grade:v.grade,nom:v.nom,prenom:v.prenom,mat:v.mat},code:codeFmt(v.code),gid:gidOf(v.code),created:new Date().toISOString(),n:0,sent:[],ex:[],log:{}};save();clsHeader();FOCUS_NEXT="#main h2";go("cls_envoi");}
function clsStats(D){const w=workOf(D),q=Object.values(D.quiz||{});return {etapes:Object.keys(w).length,tests:q.length,valides:q.filter(x=>x.best>=PASS).length,examens:((D.cls||{}).ex||[]).length};}
function envoiPage(){const c=S.cls,s=clsStats(S),last=(c.sent||[]).slice(-1)[0];
 return `<div class="ref">MaisDot Classroom</div><h2>Envoyer mes travaux au professeur</h2>
 <div class="card"><h3>Mon identité</h3><p class="cls-id">${esc(idTxt(c.id))}</p><p>Matricule : <b>${esc(c.id.mat)}</b> · Groupe : <b>${esc(c.code)}</b></p></div>
 <div class="card"><h3>Contenu de l’envoi</h3><ul class="c"><li>Étapes avec des gabarits remplis : <b>${s.etapes}</b></li><li>Tests faits : <b>${s.tests}</b> (validés : <b>${s.valides}</b>)</li><li>Examens blancs passés : <b>${s.examens}</b></li></ul>
 <p>L’envoi contient <b>tout</b> : gabarits, TCIDR, frise, résultats des tests et des examens blancs. Tu peux envoyer autant de fois que nécessaire : ton professeur garde le dernier envoi.</p>
 <div class="rowb"><button class="btn" onclick="clsSend()">Préparer mon envoi (.json)</button></div><div id="ioMsg" role="status"></div>
 <p class="ref">Joins ensuite le fichier téléchargé au message adressé à ton professeur. Ne modifie pas ce fichier : toute modification est détectée.</p>
 ${last?`<p>Dernier envoi : <b>${esc(dtxt(last.date))}</b> (<span>envoi n° ${last.n}</span>)</p>`:"<p>Aucun envoi pour l’instant.</p>"}</div>
 <div class="card"><h3>Recevoir ma correction</h3><p>Ton professeur te renvoie un fichier de correction (.json). Importe-le ici pour voir les points non maîtrisés et les étapes à revoir.</p>
 <div class="rowb"><button class="btn dk" onclick="document.getElementById('fCor').click()">Importer ma correction</button><input type="file" id="fCor" accept=".json,application/json" hidden onchange="clsImportCorr(this)">${c.corr?`<button class="btn s" onclick="go('cls_retour')">Voir ma correction</button>`:""}</div><div id="corMsg" role="status"></div></div>`;}
function clsSend(){const c=S.cls;c.n=(c.n||0)+1;const date=new Date().toISOString();
 const data={quiz:S.quiz,v:S.v,tab:S.tab,tcidr:S.tcidr,frise:S.frise,ex:c.ex||[],log:c.log||{}};
 const o={type:"maisdot-classroom-envoi",ver:CLS_V,gid:c.gid,id:c.id,date,n:c.n,lang:LANG,data};o.sig=sign(o,c.code);
 (c.sent=c.sent||[]).push({date,n:c.n});save();
 dl(`MaisDot_envoi_${fsafe(c.id.nom)}_${fsafe(c.id.mat)}_${date.slice(0,10)}.json`,"application/json",JSON.stringify(o));
 setTimeout(()=>{keep();msg("Envoi prêt : joins le fichier téléchargé au message adressé à ton professeur.");},50);}
async function clsImportCorr(inp){const f=inp.files[0];inp.value="";if(!f)return;const o=await readJsonFile(f),c=S.cls;
 if(!o||o.type!=="maisdot-classroom-correction")return clsMsg("corMsg",`<p class="warn">${esc("Ce fichier n’est pas une correction MaisDot Classroom.")}</p>`);
 if(o.gid!==c.gid||!sigOk(o,c.code))return clsMsg("corMsg",`<p class="warn">${esc("Correction refusée : elle ne vient pas de ton groupe ou le fichier a été modifié.")}</p>`);
 if(o.mat!==c.id.mat)return clsMsg("corMsg",`<p class="warn">${esc("Correction refusée : elle concerne un autre élève.")}</p>`);
 if(c.corr&&c.corr.date>o.date)return clsMsg("corMsg",`<p class="warn">${esc("Cette correction est plus ancienne que celle déjà importée.")}</p>`);
 c.corr={date:o.date,envoi:o.envoi,gen:o.gen||"",items:o.items||{}};save();FOCUS_NEXT="#main h2";go("cls_retour");}
function retourPage(){const c=S.cls.corr;let h=`<div class="ref">MaisDot Classroom</div><h2>Ma correction</h2>`;
 if(!c)return h+`<div class="card"><p>Aucune correction importée. Quand ton professeur t’a renvoyé un fichier de correction, importe-le depuis « Envoyer mes travaux ».</p><div class="rowb"><button class="btn" onclick="go('cls_envoi')">Aller à « Envoyer mes travaux »</button></div></div>`;
 const E=Object.entries(c.items).map(([id,x])=>[M.find(m=>m.id===id),x]).filter(([m])=>m).sort((a,b)=>M.indexOf(a[0])-M.indexOf(b[0]));
 const na=E.filter(([,x])=>x.s==="NA"),a=E.filter(([,x])=>x.s==="A");
 h+=`<div class="card"><p>Correction du <b>${esc(dtxt(c.date))}</b>${c.envoi?` – envoi du <b>${esc(dtxt(c.envoi))}</b>`:""}.</p><p><span class="cls-a">Acquis : ${a.length}</span> · <span class="cls-na">Non acquis : ${na.length}</span></p>${c.gen?`<div class="but"><b>${esc("Appréciation du professeur")}</b><br>${esc(c.gen).replace(/\n/g,"<br>")}</div>`:""}</div>`;
 if(na.length)h+=`<h3>Points non maîtrisés</h3>`+na.map(([m,x])=>`<div class="card"><div class="ref">${esc(m.grp)}</div><h4>${esc(m.title)} <span class="cls-na">– Non acquis</span></h4>${x.c?`<p>${esc(x.c).replace(/\n/g,"<br>")}</p>`:""}<div class="rowb"><button class="btn" onclick="go('${m.id}','c')">Revoir l’étape</button>${m.quiz?`<button class="btn s" onclick="go('${m.id}','e')">Refaire le test</button>`:""}${m.apply?`<button class="btn s" onclick="go('${m.id}','a')">Reprendre mes gabarits</button>`:""}</div></div>`).join("");
 if(a.length)h+=`<h3>Acquis</h3><div class="card"><ul class="c">${a.map(([m,x])=>`<li><a href="#${m.id}" onclick="event.preventDefault();go('${m.id}')">${esc(m.title)}</a>${x.c?` – ${esc(x.c)}`:""}</li>`).join("")}</ul></div>`;
 return h;}
function clsSujet(){const P=String(DEMO_SITU.situation||DEMO_SITU.resume).split(/\n\s*\n/).filter(p=>!/^AVERTISSEMENT/.test(p));
 openModal(`<h3>Sujet VIENNE – 33(AZ)BB</h3><p class="ref">Repère horaire : J = 16 juin, heures en ZOULOU (160501Z = J 05h01).</p>${P.map(p=>`<p>${esc(p).replace(/\n/g,"<br>")}</p>`).join("")}`);}
function clsHeader(){const t=document.querySelector("header .t2");if(!t)return;
 t.textContent=CLS==="eleve"?"MaisDot Classroom · version élève":"MaisDot Classroom · version professeur";
 if(CLS==="eleve"&&S.cls&&S.cls.id){const b=document.createElement("b");b.textContent=" · "+idTxt(S.cls.id);t.appendChild(b);}}
function clsBanner(){if(CLS!=="eleve"||!S.cls||!S.cls.corr)return;const m=M.find(x=>x.id===cur),x=m&&S.cls.corr.items[m.id];if(!x||!m.title)return;
 const h=document.querySelector("#main h2");if(!h)return;const d=document.createElement("div");d.className="cls-bn"+(x.s==="A"?" ok":"");
 d.innerHTML=`<b>${esc(x.s==="A"?"Correction du professeur : acquis":"Correction du professeur : non acquis")}</b>${x.c?`<br>${esc(x.c).replace(/\n/g,"<br>")}`:""}`;h.after(d);}
function clsNavMarks(){const it=CLS==="eleve"&&S.cls&&S.cls.corr&&S.cls.corr.items;if(!it)return;
 document.querySelectorAll("#navList a[data-id]").forEach(a=>{const x=it[a.dataset.id];if(x&&x.s==="NA"&&!a.querySelector(".cls-nav-na")){const s=document.createElement("span");s.className="cls-nav-na";s.title="Non acquis";s.setAttribute("aria-label","Non acquis");s.textContent="✗";a.appendChild(s);}});}

/* ======================= VERSION PROFESSEUR ======================= */
let PR={grp:null,st:{}},SEL=null,SHOWALL=false;
const PDB_NAME="maisdot-classroom-prof",PDB_K="db";
let PDB=null;
function pdbOpen(){if(PDB)return Promise.resolve(PDB);return new Promise((res,rej)=>{try{const r=indexedDB.open(PDB_NAME,1);r.onupgradeneeded=()=>r.result.createObjectStore("kv");r.onsuccess=()=>{PDB=r.result;res(PDB);};r.onerror=()=>rej(r.error);}catch(e){rej(e);}});}
async function prLoad(){try{const db=await pdbOpen();const v=await new Promise((res,rej)=>{const q=db.transaction("kv").objectStore("kv").get(PDB_K);q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error);});if(v&&v.st)PR=v;}
 catch(e){try{const v=JSON.parse(localStorage.getItem(PDB_NAME)||"null");if(v&&v.st)PR=v;}catch(x){}}}
/* Enregistrement immédiat à chaque modification (IndexedDB ; à défaut localStorage) */
let PR_Q=Promise.resolve();
function prSave(){const snap=JSON.stringify(PR);PR_Q=PR_Q.then(async()=>{try{const db=await pdbOpen();await new Promise((res,rej)=>{const tx=db.transaction("kv","readwrite");tx.objectStore("kv").put(JSON.parse(snap),PDB_K);tx.oncomplete=res;tx.onerror=()=>rej(tx.error);tx.onabort=()=>rej(tx.error);});}
 catch(e){try{localStorage.setItem(PDB_NAME,snap);}catch(x){}}});return PR_Q;}
/* Saisie des commentaires : enregistrement groupé (0,4 s), forcé si la page est masquée ou fermée */
let PR_T=null;function prSaveSoon(){clearTimeout(PR_T);PR_T=setTimeout(()=>{PR_T=null;prSave();},400);}
addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden"&&PR_T){clearTimeout(PR_T);PR_T=null;prSave();}});
addEventListener("pagehide",()=>{if(PR_T){clearTimeout(PR_T);PR_T=null;prSave();}});
function prList(){return Object.values(PR.st).sort((a,b)=>String(a.id.nom).localeCompare(String(b.id.nom),"fr")||String(a.id.prenom).localeCompare(String(b.id.prenom),"fr"));}
function prStatus(s){if(!s.env)return ["Aucun envoi","cls-ne"];const c=s.corr||{},n=Object.keys(c.items||{}).length;
 if(c.exp&&(!c.mod||c.exp>=c.mod)&&c.exp>=s.env.recv)return ["Correction renvoyée","cls-a"];
 if(c.exp&&s.env.recv>c.exp)return ["Nouvel envoi à corriger","cls-na"];
 return n?["Correction en cours","cls-flag"]:["À corriger","cls-na"];}
function prSim(){const L=prList().filter(s=>s.env),T=L.map(s=>longTexts(s.env.data)),out=[];
 for(let i=0;i<L.length;i++)for(let j=i+1;j<L.length;j++){let n=0,lg=0;T[i].forEach(t=>{if(T[j].has(t)){n++;if(t.length>=100)lg++;}});const mn=Math.min(T[i].size,T[j].size);
  if(lg||n>=3||(n>=2&&mn&&n/mn>=0.5))out.push([L[i],L[j],n]);}
 return out;}
function groupePage(){let h=`<div class="ref">MaisDot Classroom</div><h2>Mon groupe</h2>`;
 if(!PR.grp)return h+`<div class="card"><h3>Créer le groupe</h3><p>Le groupe compte ${CLS_MAX} élèves au plus. Un <b>code du groupe</b> est créé : chaque élève le saisit à la première ouverture de sa version élève. Il sert à vérifier que les envois viennent bien de ton groupe et n’ont pas été modifiés.</p>
 <div class="fld"><label for="gN">Nom du groupe</label><input id="gN" placeholder="Par exemple : ESORSEM 2026-2027, groupe 3" autocomplete="off"></div>
 <div class="rowb"><button class="btn" onclick="prCreate()">Créer le groupe</button><button class="btn s" onclick="document.getElementById('fGrp').click()">Reprendre une sauvegarde du groupe</button><input type="file" id="fGrp" accept=".json" hidden onchange="prRestore(this)"></div><div id="gMsg" role="status"></div></div>`;
 const L=prList(),sim=prSim();
 h+=`<div class="card"><h3>${esc(PR.grp.name)}</h3><p>Code du groupe à donner aux élèves : <span class="cls-code">${esc(PR.grp.code)}</span> <button class="btn s" onclick="prCopyCode()">Copier le code</button></p><p>Élèves : <b>${L.length}</b> / ${CLS_MAX}</p>
 <p class="ref">Ne diffuse ce code qu’à ton groupe. Sauvegarde régulièrement le groupe : les données restent dans ce navigateur.</p>
 <div class="rowb"><button class="btn s" onclick="prBackup()">Sauvegarder le groupe (.json)</button><button class="btn s" onclick="document.getElementById('fGrp').click()">Reprendre une sauvegarde du groupe</button><input type="file" id="fGrp" accept=".json" hidden onchange="prRestore(this)"><button class="btn s" onclick="prCsv()">Exporter le tableau (Excel, .csv)</button><button class="btn danger" onclick="prReset()">Supprimer le groupe</button></div><div id="gMsg" role="status"></div></div>`;
 h+=`<div class="card"><h3>Recevoir des envois</h3><div class="cls-drop" id="clsDrop"><p>Dépose ici les fichiers .json reçus des élèves (plusieurs à la fois), ou</p><button class="btn" onclick="document.getElementById('fEnv').click()">Choisir les fichiers</button><input type="file" id="fEnv" accept=".json,application/json" multiple hidden onchange="prImport(this.files);this.value=''"></div><div id="envMsg" role="status" aria-live="polite"></div></div>`;
 if(sim.length)h+=`<div class="card"><h3>⚠ Travaux très proches</h3><p>Ces élèves ont rendu des textes longs identiques. À vérifier avec eux.</p><ul class="c">${sim.map(([a,b,n])=>`<li><b>${esc(idTxt(a.id))}</b> ↔ <b>${esc(idTxt(b.id))}</b> : ${n} textes identiques</li>`).join("")}</ul></div>`;
 h+=`<div class="card"><h3>Tableau du groupe</h3>${L.length?`<div class="tw"><table><thead><tr><th>Élève</th><th>Matricule</th><th>Dernier envoi</th><th>Étapes remplies</th><th>Tests validés</th><th>Meilleur examen</th><th>Contrôle</th><th>Correction</th><th></th></tr></thead><tbody>${L.map(s=>{const e=s.env,ss=e?clsStats(Object.assign({cls:{ex:e.data.ex}},e.data)):null,ex=e?(e.data.ex||[]).reduce((m,x)=>Math.max(m,x.pct),-1):-1,[stx,stc]=prStatus(s);
  return `<tr><td data-l="Élève"><b>${esc(idTxt(s.id))}</b></td><td data-l="Matricule">${esc(s.id.mat)}</td><td data-l="Dernier envoi">${e?esc(dtxt(e.date)):"–"}</td><td data-l="Étapes remplies">${ss?ss.etapes:"–"}</td><td data-l="Tests validés">${ss?ss.valides+" / "+ss.tests:"–"}</td><td data-l="Meilleur examen">${ex>=0?ex+" %":"–"}</td><td data-l="Contrôle">${(s.flags||[]).length?`<span class="cls-flag" title="${esc(s.flags.join(" "))}"><span aria-hidden="true">⚠</span> ${esc(s.flags[0])}</span>`:'<span class="cls-a">✓</span>'}</td><td data-l="Correction"><span class="${stc}">${esc(stx)}</span></td><td>${e?`<button class="btn s" onclick="prOpen('${esc(s.id.mat)}')">Corriger</button>`:""}</td></tr>`;}).join("")}</tbody></table></div>`:"<p>Aucun élève pour l’instant : les élèves apparaissent à la réception de leur premier envoi.</p>"}</div>`;
 return h;}
function prCreate(){const n=((document.getElementById("gN")||{}).value||"").trim();if(!n)return clsMsg("gMsg",`<p class="warn">${esc("Donne un nom au groupe.")}</p>`);
 const code=codeNew();PR={grp:{name:n,code,gid:gidOf(code),created:new Date().toISOString()},st:{}};prSave();keep();}
async function prCopyCode(){try{await navigator.clipboard.writeText(PR.grp.code);clsMsg("gMsg",`<p class="ok-msg">${esc("Code copié.")}</p>`);}catch(e){openModal(`<h3>Code du groupe</h3><p class="cls-code">${esc(PR.grp.code)}</p>`);}}
function prBackup(){dl(`MaisDot_groupe_${fsafe(PR.grp.name)}_${new Date().toISOString().slice(0,10)}.json`,"application/json",JSON.stringify({type:"maisdot-classroom-groupe",ver:CLS_V,pr:PR}));
 setTimeout(()=>clsMsg("gMsg",`<p class="ok-msg">${esc("Sauvegarde du groupe générée. Elle contient le code du groupe : garde-la pour toi.")}</p>`),50);}
async function prRestore(inp){const f=inp.files[0];inp.value="";if(!f)return;const o=await readJsonFile(f);
 if(!o||o.type!=="maisdot-classroom-groupe"||!o.pr||!o.pr.grp||!o.pr.st)return clsMsg("gMsg",`<p class="warn">${esc("Fichier non reconnu : ce n’est pas une sauvegarde de groupe MaisDot Classroom.")}</p>`);
 const go2=()=>{PR=o.pr;prSave();closeModal();keep();};
 if(PR.grp&&PR.grp.gid!==o.pr.grp.gid){window.__prR=go2;openModal(`<h3>Remplacer le groupe actuel ?</h3><p>Le groupe « <b>${esc(PR.grp.name)}</b> » sera remplacé par « <b>${esc(o.pr.grp.name)}</b> ».</p><div class="rowb"><button class="btn" onclick="__prR()">Remplacer</button></div>`);}else go2();}
function prReset(){openModal(`<h3>Supprimer le groupe ?</h3><p>Le groupe, les envois reçus et les corrections seront supprimés de ce navigateur. Sauvegarde d’abord le groupe si tu veux le garder.</p><div class="rowb"><button class="btn" onclick="PR={grp:null,st:{}};prSave();SEL=null;closeModal();keep()">Oui, supprimer</button></div>`);}
async function prImport(files){const out=[];if(!PR.grp)return;
 for(const f of [...files]){const o=await readJsonFile(f),nm=`<b>${esc(f.name)}</b> : `;
  if(!o||o.type!=="maisdot-classroom-envoi"||!o.id||!o.data){out.push(`<p class="warn">${nm}${esc("fichier non reconnu (ce n’est pas un envoi MaisDot Classroom).")}</p>`);continue;}
  if(o.gid!==PR.grp.gid){out.push(`<p class="warn">${nm}${esc("refusé : envoi destiné à un autre groupe.")}</p>`);continue;}
  const mat=String(o.id.mat||""),s0=PR.st[mat];
  if(!/^[A-Za-z0-9-]{4,20}$/.test(mat)){out.push(`<p class="warn">${nm}${esc("refusé : matricule invalide.")}</p>`);continue;}
  if(!s0&&Object.keys(PR.st).length>=CLS_MAX){out.push(`<p class="warn">${nm}${esc("refusé : le groupe compte déjà 30 élèves.")}</p>`);continue;}
  if(s0&&s0.env&&s0.env.date>=o.date){out.push(`<p class="warn">${nm}${esc("ignoré : envoi plus ancien ou identique au dernier reçu.")}</p>`);continue;}
  const flags=[];if(!sigOk(o,PR.grp.code))flags.push("Signature invalide : fichier modifié après l’envoi.");
  if(s0&&idTxt(s0.id)!==idTxt(o.id))flags.push("Identité différente pour ce matricule.");
  if(s0&&s0.env&&o.n<=s0.env.n)flags.push("Numéro d’envoi incohérent.");
  const s=PR.st[mat]=s0||{id:o.id,corr:{items:{},gen:""},hist:[]};s.id=s0?s.id:o.id;
  s.env={date:o.date,n:o.n,lang:o.lang,data:o.data,recv:new Date().toISOString()};s.hist.push({date:o.date,n:o.n});s.flags=flags;
  out.push(`<p class="${flags.length?"warn":"ok-msg"}">${nm}${esc(idTxt(o.id))} – ${esc(flags.length?flags.join(" "):"envoi reçu, contrôle correct.")}</p>`);}
 prSave();keep();clsMsg("envMsg",out.join(""));}
function prOpen(mat){SEL=mat;SHOWALL=false;FOCUS_NEXT="#main h2";go("cls_corr");}
/* Suggestion automatique d'après les tests et les examens blancs */
function prSuggest(s,m){const d=s.env.data,q=(d.quiz||{})[m.id];let ok=0,n=0;(d.ex||[]).forEach(x=>{const p=x.per&&x.per[m.id];if(p){ok+=p.ok;n+=p.n;}});
 const r=[];if(q)r.push([q.best>=PASS?"A":"NA",`test ${Math.round(q.best*100)} %`]);if(n>=2)r.push([ok/n>=0.5?"A":"NA",`examens ${ok} / ${n}`]);
 if(!r.length)return null;return {s:r.some(x=>x[0]==="NA")?"NA":"A",why:r.map(x=>x[1]).join(" ; ")};}
function corrPage(){const s=PR.st[SEL];let h=`<div class="ref">MaisDot Classroom</div><h2>Correction</h2>`;
 if(!PR.grp)return h+`<div class="card"><p>Crée d’abord le groupe.</p><div class="rowb"><button class="btn" onclick="go('cls_groupe')">Mon groupe</button></div></div>`;
 const L=prList().filter(x=>x.env);
 h+=`<div class="card"><div class="fld"><label for="selE">Élève</label><select id="selE" onchange="SEL=this.value;keep()"><option value="">–</option>${L.map(x=>`<option value="${esc(x.id.mat)}" ${x.id.mat===SEL?"selected":""}>${esc(idTxt(x.id))} (${esc(x.id.mat)})</option>`).join("")}</select></div></div>`;
 if(!s||!s.env)return h+(L.length?"<p>Choisis un élève.</p>":"<p>Aucun envoi reçu pour l’instant.</p>");
 const d=s.env.data,W=workOf(d),CV=corrVienne(),c=s.corr,ex=d.ex||[];
 h+=`<div class="card"><h3>${esc(idTxt(s.id))}</h3><p>Matricule : <b>${esc(s.id.mat)}</b> · Envoi n° ${s.env.n} du <b>${esc(dtxt(s.env.date))}</b></p>${(s.flags||[]).length?s.flags.map(f=>`<p class="cls-flag"><span aria-hidden="true">⚠</span> ${esc(f)}</p>`).join(""):`<p class="cls-a">✓ Contrôle correct (signature valide).</p>`}
 ${ex.length?`<h4>Examens blancs</h4><ul class="c">${ex.map(x=>`<li>${esc(dtxt(x.date))} – ${esc(EX_LBL[x.sc]||x.sc)} : <b>${x.pct} %</b>${x.exp?` <span class="ref">(${esc("temps écoulé")})</span>`:""}</li>`).join("")}</ul>`:""}
 <div class="fld"><label for="cGen">Appréciation générale</label><textarea id="cGen" rows="3" oninput="prSetGen(this.value)">${esc(c.gen||"")}</textarea></div>
 <div class="rowb"><button class="btn dk" onclick="prApplySug()">Appliquer les suggestions (tests et examens)</button><button class="btn s" onclick="SHOWALL=!SHOWALL;keep()">${SHOWALL?"Afficher seulement les étapes travaillées":"Afficher toutes les étapes"}</button></div></div>`;
 const mods=M.filter(m=>m.title&&!/^cls_/.test(m.id)&&m.kind!=="home"&&(SHOWALL?(m.apply||m.quiz):(W[m.id]||(d.quiz||{})[m.id]||c.items[m.id]||ex.some(x=>x.per&&x.per[m.id]))));
 if(!mods.length)h+=`<p>Cet élève n’a encore rien rempli.</p>`;
 mods.forEach(m=>{const it=c.items[m.id]||{},sg=prSuggest(s,m),q=(d.quiz||{})[m.id],lg=(d.log||{});
  const nlog=(m.apply||[]).reduce((a,b)=>{const t=blkTab(b),k=b.t==="fields"?b.id:t?t.id:null,x=k&&lg[k];if(x){a.n+=x.n;a.p+=x.p;}return a;},{n:0,p:0});
  h+=`<div class="card" id="cm_${m.id}"><div class="ref">${esc(m.grp)}</div><h3>${esc(m.title)}</h3>
  <p>${q?`Test : <b>${Math.round(q.best*100)} %</b> ${q.best>=PASS?'<span class="cls-a">(validé)</span>':'<span class="cls-na">(non validé)</span>'}`:`<span class="cls-ne">${esc("Test non fait")}</span>`}${nlog.n?` · <span class="ref">${esc("Saisies")} : ${nlog.n} · ${esc("collages")} : ${nlog.p}</span>`:""}${sg?` · ${esc("Suggestion")} : <span class="${sg.s==="A"?"cls-a":"cls-na"}">${esc(sg.s==="A"?"acquis":"non acquis")}</span> <span class="ref">(<span>${esc(sg.why)}</span>)</span>`:""}</p>
  ${m.apply?`<div class="cls-grid"><div class="cls-col"><h4>${esc("Travail de l’élève")}</h4>${workBody(m,W[m.id])||`<p class="cls-ne">${esc("Rien de rempli.")}</p>`}</div><details class="cls-col cls-cor"><summary><b>${esc("Corrigé VIENNE")}</b> <span class="ref">(afficher / masquer)</span></summary>${workBody(m,CV[m.id])||`<p class="cls-ne">${esc("Pas de corrigé VIENNE pour cette étape.")}</p>`}</details></div>`:""}
  <fieldset class="cls-ev"><legend class="sr">${esc("Évaluation")}</legend>${[["A","Acquis"],["NA","Non acquis"],["","Non évalué"]].map(([v,l])=>`<label><input type="radio" name="ev_${m.id}" value="${v}" ${(it.s||"")===v?"checked":""} onchange="prSetItem('${m.id}','s',this.value)"> ${esc(l)}</label>`).join("")}</fieldset>
  <div class="fld"><label for="cc_${m.id}">Explication pour l’élève (points non maîtrisés)</label><textarea id="cc_${m.id}" rows="2" oninput="prSetItem('${m.id}','c',this.value)">${esc(it.c||"")}</textarea></div></div>`;});
 const n=Object.values(c.items).filter(x=>x.s).length;
 h+=`<div class="card"><h3>Renvoyer la correction</h3><p>Étapes évaluées : <b>${n}</b>${c.exp?` · ${esc("Dernier export")} : <b>${esc(dtxt(c.exp))}</b>`:""}</p><div class="rowb"><button class="btn" onclick="prExport()">Exporter la correction (.json)</button></div><div id="ioMsg" role="status"></div><p class="ref">Joins le fichier au message de réponse à l’élève : il l’importe dans sa version élève (« Envoyer mes travaux » → « Importer ma correction »).</p></div>`;
 return h;}
function prSetGen(v){const s=PR.st[SEL];s.corr.gen=v;s.corr.mod=new Date().toISOString();prSaveSoon();}
function prSetItem(id,k,v){const s=PR.st[SEL],it=s.corr.items[id]=s.corr.items[id]||{};it[k]=v;if(!it.s&&!it.c)delete s.corr.items[id];s.corr.mod=new Date().toISOString();k==="c"?prSaveSoon():prSave();}
function prApplySug(){const s=PR.st[SEL];let n=0;M.forEach(m=>{const sg=prSuggest(s,m),it=s.corr.items[m.id];if(sg&&!(it&&it.s)){(s.corr.items[m.id]=it||{}).s=sg.s;n++;}});
 s.corr.mod=new Date().toISOString();prSave();keep();msg(`Suggestions appliquées : ${n}.`);}
function prExport(){const s=PR.st[SEL],items={};Object.entries(s.corr.items).forEach(([k,x])=>{if(x.s)items[k]={s:x.s,c:x.c||""};});
 const o={type:"maisdot-classroom-correction",ver:CLS_V,gid:PR.grp.gid,mat:s.id.mat,date:new Date().toISOString(),envoi:s.env.date,gen:s.corr.gen||"",items};o.sig=sign(o,PR.grp.code);
 clearTimeout(PR_T);PR_T=null;s.corr.exp=o.date;s.corr.mod=o.date;prSave();
 dl(`MaisDot_correction_${fsafe(s.id.nom)}_${fsafe(s.id.mat)}.json`,"application/json",JSON.stringify(o));setTimeout(()=>{keep();msg("Correction exportée : joins le fichier au message de réponse à l’élève.");},50);}
function synthPage(){let h=`<div class="ref">MaisDot Classroom</div><h2>Synthèse du groupe</h2>`;const L=prList().filter(s=>Object.values(s.corr.items).some(x=>x.s));
 if(!L.length)return h+`<div class="card"><p>Aucune correction pour l’instant : la synthèse se remplit au fil des corrections.</p></div>`;
 const R=M.filter(m=>m.title).map(m=>{const v=L.map(s=>s.corr.items[m.id]).filter(x=>x&&x.s);return {m,a:v.filter(x=>x.s==="A").length,na:v.filter(x=>x.s==="NA").length,who:L.filter(s=>(s.corr.items[m.id]||{}).s==="NA")};}).filter(r=>r.a+r.na).sort((x,y)=>y.na-x.na||M.indexOf(x.m)-M.indexOf(y.m));
 h+=`<div class="card"><p>Élèves corrigés : <b>${L.length}</b>. Les étapes les moins maîtrisées sont en tête : ce sont les points à reprendre en séance.</p><div class="rowb"><button class="btn s" onclick="prSynthWord()">Exporter la synthèse (Word)</button></div><div id="ioMsg" role="status"></div></div>`;
 h+=`<div class="card"><div class="tw"><table><thead><tr><th>Étape</th><th>Acquis</th><th>Non acquis</th><th>Élèves en difficulté</th></tr></thead><tbody>${R.map(r=>`<tr><td data-l="Étape"><b>${esc(r.m.title)}</b><br><span class="ref">${esc(r.m.grp)}</span></td><td data-l="Acquis" class="cls-a">${r.a}</td><td data-l="Non acquis" class="cls-na">${r.na}</td><td data-l="Élèves en difficulté">${r.who.map(s=>esc(idTxt(s.id))).join("<br>")||"–"}</td></tr>`).join("")}</tbody></table></div></div>`;
 return h;}
function prSynthWord(){const el=document.createElement("div");el.innerHTML=synthPage();el.querySelectorAll(".rowb,#ioMsg").forEach(x=>x.remove());
 dl(`MaisDot_synthese_${fsafe(PR.grp.name)}.doc`,"application/msword",`<html><head><meta charset="utf-8"><style>body{font-family:Calibri,Arial;font-size:11pt}h2{color:#7E0C16}th{background:#1E2227;color:#fff}td,th{border:1px solid #999;padding:4px}table{border-collapse:collapse}</style></head><body><h1>${esc(PR.grp.name)}</h1>${el.innerHTML}</body></html>`);}
function prCsv(){const q=v=>`"${String(v==null?"":v).replace(/"/g,'""')}"`,hd=["Grade","Nom","Prénom","Matricule","Dernier envoi","Étapes remplies","Tests validés","Tests faits","Meilleur examen (%)","Acquis","Non acquis","Contrôle","Correction"].map(x=>tr(x));
 const rows=prList().map(s=>{const e=s.env,ss=e?clsStats(Object.assign({cls:{ex:e.data.ex}},e.data)):{},it=Object.values(s.corr.items);
  return [s.id.grade,s.id.nom,s.id.prenom,s.id.mat,e?dtxt(e.date):"",ss.etapes??"",ss.valides??"",ss.tests??"",e&&(e.data.ex||[]).length?Math.max(...e.data.ex.map(x=>x.pct)):"",it.filter(x=>x.s==="A").length,it.filter(x=>x.s==="NA").length,tr((s.flags||[]).join(" ")||"OK"),tr(prStatus(s)[0])];});
 dl(`MaisDot_groupe_${fsafe(PR.grp.name)}.csv`,"text/csv;charset=utf-8","﻿"+[hd,...rows].map(r=>r.map(q).join(";")).join("\r\n"));}

/* ======================= BRANCHEMENTS ======================= */
const CLS_MODS=CLS==="eleve"?[{id:"cls_envoi",grp:"MaisDot Classroom",title:"Envoyer mes travaux",kind:"cls_envoi"},{id:"cls_retour",grp:"MaisDot Classroom",title:"Ma correction",kind:"cls_retour"}]
 :[{id:"cls_groupe",grp:"MaisDot Classroom",title:"Mon groupe",kind:"cls_groupe"},{id:"cls_corr",grp:"MaisDot Classroom",title:"Correction d’un élève",kind:"cls_corr"},{id:"cls_synth",grp:"MaisDot Classroom",title:"Synthèse du groupe",kind:"cls_synth"}];
{let i=M.findIndex((m,k)=>k>0&&m.grp!=="Démarrer");M.splice(i<0?1:i,0,...CLS_MODS);NAV_OPEN.add("MaisDot Classroom");}
Object.assign(KINDS,CLS==="eleve"?{cls_envoi:envoiPage,cls_retour:retourPage}:{cls_groupe:groupePage,cls_corr:corrPage,cls_synth:synthPage});
if(CLS==="eleve"){
 /* Fichier personnel : tant que l'identité n'est pas fixée, seule la page d'identité s'affiche */
 var CLS_GATE=function(){return S.cls&&S.cls.id?null:clsIdForm();};
 /* Pas de corrigé ni de chargement de cas dans la version élève */
 corrige=function(){return "";};importCas=function(){};CAS=null;
 {const hm=home;home=function(){let h=hm();
  h=h.replace(/<div class="card"><h3>Cas concret \(instructeur\)<\/h3>[\s\S]*?<div id="casMsg" role="status"><\/div><\/div>/,"");
  h=h.replace(/Pour voir un exemple sur le thème VIENNE[^<]*<b>« Exemple VIENNE »<\/b>[^<]*<\/li>/,"Le sujet d’exercice VIENNE est accessible par le bouton <b>« Sujet VIENNE »</b> en haut de l’écran. Quand tu as avancé, envoie tes travaux à ton professeur (rubrique « MaisDot Classroom »).</li>");
  return h;};}
 /* Sauvegarde personnelle signée : reprise seulement sur le même matricule et le même groupe */
 exportJson=function(){const c=S.cls;if(!c||!c.id)return;const o={type:"maisdot-classroom-sauvegarde",ver:CLS_V,gid:c.gid,mat:c.id.mat,date:new Date().toISOString(),s:S};o.sig=sign(o,c.code);
  dl(`MaisDot_sauvegarde_${fsafe(c.id.nom)}_${fsafe(c.id.mat)}.json`,"application/json",JSON.stringify(o));};
 importJson=async function(inp){const f=inp.files[0];inp.value="";if(!f)return;const o=await readJsonFile(f),c=S.cls;
  if(!o||o.type!=="maisdot-classroom-sauvegarde"||!o.s)return msg("Fichier non reconnu : seule une sauvegarde de ta version élève peut être reprise.");
  if(o.gid!==c.gid||o.mat!==c.id.mat||!sigOk(o,c.code))return msg("Sauvegarde refusée : elle appartient à un autre élève ou a été modifiée.");
  S=Object.assign({quiz:{},v:{},tab:{},tcidr:[],frise:[]},o.s);S.cls=Object.assign({},o.s.cls,{id:c.id,code:c.code,gid:c.gid,sent:(c.sent||[]).length>((o.s.cls||{}).sent||[]).length?c.sent:o.s.cls.sent,n:Math.max(c.n||0,(o.s.cls||{}).n||0)});
  USER=S;save();render();msg("Sauvegarde reprise.");};
 resetAll=function(){openModal(`<h3>Tout effacer ?</h3><p>Tes saisies, tes scores et ta correction seront supprimés de ce navigateur. Ton identité est conservée.</p><div class="rowb"><button class="btn" onclick="S={quiz:{},v:{},tab:{},tcidr:[],frise:[],unlock:false,cls:Object.assign({},S.cls,{ex:[],log:{},corr:null})};USER=S;save();closeModal();go('accueil')">Oui, tout effacer</button></div>`);};
}
function clsInit(){clsHeader();
 const sw=document.querySelector("header .demo-sw");
 if(CLS==="eleve"&&sw){const b=document.createElement("button");b.type="button";b.className="btn s";b.textContent="Sujet VIENNE";b.onclick=clsSujet;sw.replaceWith(b);}
 {const rn=renderNav;renderNav=function(){rn();clsNavMarks();};}
 {const r=render;render=function(){r();clsBanner();};}
 if(CLS==="prof"){prLoad().then(()=>render());
  document.addEventListener("dragover",e=>{const z=e.target.closest&&e.target.closest("#clsDrop");if(z){e.preventDefault();z.classList.add("on");}});
  document.addEventListener("dragleave",e=>{const z=e.target.closest&&e.target.closest("#clsDrop");if(z)z.classList.remove("on");});
  document.addEventListener("drop",e=>{const z=e.target.closest&&e.target.closest("#clsDrop");if(z){e.preventDefault();z.classList.remove("on");prImport(e.dataTransfer.files);}});}}
