# Audit v2 – forme, ergonomie, accessibilité (WCAG 2.2 AA)

**Objet** : `index.html` (build du 16/11/2026, 18 h 00, 228 041 octets), sources `src/app.html` et `src/p2.js`.
**Méthode** : Playwright 1.63 et Chromium 153, avec deux profils : smartphone 390 × 844 (`is_mobile`, `has_touch`, DPR 2) et PC 1366 × 768. axe-core 4.14.1 a été injecté localement (règles wcag2a/aa, 21a/aa, 22aa, best-practice). Des scripts maison ont mesuré les débordements, les cibles tactiles, le contraste réel (fond composé), le parcours au clavier, la conservation du focus et le temps de rendu. L'« Exemple fictif » (`#demoSw`) était activé sur tous les écrans de travail.
**Parcours** : accueil, recherche (« effet »), phase 1 étape 3 (les 3 onglets), onglet Appliquer de p2e1 à p2e6, réunion de décision et plan de manœuvre, TCIDR/frise, examen blanc (en cours puis résultat), fiche réflexe, chargement de `docs/exemple_cas_valdor.json` (bandeau, situation, corrigé p1e5), et enfin démo et cas en même temps.
**Captures** : `/tmp/a3_m_*.png` (mobile) et `/tmp/a3_d_*.png` (PC), soit 49 fichiers.

> Le bandeau « cas » vide s'affichait (bande bleue sous l'en-tête) car `[hidden]` était écrasé par `display:flex`. Ce défaut a été **corrigé pendant l'audit** (`.cas-banner[hidden]{display:none!important}`, build de 18 h 07). Il n'est pas compté ci-dessous.

## Synthèse

| Priorité | Nombre | Nature |
|---|---|---|
| **P1 – bloquant** | **5** | focus clavier perdu, modale, tiroir mobile, tableaux larges illisibles sur PC, schéma du cycle |
| **P2 – important** | **9** | champs tronqués, pages mobiles très longues, Gantt mobile, contraste, ARIA, couleurs sémantiques, cibles tactiles, zoom iOS, bandeaux |
| **P3 – finition** | **10** | cohérence de la charte, légendes, états, libellés |

**Ce qui est conforme** : aucun débordement horizontal, ni à 390 px ni à 1366 px, sur les 18 vues mesurées (`scrollWidth = innerWidth` partout). Aucune erreur console. Tous les champs ont un nom accessible (axe : 0 `label`). L'anneau de focus fait 3 px en rouge sur les liens et les boutons. Le lien d'évitement est présent. `lang="fr"` est déclaré. Les cibles tactiles sont à 44 px sous `pointer:coarse` (tables, onglets, quiz, menu). Le contraste des textes courants et des pastilles vert, ambre et rouge est au-dessus de 4,5:1. Le repli hors ligne (stockage, presse-papiers, téléchargement, impression) passe par `try/catch`, ce qui convient à l'iframe sandbox.

**Performance (sans problème)** : fichier de 228 Ko, aucun appel réseau, DOMContentLoaded en 38 à 41 ms. Le rendu le plus long, `go()`, prend 17 ms (`dec`, PC), et p2e6 rend 1 243 nœuds en 9 ms. Une frappe dans un tableau (`setc` puis `refreshCharts`) coûte de 0,2 à 0,3 ms. Le problème des pages longues est donc **ergonomique, pas technique** :

| Vue (démo) | Hauteur PC | Hauteur mobile |
|---|---|---|
| p2e6 Appliquer | 6 598 px | **22 070 px** (≈ 26 écrans) |
| p2e2 Appliquer | 5 363 | **16 795** |
| p2e1 Appliquer | 4 402 | **12 701** |
| examen en cours | 7 827 | 11 044 |
| pm Appliquer | 2 840 | 8 784 |

---

## P1 – Bloquant

### P1-1 Le focus clavier est perdu à chaque re-rendu (WCAG 2.4.3, 2.1.1)
**Constat.** `render()` remplace tout le `innerHTML` de `<main>`. Le test (Entrée ou Espace au clavier, mobile et PC) donne `document.activeElement = BODY` après chacune de ces actions : réponse au quiz, changement d'onglet, « + Ajouter une ligne », case du canevas, « Voir le corrigé » et suppression de ligne. L'utilisateur au clavier ou au lecteur d'écran repart du haut de la page à chaque action. De plus, après une navigation par le menu (mobile surtout), le focus reste sur un lien du tiroir désormais caché.

