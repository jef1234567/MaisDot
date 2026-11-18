# Spécification commune – livraison 2 (phase 2 + finalisation)

Webapp : `src/app.html` (monofichier, hors ligne, aucun CDN). Build : `python3 build.py` → `index.html` (insère `src/demo.js` puis `src/p2.js` aux emplacements `/*__demo.js__*/` et `/*__p2.js__*/`).
Contenu : tableau JS `M` (modules). `src/p2.js` définit `P2` (tableau de modules) et `DEMO_P2` ; le code d'intégration (déjà présent dans app.html, juste après le placeholder p2.js) remplace les deux modules « à venir » (`id:"p2"` et `id:"pm"`) par `P2`, et fusionne `DEMO_P2` dans `DEMO` (v, tab : Object.assign ; tcidr, frise : push).

## Identifiants des modules de P2 (dans cet ordre)
| id | grp | title |
|---|---|---|
| p2e1 | Phase 2 – Conception de la manœuvre | Étape 1 – Conception des ME |
| p2e2 | idem | Étape 2 – Conception des MA |
| p2e3 | idem | Étape 3 – Manœuvres fonctionnelles |
| p2e4 | idem | Étape 4 – Comparaison des MA |
| p2e5 | idem | Étape 5 – Confrontation MA-ME |
| p2e6 | idem | Étape 6 – Finalisation des MA |
| dec | idem | Réunion de décision (reu:1) |
| pm | idem | Finalisation du plan de manœuvre |

Format d'un module : comme les modules existants de `M` (`id, grp, title, qtag?, ref, but, sections:[{h,p?|l?}], vig:[], canevas?:[], apply:[blocs], quiz:[{q,o:[bonne,faux,faux,faux],a:0,e}]`).

## Blocs `apply` disponibles
Existants : `{t:"note",x}`, `{t:"fields",id,f:[{k,l,a?,o?,h?}]}`, `{t:"table",id,cols:[{k,l,o?,ro?}],fixed?}`, `{t:"canevas"}`, `{t:"tcidr"}`, `{t:"frise"}`, `{t:"tiers"}`, `{t:"chart",k,l}` (k = clé de `CHARTS`).

Nouveaux (implémentés dans app.html par l'agent fonctionnalités) — **modèle de données figé** :

### `{t:"sync", id:"<id>", l:"<titre>"}` – matrice de synchronisation (tableau + Gantt)
Données : `S.tab["sync_"+id]` = lignes `{u:unité, a:action, fo:fonction opérationnelle, d:GDH début, f:GDH fin, ph:phase/temps, pd:"" | "PD1"…}`. GDH au format « J 06h00 », « J+1 02h00 », « J-1 18h00 » (fonction existante `gdhKey`). Graphique : barres par ligne entre d et f, couleur par fonction, étoile ★ sur les lignes ayant un point de décision.
Ids utilisés : `me1`, `me2` (ME), `ma1`, `ma2` (MA, en p2e2 ébauche, en p2e6 finalisée : `ma1f`, `ma2f`… → au choix de l'agent contenu, tant qu'il les déclare dans apply et dans DEMO_P2).

### `{t:"cmp"}` – comparaison pondérée des MA
Données : `S.tab.cmp` = lignes `{c:critère, w:"1"|"2"|"3" (poids), s1:"+"|"="|"−", s2:"+"|"="|"−", a1:avantages/inconvénients MA1 (texte), a2:idem MA2}`. Total = Σ w × (+1/0/−1) par MA, affiché + graphique barres. Les critères du chef saisis en réunion de synthèse (`S.v.synv.crit`) sont rappelés au-dessus.

### `{t:"mame"}` – confrontation MA × ME
Données : `S.tab.mame` = lignes `{ma:"MA1"|"MA2", me:"ME1"|"ME2", o:opportunités, r:risques, am:amendements au MA, pd:point de décision}`. Graphique : grille MA (lignes) × ME (colonnes), cellule verte/ambre/rouge selon présence d'opportunités / risques, compteurs.

### `{t:"pdm"}` – plan de manœuvre
Données : `S.tab.pdm` = lignes `{n:N°, g:GDH, h:hypothèse, ty:"Forces ennemies"|"Forces amies"|"Environnement", cn:"Opportunité"|"Risque", im:impact (mission / effet majeur / MA), rens:renseignement à rechercher, gpd:GDH du point de décision, sol:ébauche de solution tactique}`.

## Situation fictive (DEMO_P2)
Prolonger Valdor (`src/demo.js`, à lire) : ennemi Kardestan (2 BMECA), GTIA ALPHA freine entre le bois de Vernes et la Sarve, recueil au nord ; effet majeur retenu : « User d’au moins 30 % le BMECA de tête dans la trouée de Vernes entre J 14h00 et J 20h00… ». Deux ME (ex. ME1 effort D17 dans la trouée ; ME2 débordement par l’est / Saint-Ivre), deux MA. Tout reste fictif.