**Correctif (JS, à placer juste avant `/* ============ INIT ============ */`)** :
```js
/* audit v2 – conserver ou déplacer le focus à travers les re-rendus */
let FOCUS_NEXT=null;
function focusKey(el){const m=document.getElementById("main");if(!el||el===m||!m.contains(el))return null;
 if(el.id)return "#"+CSS.escape(el.id);
 for(const a of ["aria-label","onclick","onchange"]){const v=el.getAttribute(a);if(v)return `${el.tagName}[${a}="${CSS.escape(v)}"]`;}
 return null;}
const _render=render;
render=function(){const k=focusKey(document.activeElement);_render();
 autoH(document.querySelectorAll("#main textarea"));            /* P2-1 */
 applyToc();                                                      /* P2-2 */
 let e=k&&document.querySelector(k);if(e&&e.disabled)e=null;
 if(!e&&FOCUS_NEXT){e=document.querySelector(FOCUS_NEXT);if(e&&!e.matches("a,button,input,select,textarea,summary,[tabindex]"))e.tabIndex=-1;}
 FOCUS_NEXT=null;if(e)e.focus({preventScroll:true});};
```
Points d'appel à ajuster :
```js
// tryGo (accueil, « Étape suivante ») : focus sur le titre de la page cible
function tryGo(id){const m=M.find(x=>x.id===id);if(unlocked(m)){FOCUS_NEXT="#main h2";go(id);}else flash(m);}
// clic dans le menu (listener #nav, juste avant go(m.id)) :
FOCUS_NEXT="#main h2";
// answer() : le bouton cliqué devient disabled -> focus sur la correction
//   dans quiz(), mettre un id : <div class="ex" id="qex_${qi}" role="status">
//   dans answer(), avant render : FOCUS_NEXT="#qex_"+qi;
// addRow(t) : focus sur le 1er champ de la nouvelle ligne
function addRow(t){S.tab[t].push({});save();FOCUS_NEXT=`[onclick="addRow('${t}')"]`;keep();
 const b=document.querySelector(`[onclick="addRow('${t}')"]`),tr=b&&b.previousElementSibling.querySelector("tbody tr:last-child");
 const f=tr&&tr.querySelector("input,select,textarea");if(f)f.focus();}
```
CSS : `#main h2:focus{outline:none}` (titre ciblé par programme, pas par l'utilisateur).

### P1-2 La modale (fiche réflexe, situation, confirmations) ne retient pas le focus
**Constat.** Après l'ouverture de la fiche réflexe, **34 Tab sur 40 sortent de la modale** (mobile comme PC), alors que `aria-modal="true"` est déclaré. Autres défauts : le nom accessible est `aria-labelledby="modalBody"`, c'est-à-dire *tout le contenu* lu comme titre. Il n'y a pas de bouton Fermer visible sans défiler : sur mobile, la fiche fait 717 px et « Fermer » est en bas (capture `a3_m_09_fiche.png`). Enfin, la page derrière défile.

**Correctif.** HTML de `#modal` :
```html
<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle"><div class="card" tabindex="-1">
 <div class="mtop"><button class="btn x" aria-label="Fermer" onclick="closeModal()">✕</button></div>
 <div id="modalBody"></div><div class="rowb"><button class="btn s" onclick="closeModal()">Fermer</button></div></div></div>
```
JS :
```js
// fin de openModal(h) :
 const t=document.querySelector("#modalBody h2,#modalBody h3");if(t)t.id="modalTitle";document.body.classList.add("modal-open");
// début de closeModal() :
 document.body.classList.remove("modal-open");
// piège de focus
document.getElementById("modal").addEventListener("keydown",e=>{if(e.key!=="Tab")return;
 const f=[...e.currentTarget.querySelectorAll('a[href],button:not([disabled]),input:not([type=hidden]),select,textarea,summary,[tabindex="0"]')].filter(x=>x.offsetParent!==null);
 if(!f.length)return;const a=f[0],z=f[f.length-1],c=document.activeElement;
 if(e.shiftKey&&(c===a||c===e.currentTarget.querySelector(".card"))){e.preventDefault();z.focus();}
 else if(!e.shiftKey&&c===z){e.preventDefault();a.focus();}});
```
CSS :
```css
body.modal-open{overflow:hidden}
.modal .card{padding-top:0}
.modal .mtop{position:sticky;top:0;z-index:1;display:flex;justify-content:flex-end;background:#fff;padding:6px 0 0;margin:0 -8px 0 0}
@media print{.modal .mtop{display:none}}
```

### P1-3 Le tiroir mobile fermé reste dans l'ordre de tabulation, et son ombre déborde
**Constat.** À 390 px, le `nav` fermé est seulement translaté (`transform:translateX(-100%)`). Le test Tab depuis l'accueil donne **21 arrêts consécutifs sur des liens hors écran** (`inView:false`) : la recherche, puis les 20 liens du menu. Le lecteur d'écran les lit aussi. De plus, l'ombre `box-shadow:4px 0 16px` reste visible : une bande grise d'environ 15 px longe le bord gauche de tous les écrans mobiles (`a3_m_10_cas_charge.png`, `a3_m_13_*.png`). Enfin, le tiroir n'a pas de bouton de fermeture visible, et Échap ne rend pas le focus au bouton ☰.

**Correctif CSS** (à ajouter après le bloc `@media(max-width:820px)` de la ligne 162) :
```css
@media(max-width:820px){
 nav{visibility:hidden;box-shadow:none;transition:transform .2s,visibility 0s .2s}
 nav.open{visibility:visible;box-shadow:4px 0 16px #0003;transition:transform .2s}
 .nav-x{display:flex}
}
.nav-x{display:none;justify-content:flex-end;padding:6px 10px 0}
```
**HTML** : premier enfant de `<nav>` : `<div class="nav-x"><button class="btn s" onclick="toggleNav(false);document.getElementById('menuBtn').focus()">Fermer le menu ✕</button></div>`.
**JS** : dans `toggleNav`, ajouter à la fin `if(o)setTimeout(()=>document.getElementById("srchIn").focus(),60);`. Dans le gestionnaire Échap : `else if(document.body.classList.contains("navopen")){toggleNav(false);document.getElementById("menuBtn").focus();}`.

### P1-4 Sur PC 1366 px, les tableaux larges sont illisibles
**Constat** (`a3_d_05_pm_a.png`, `a3_d_05_p2e5_a.png`, `a3_d_05_p2e1_a.png`). La zone utile fait 966 px.
- **Plan de manœuvre (9 colonnes)** : la liste « Type » est réduite à 56 px et affiche « For⌄ » ou « Env⌄ ». Les textes sont coupés au milieu des mots (« Engageme/nt », « prolongatio/n »), et **25 textareas sur 45 ont leur contenu masqué**.
- **Confrontation MA × ME** : les listes MA et ME font 55 px et n'affichent que « MA⌄ » et « ME⌄ ». On ne voit pas quel couple est saisi.
- **Matrices de synchronisation** : Unité et Action sont étroites (le texte est tronqué), alors que Phase et PD, souvent vides, prennent la largeur.

**Correctif.**
1. Marquer les colonnes courtes avec `s:1` dans `SYNC_COLS` (`d`, `f`, `ph`) et `PDM_COLS` (`n`, `g`, `gpd`).
2. Les rendre en `<input>` d'une ligne, ce qui sert aussi sur mobile (P2-2). Dans `cell()`, avant le `return` du textarea :
```js
if(c.s)return `<input ${al} value="${esc(v)}" oninput="setc('${tid}',${i},'${c.k}',this.value)">`;
```
3. Remplacer `tbl()` : classes de colonnes, en-tête de ligne `th scope="row"` (P3-7), classe `del`, et mode `wide` à partir de 8 colonnes :
```js
function tbl(b){let rows=S.tab[b.id];if(!rows){rows=b.fixed?b.fixed.map(d=>({d})):[{}];S.tab[b.id]=rows;}
 const nc=c=>c.s||(c.o&&Math.max(...c.o.map(o=>String(o).length))<=12)?"nw":"",wide=b.cols.length>=8;
 return `<div class="tw${wide?" wide":""}"><table><thead><tr>${b.cols.map(c=>`<th class="${nc(c)}">${esc(c.l)}</th>`).join("")}${b.fixed?"":`<th class="del"><span class="sr">Supprimer</span></th>`}</tr></thead><tbody>${rows.map((r,i)=>`<tr>${b.cols.map(c=>c.ro?`<th scope="row" data-l="${esc(c.l)}">${esc(r[c.k])}</th>`:`<td class="${nc(c)}" data-l="${esc(c.l)}">${cell(b.id,i,c,r[c.k])}</td>`).join("")}${b.fixed?"":`<td class="del"><button class="btn x" title="Supprimer" aria-label="Supprimer la ligne ${i+1}" onclick="delRow('${b.id}',${i})">✕</button></td>`}</tr>`).join("")}</tbody></table></div>${b.fixed?"":`<button class="btn s" onclick="addRow('${b.id}')">+ Ajouter une ligne</button>`}`;}
```
4. CSS :
```css
.tw th.nw,.tw td.nw{width:7.5em}.tw th.del,.tw td.del{width:44px}
td select{min-width:6em}
tbody th[scope=row]{background:#fff;color:var(--encre);font-weight:700}
/* 8 colonnes et plus : une fiche par ligne, en grille de 3, entre 601 et 1280 px */
@media(min-width:601px) and (max-width:1280px){
 .tw.wide thead{display:none}.tw.wide table,.tw.wide tbody{display:block}
 .tw.wide tr{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-flow:dense;gap:6px 12px;border:1px solid var(--argent-c);border-radius:6px;margin:10px 0;padding:10px;background:#fff}
 .tw.wide td{display:block;border:none;padding:0;grid-column:span 3}
 .tw.wide td.nw{grid-column:span 1}
 .tw.wide td.del{grid-column:3;grid-row:1;justify-self:end}
 .tw.wide td[data-l]::before{content:attr(data-l);display:block;font-size:.8em;font-weight:600;color:var(--gris)}
}
```

### P1-5 Le schéma du cycle (accueil PC) cache ses liens et coupe sa dernière ligne
**Constat.**
- Le `<svg role="img">` contient 17 `<g tabindex="0" role="link">`. Avec `role="img"`, les enfants deviennent présentationnels : **les lecteurs d'écran ne voient aucun des 17 liens** (axe : `nested-interactive`, sérieux).
- Le nom `aria-label="1. Mission"` ne contient pas le texte visible « Pourquoi ? Quoi ? » (axe : `label-content-name-mismatch` ×45, WCAG 2.5.3).
- Le `viewBox` fait 340 de haut alors que les questions de la phase 2 descendent jusqu'à y = 344 : « Comment ENI ? », « Comment AMI ? », « MA / MA »… sont **coupés** (`a3_d_01_accueil.png`).
- L'indicateur de focus (`.nd:focus rect`) ne s'applique pas aux **losanges des réunions** (`polygon`) : aucun repère de focus sur Orientation, Synthèse et Décision.

**Correctif `cycleSvg()`** :
```js
// viewBox et rôle
let s=`<svg viewBox="0 0 ${W} 360" role="group" aria-label="Schéma du cycle MEDOT …">…`;
// nom = texte visible
s+=`<g class="nd${soon?" soon":""}" tabindex="0" role="link" aria-label="${esc(l+(q?" – "+q:""))}" …>`;
```
CSS (remplace la ligne 95) :
```css
.cycle-svg .nd:hover :is(rect,polygon),.cycle-svg .nd:focus-visible :is(rect,polygon){stroke:#1E2227;stroke-width:3;stroke-dasharray:none}
.cycle-svg .nd:focus-visible :is(rect,polygon){stroke-dasharray:5 3}
```

---

## P2 – Important

### P2-1 Les textareas ne s'agrandissent pas : du contenu reste masqué
**Constat.** La hauteur est estimée une seule fois (`rows = longueur/80` ou `/22`), puis ne bouge plus. Textareas dont le contenu dépasse : **p2e6 PC 37/155**, **p2e1 PC 21/84**, **pm PC 25/45**, p2e1 mobile 6/84. Exemples : « Besoins en renseignement » (p2e1), « Synthèse de la comparaison » (p2e4).
**Correctif** (appelé dans le wrapper `render` de P1-1) :
```js
function autoH(list){const L=[...list].filter(t=>t.offsetParent!==null);L.forEach(t=>t.style.height="auto");
 const h=L.map(t=>t.scrollHeight);L.forEach((t,i)=>t.style.height=(h[i]+2)+"px");}
document.addEventListener("input",e=>{if(e.target.matches("#main textarea"))autoH([e.target]);});
document.addEventListener("toggle",e=>{if(e.target.open)autoH(e.target.querySelectorAll("textarea"));},true);
```
Le calcul est groupé (une lecture, puis une écriture) : un seul reflow, même pour 155 champs. `field-sizing:content` a été écarté parce que Firefox ESR ne le prend pas en charge.

### P2-2 Les pages « Appliquer » sont très longues sur mobile
**Constat.** p2e6 fait 22 070 px, p2e2 16 795 et p2e1 12 701. Une ligne de matrice de synchronisation occupe **environ 660 px** (7 champs empilés). Les GDH et le PD sont des textareas de 2 lignes (53 px). Le bouton ✕ reste seul en bas de la fiche, sans libellé visible. La matrice ME 1 seule mesure 4 828 px. Il n'y a ni sommaire ni retour en haut.
**Correctif.**
- Colonnes `s:1` en `<input>` (P1-4).
- Fiche de ligne sur 2 colonnes :
```css
@media(max-width:600px){
 .tw tr{display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:dense;gap:2px 10px}
 .tw td,.tw th[scope=row]{display:block;border:none;padding:4px 2px;grid-column:1/-1}
 .tw td.nw{grid-column:auto}
 .tw td.del{grid-column:2;grid-row:1;justify-self:end;padding:0}
 .tw td.del .btn.x::after{content:" Supprimer";font-size:.8em}
}
```
- Sommaire de l'onglet et bouton de retour en haut :
```js
function applyToc(){if(curTab!=="a")return;const el=document.getElementById("main"),hs=[...el.querySelectorAll(".card>h3")];if(hs.length<4)return;
 const n=document.createElement("nav");n.className="toc";n.setAttribute("aria-label","Sommaire de l’onglet");
 n.innerHTML=hs.map((h,i)=>{h.id="sec_"+i;h.tabIndex=-1;return `<a href="#sec_${i}" onclick="event.preventDefault();const h=document.getElementById('sec_${i}');h.scrollIntoView();h.focus({preventScroll:true})">${esc(h.textContent)}</a>`;}).join("");
 const t=el.querySelector(".tabs");if(t)t.after(n);}
const toTop=document.getElementById("toTop");addEventListener("scroll",()=>{toTop.hidden=scrollY<1200;},{passive:true});
```
Le `preventDefault` est indispensable : sinon `hashchange` appelle `fromHash()`, qui relance le rendu et remet la page en haut.
HTML (à placer **avant** la balise `<script>`, par exemple après `<footer>`, pour que `getElementById("toTop")` le trouve) : `<button id="toTop" class="btn dk" hidden aria-label="Revenir en haut de la page" onclick="scrollTo(0,0);const h=document.querySelector('#main h2');h&&(h.tabIndex=-1,h.focus({preventScroll:true}))">↑</button>`
```css
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.toc a{font-size:.85em;padding:6px 12px;border:1px solid var(--argent);border-radius:16px;color:var(--encre);text-decoration:none;background:#fff}
.toc a:hover{background:var(--rouge-c)}
@media(pointer:coarse){.toc a{min-height:40px;display:inline-flex;align-items:center}}
#toTop{position:fixed;right:14px;bottom:14px;z-index:6;width:48px;height:48px;border-radius:50%;font-size:1.3em;box-shadow:0 2px 8px #0004}
@media print{.toc,#toTop{display:none}}
```

### P2-3 Le Gantt est peu lisible sur mobile
**Constat** (`a3_m_05_p2e1_a.png`). À 390 px, les deux dernières graduations se chevauchent (« J+1 06hJ+1 12h »). Les graduations sont en **10,3 px**. L'axe ne figure qu'au-dessus de la première ligne : au défilement, les barres perdent leur repère temporel (de 5 à 13 lignes selon la matrice).
**Correctif.** Dans `CHARTS.sync`, remplacer la ligne `stH` :
```js
const maxT=matchMedia("(max-width:600px)").matches?3:6;
const stH=[1,2,3,4,6,12,24,48].find(h=>sp/(h*60)<=maxT)||96,st=stH*60,pc=x=>(100*(x-t0)/sp).toFixed(2);
```
Puis recalculer au redimensionnement (rotation, fenêtre PC) :
```js
let rsz;addEventListener("resize",()=>{clearTimeout(rsz);rsz=setTimeout(()=>{refreshCharts();autoH(document.querySelectorAll("#main textarea"));},200);});
```
CSS :
```css
.gantt .ticks{font-size:12px;height:20px}
.gantt .gr.ax{position:sticky;top:0;z-index:2;background:#fff;padding:4px 0;border-bottom:1px solid var(--argent-c)}
```

### P2-4 Contraste insuffisant
| Élément | Mesure | Seuil | Correctif |
|---|---|---|---|
| `.pdk` « ★ PD… » (Gantt, grille MA×ME, légende), 12,9 px gras | **3,57:1** (#B07F00 sur blanc) | 4,5 | `.pdk{color:var(--ambre)}` (#8A5700, ≈ 6:1) |
| Barre de Gantt sans fonction (#8B9199 sur #F3F4F6) | 2,89:1 | 3 (1.4.11) | `FO_COL[r.fo]\|\|"#6B7179"` (4,5:1) |
| Étoile `.pd` sur la piste (#E0A800) | 1,95:1, compensée par le liseré noir | 3 | conserver le `text-shadow` ; facultatif : `-webkit-text-stroke:.5px #1E2227` |

### P2-5 Erreurs ARIA relevées par axe
- `aria-prohibited-attr` (×68) : `.sb aria-label` posé sur un `div` sans rôle (barres « Ma progression » et résultat d'examen). → Ajouter `role="img"` aux deux gabarits `<div class="sb" role="img" aria-label=…>`.
- Onglets : `role="tablist"` et `role="tab"` sont présents, mais sans `tabpanel`, sans `aria-controls` et sans navigation aux flèches. Ces boutons sont en réalité de la navigation. Remplacer la ligne 518 par :
```js
h+=`<div class="tabs" role="group" aria-label="Temps de l’étape">${[["c","1 · Comprendre"],["e","2 · S’entraîner"],["a","3 · Appliquer"]].map(t=>`<button type="button" ${curTab===t[0]?'aria-current="step"':""} class="${curTab===t[0]?"on":""}" onclick="go('${m.id}','${t[0]}')">${t[1]}</button>`).join("")}</div>`;
```
- `empty-table-header` : la cellule d'angle de la grille MA×ME est vide. → `<span role="columnheader"><span class="sr">MA / ME</span></span>`.
- `label-content-name-mismatch` du schéma : traité en P1-5.

### P2-6 Les couleurs de sens ne sont pas cohérentes d'un module à l'autre
**Constat.**
- « Risque » est **ambre** dans la confrontation des séquences (`.mid.ri`) et sur la frise du plan de manœuvre, mais **rouge** dans la grille MA×ME (« risques seuls ») et dans la comparaison (« − »). Dans la grille, l'ambre signifie « mixte ».
- Dans le plan de manœuvre, les étiquettes « Opportunité » et « Risque » sont grises : seule la pastille porte le sens.
- Frise consolidée : 14 couleurs de source, dont plusieurs impossibles à distinguer (#B3121F / #9D174D / #C2410C ; #A86B00 / #8B5A2B). L'origine n'est donnée que par la couleur et la légende (1.4.1).

**Règle proposée** : vert ▲ = opportunité ou avantage ; rouge ▼ = risque ou inconvénient ; ambre = mixte ou attention. Toujours avec pictogramme et texte.
```css
.sync .mid.ri,.sync-m .mid.ri{border-color:var(--rouge);background:var(--rouge-c)}.sync .mid.ri b{color:var(--rouge-f)}
.tag.t-op{background:var(--vert-c);color:var(--vert)}.tag.t-ri{background:var(--rouge-c);color:var(--rouge-f)}
```
```js
// CHARTS.pdm : légende et pastille « Risque » en var(--rouge) au lieu de var(--ambre) ; étiquette colorée :
${r.cn?` <span class="tag ${r.cn==="Risque"?"t-ri":"t-op"}">${r.cn==="Risque"?"▼":"▲"} ${esc(r.cn)}</span>`:""}
// CHARTS.frise : origine en texte
<span class="e">${esc(r.e)} <span class="tag">${esc(title(r.src))}</span></span>
```

### P2-7 Cibles tactiles trop petites (2.5.8, et 44 px recommandés)
Mesures sous `pointer:coarse`, à 390 px :
- `summary` des bandeaux démo et cas : **16 px** de haut (sous les 24 px du minimum AA) ;
- libellé de l'interrupteur « Exemple fictif » : 104 × 30 px ;
- liens du graphique « Ma progression » et du résultat d'examen : **20 px** ;
- lien d'évitement : 23 px.
```css
@media(pointer:coarse){
 .demo-banner summary,.cas-banner summary{display:list-item;list-style-position:inside;padding:12px 0}
 .demo-sw{display:inline-flex!important;align-items:center;gap:8px;min-height:44px}
 .scores a{display:inline-block;padding:10px 0}
 .skip:focus{padding:12px 14px}
}
```

### P2-8 iOS zoome dès qu'on touche un champ
**Constat.** Les champs de tableau sont en **13,8 px**, les champs `.fld` en 15 px. Safari iOS zoome sur tout champ de moins de 16 px, puis ne revient pas à l'échelle. Android n'est pas concerné.
```css
@media(max-width:600px){input,select,textarea{font-size:16px}}
```

### P2-9 Sur mobile, les bandeaux mangent un tiers de l'écran
**Constat.** Avec démo et cas actifs, l'en-tête et les deux bandeaux occupent **290 px sur 844 (34 %)** avant le titre de l'étape (`a3_m_13_demo_cas_p2e4.png`). Le bouton « Revenir à mes travaux » est seul sur sa ligne.
```css
@media(max-width:600px){
 .demo-banner{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px;padding:6px 12px;font-size:.85em}
 .demo-banner details{flex:1 1 60%}.demo-banner .btn{margin-left:auto}
 .cas-banner{padding:6px 12px;font-size:.85em;gap:4px 8px}.cas-banner>span:first-child{flex:1 1 100%}
}
```
Facultatif : déplacer « Modifications non enregistrées » dans le `summary` (« Exemple fictif – non enregistré »).

---

## P3 – Finitions

1. **L'élément actif du menu PC n'est pas visible** quand il est bas dans la liste : sur p2e4, « Étape 4 – Comparaison des MA » est coupé en bas du menu. À la fin de `renderNav()` :
```js
if(matchMedia("(min-width:821px)").matches){const n=document.getElementById("nav"),a=n.querySelector("#navList a.on");
 if(a&&(a.offsetTop<n.scrollTop||a.offsetTop+a.offsetHeight>n.scrollTop+n.clientHeight))n.scrollTop=a.offsetTop-n.clientHeight/3;}
```
2. **Cases à cocher en bleu système**, hors charte (en-tête, canevas) : `input[type=checkbox],input[type=radio]{accent-color:var(--rouge)}`.
3. **L'étiquette du titre (`h2 .tag`) hérite du Georgia du titre** : elle s'affiche en grosse pastille serif (« Pourquoi ? Quoi ? », « MA / MA »), surtout sur mobile et dans la fiche. Correctif : `h2 .tag{font:600 .5em/1.7 "Segoe UI",Calibri,Arial,sans-serif;vertical-align:.3em}`.
4. **Légende de la grille MA×ME presque invisible** : `.legend i` (rond de 10 px) écrase `.lg`, ce qui donne des cercles creux pâles. Correctif : `.legend i.lg{width:14px;height:14px;border-radius:3px;border-width:2px;border-style:solid}`.
5. **Examen blanc** : le fond de la réponse choisie (`.sel`) est écrasé par `:hover` (gris sur PC, blanc sur tactile, où le survol reste collé). Correctif : `.qz .o.sel,.qz .o.sel:hover{background:var(--rouge-c)}`.
6. **« Tout effacer » a le même style que « Copier »**. Proposer `class="btn danger"`, isolé à droite : `.btn.danger{background:#fff;color:var(--rouge-f);border:1.5px solid var(--rouge);margin-left:auto}.btn.danger:hover{background:var(--rouge-c)}`.
7. **Tableaux vides** : les TCIDR et la frise d'une étape sans ligne n'affichent qu'un en-tête noir (`a3_d_12_cas_corrige.png`). Dans `tcidrTbl` et `friseTbl`, si `!L.length`, rendre `<p class="ref">Aucun élément pour cette étape.</p>` à la place du tableau. Les en-têtes de ligne en lecture seule (Fonction, p2e3) passent en `th scope="row"` (fait dans `tbl()` en P1-4).
8. **Contenu hors repères** (axe `region`, ×26) : les bandeaux sont hors des repères de page. Ajouter `role="region" aria-label="Exemple fictif"` sur `#demoBanner`, et `role="region" aria-label="Cas concret"` sur `#casBanner`.
9. **Libellés « Ph. 1 – Étape 3 » peu parlants** dans « Ma progression » et le résultat d'examen. Avec `shortT`, 11 lignes sur 17 se ressemblent. Proposer `` `${p}${m.title.replace(/^Étape (\d) – /,"$1. ")}` ``, par exemple « Ph. 1 – 3. Analyse des forces ennemies ». Sur mobile, la grille de l'accueil (`.cycle`) n'indique pas les étapes validées alors que le schéma PC le fait. Dans `box()`, ajouter `${m&&m.quiz&&done(id)?' <span aria-label="validée">✓</span>':""}`.
10. **Comparaison pondérée sur PC** : le critère et ses notes sont séparés d'environ 600 px (grille pleine largeur, 966 px), ce qui oblige à suivre la ligne des yeux. Correctif : `.cmpg,.tot{max-width:680px}`.

---

## Bloc CSS consolidé (à ajouter en fin de `<style>`, après la ligne 244)

```css
/* ---- audit v2 forme ---- */
#main h2:focus{outline:none}
body.modal-open{overflow:hidden}
.modal .card{padding-top:0}
.modal .mtop{position:sticky;top:0;z-index:1;display:flex;justify-content:flex-end;background:#fff;padding:6px 0 0;margin:0 -8px 0 0}
@media(max-width:820px){nav{visibility:hidden;box-shadow:none;transition:transform .2s,visibility 0s .2s}nav.open{visibility:visible;box-shadow:4px 0 16px #0003;transition:transform .2s}.nav-x{display:flex}}
.nav-x{display:none;justify-content:flex-end;padding:6px 10px 0}
.tw th.nw,.tw td.nw{width:7.5em}.tw th.del,.tw td.del{width:44px}
td select{min-width:6em}
tbody th[scope=row]{background:#fff;color:var(--encre);font-weight:700}
@media(min-width:601px) and (max-width:1280px){
 .tw.wide thead{display:none}.tw.wide table,.tw.wide tbody{display:block}
 .tw.wide tr{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-flow:dense;gap:6px 12px;border:1px solid var(--argent-c);border-radius:6px;margin:10px 0;padding:10px;background:#fff}
 .tw.wide td{display:block;border:none;padding:0;grid-column:span 3}.tw.wide td.nw{grid-column:span 1}
 .tw.wide td.del{grid-column:3;grid-row:1;justify-self:end}
 .tw.wide td[data-l]::before{content:attr(data-l);display:block;font-size:.8em;font-weight:600;color:var(--gris)}}
@media(max-width:600px){
 .tw tr{display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:dense;gap:2px 10px}
 .tw td,.tw th[scope=row]{display:block;border:none;padding:4px 2px;grid-column:1/-1}
 .tw td.nw{grid-column:auto}.tw td.del{grid-column:2;grid-row:1;justify-self:end;padding:0}
 .tw td.del .btn.x::after{content:" Supprimer";font-size:.8em}
 input,select,textarea{font-size:16px}
 .demo-banner{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px;padding:6px 12px;font-size:.85em}
 .demo-banner details{flex:1 1 60%}.demo-banner .btn{margin-left:auto}
 .cas-banner{padding:6px 12px;font-size:.85em;gap:4px 8px}.cas-banner>span:first-child{flex:1 1 100%}}
.cycle-svg .nd:hover :is(rect,polygon),.cycle-svg .nd:focus-visible :is(rect,polygon){stroke:#1E2227;stroke-width:3}
.cycle-svg .nd:focus-visible :is(rect,polygon){stroke-dasharray:5 3}
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.toc a{font-size:.85em;padding:6px 12px;border:1px solid var(--argent);border-radius:16px;color:var(--encre);text-decoration:none;background:#fff}
.toc a:hover{background:var(--rouge-c)}
#toTop{position:fixed;right:14px;bottom:14px;z-index:6;width:48px;height:48px;border-radius:50%;font-size:1.3em;box-shadow:0 2px 8px #0004}
.gantt .ticks{font-size:12px;height:20px}
.gantt .gr.ax{position:sticky;top:0;z-index:2;background:#fff;padding:4px 0;border-bottom:1px solid var(--argent-c)}
.pdk{color:var(--ambre)}
.sync .mid.ri,.sync-m .mid.ri{border-color:var(--rouge);background:var(--rouge-c)}.sync .mid.ri b{color:var(--rouge-f)}
.tag.t-op{background:var(--vert-c);color:var(--vert)}.tag.t-ri{background:var(--rouge-c);color:var(--rouge-f)}
input[type=checkbox],input[type=radio]{accent-color:var(--rouge)}
h2 .tag{font:600 .5em/1.7 "Segoe UI",Calibri,Arial,sans-serif;vertical-align:.3em}
.legend i.lg{width:14px;height:14px;border-radius:3px;border-width:2px;border-style:solid}
.qz .o.sel,.qz .o.sel:hover{background:var(--rouge-c)}
.btn.danger{background:#fff;color:var(--rouge-f);border:1.5px solid var(--rouge);margin-left:auto}.btn.danger:hover{background:var(--rouge-c)}
.cmpg,.tot{max-width:680px}
@media(pointer:coarse){
 .demo-banner summary,.cas-banner summary{display:list-item;list-style-position:inside;padding:12px 0}
 .demo-sw{display:inline-flex!important;align-items:center;gap:8px;min-height:44px}
 .scores a{display:inline-block;padding:10px 0}.skip:focus{padding:12px 14px}
 .toc a{min-height:40px;display:inline-flex;align-items:center}}
@media print{.modal .mtop,.toc,#toTop{display:none}}
```

## Ordre d'intégration du JS
1. Ajouter `s:1` dans `SYNC_COLS` (`d`, `f`, `ph`) et dans `PDM_COLS` (`n`, `g`, `gpd`). Modifier ensuite `cell()` (branche `c.s`) et `tbl()` (P1-4).
2. `cycleSvg()` : `viewBox` 360, `role="group"`, `aria-label` complet (P1-5).
3. Ligne 518 (onglets en `role="group"` avec `aria-current`). Ajouter `role="img"` sur les deux `.sb`. Mettre la cellule d'angle `sr` de la grille MA×ME (P2-5).
4. `CHARTS.sync` (`maxT`), `CHARTS.pdm` et `CHARTS.frise` (P2-3, P2-6). Mettre `FO_COL[...]||"#6B7179"` (P2-4).
5. `openModal`, `closeModal`, piège de focus et HTML de `#modal` (P1-2). `toggleNav`, Échap et `.nav-x` (P1-3).
6. Avant `INIT` : `autoH`, `applyToc`, `focusKey`, l'enveloppe de `render`, l'écouteur `resize` et `toTop` (P1-1, P2-1, P2-2, P2-3). Ajuster ensuite `tryGo`, le clic du menu, `answer` (avec `id="qex_${qi}"` dans `quiz()`) et `addRow`.
7. P3 : `renderNav()` (défilement de l'élément actif), `home()` (`btn danger`, ✓ sur la grille mobile), `tcidrTbl` et `friseTbl` (état vide), régions des bandeaux, libellés de progression.

Après intégration, revérifier :
- Tab de bout en bout à 390 px : aucun arrêt hors écran ;
- 40 Tab dans la fiche réflexe : 0 sortie ;
- quiz et « Ajouter une ligne » au clavier : le focus est conservé ;
- PDM et MA×ME à 1366 px : plus de liste tronquée ;
- p2e6 à 390 px : la hauteur doit passer d'environ 22 000 px à environ 12 000 px.

## Non testé
- **Firefox** : le moteur n'est pas installé dans l'environnement d'audit. Les propriétés proposées sont compatibles avec Firefox ESR 115 et suivants (`:is`, `:focus-visible`, `accent-color`, `CSS.escape`, `inert` non utilisé). `:has()` et `field-sizing` sont volontairement évités.
- **iframe claude.ai réelle** : seuls les chemins du code ont été relus (stockage, presse-papiers, téléchargement, impression, tous protégés par `try/catch`).
- **Lecteurs d'écran réels** (NVDA, VoiceOver) : seuls axe et les tests de focus ont été utilisés.
