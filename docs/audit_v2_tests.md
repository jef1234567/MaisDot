# Audit v2 – tests fonctionnels automatisés (MaisDot)

- Suite : `tests/test_app.py` (Playwright Python, Chromium, `file://…/index.html`)
- Exécution : `python3 tests/test_app.py` (filtre possible : `python3 tests/test_app.py cmp`)
- `index.html` vérifié identique à la sortie de `build.py` (src/app.html + demo.js + p2.js) avant exécution. `src/` non modifié.
- Chaque scénario est joué dans un contexte neuf (localStorage vide), en **1366x768** et en **390x844** (tactile, menu ☰). Chaque test vérifie aussi l'absence d'erreur JS (`pageerror`, `console.error`).
- Résultat : **34 OK / 4 KO** (19 scénarios × 2 formats, 37 s). Les 4 KO viennent de **2 défauts**, chacun reproduit dans les deux formats.

## Tableau des tests

| # | Scénario | Ce qui est vérifié | PC 1366x768 | Mobile 390x844 |
|---|---|---|---|---|
| 1 | Chargement | Accueil rendu, 21 liens de menu, intégration P2 (plus de module « à venir »), progression 0, ☰ et #demoSw visibles en mobile, aucune erreur console | OK | OK |
| 2 | Navigation | 21 modules par clic dans le menu (ouverture/fermeture du ☰ en mobile), `aria-current`, titre ; 17 étapes × 3 onglets (`aria-selected`, contenu, nombre de questions = quiz) ; accès par ancre `#p2e4` | OK | OK |
| 3 | Quiz | Bonnes réponses sur p1e1 → « 7 / 7 – Étape validée ✓ », progression « 1 / 17 », ✓ dans le menu, `aria-valuenow`, score en localStorage ; échec sur p1e2 non compté ; progression conservée au rechargement | OK | OK |
| 4 | Persistance | Champ (fields), contrôle « Afin de », tableau (texte + select + ligne ajoutée), TCIDR (ajout, type), frise (ajout) → rechargement → valeurs relues ; frise visible dans le récapitulatif | OK | OK |
| 5 | Exemple fictif | Saisie utilisateur → #demoSw : valeurs démo affichées, modification en démo non enregistrée, localStorage intact (aucune donnée démo) ; retour → saisie utilisateur ; rechargement → démo désactivée, saisie intacte | OK | OK |
| 6 | Bloc sync | 3 lignes ajoutées / 1 supprimée, Gantt rafraîchi (nombre de barres), tri J-1 → J → J+1, ★ du point de décision, couleur de la fonction opérationnelle, suppression enregistrée | OK | OK |
| 7 | Bloc cmp | Rappel des critères du chef ; **calcul** : 4 critères (3/+/−, 2/=/+, 1/−/+, 3/+/+) → MA1 +5, MA2 +3, échelle ±9 ; après suppression → MA1 +2, MA2 0, ±6, « MA1 l'emporte (+2 contre 0) », `cmpTot` = {2,0,6} ; égalité 6/6 détectée ; `cmpS` accepte « - » et « − » ; totaux repris dans l'export Word | OK | OK |
| 8 | Bloc mame | 4 lignes puis 1 supprimée : cellules verte (opportunités seules), rouge (risques seuls), ambre (les deux), « Non confronté » ; ★ PD1 ; compteurs « 2 opportunité(s) · 2 risque(s) · 1 amendement(s) · 1 point(s) » | OK | OK |
| 9 | pdm + tri GDH | Plan de manœuvre trié J-1 18h00 < J 06h00 < J+1 02h00 (ligne ajoutée puis supprimée) ; frise consolidée triée (y compris « J−1 » en moins Unicode et « J 12h ») ; `gdhKey` | OK | OK |
| 10 | Examen blanc | 30 questions distinctes réparties sur ≥ 10 étapes, chrono, changement d'avis (une seule sélection), compteur ; fin anticipée → avertissement « 24 questions sans réponse » → « 5 / 30 – 17 % », « Erreurs à revoir (25) », meilleur score stocké et rappelé à l'accueil | OK | OK |
| 11 | Chargeur de cas | Import `docs/exemple_cas_valdor.json` par l'input file → « corrigé pour 3 étape(s) », bandeau, « Lire la situation », « Voir le corrigé » / « Masquer » (`aria-expanded`), étape sans corrigé, persistance au rechargement, « Retirer le cas » (localStorage vidé, bouton corrigé disparu), fichier invalide refusé | OK | OK |
| 12 | Bandeau cas masqué sans cas | `#casBanner` ne doit occuper aucune place sans cas chargé (au chargement et après retrait) | **KO** | **KO** |
| 13 | Export / Tout effacer / réimport | Téléchargement `MEDOT_sauvegarde.json` (contenu vérifié) et `MEDOT_travaux.doc` (hors ligne) ; « Tout effacer » (localStorage vide, progression 0, champ vide) ; réimport (progression et champ repris, persistant après rechargement) ; fichier non reconnu refusé | OK | OK |
| 14 | Réimport du même fichier | `#fImp` vide après lecture, pour qu'une 2e sélection du même fichier déclenche `change` (comme `#fCas`) | OK | OK |
| 15 | Reprise de sauvegarde pendant l'exemple fictif | Sauvegarde reprise alors que la démo est affichée → doit être présente après « Revenir à mes travaux » et après rechargement | **KO** | **KO** |
| 16 | Recherche | Sigle (« gtia »), définition (« effet majeur »), insensibilité aux accents (« presupposition »), aucun résultat, < 2 caractères ; clic sur une étape, une définition (carte retournée) et un sigle (ligne surlignée) | OK | OK |
| 17 | localStorage indisponible (méthodes) | `Storage.prototype.getItem/setItem/removeItem` lèvent une `SecurityError` : saisie, TCIDR, quiz et progression, cmp, démo, chargement de cas (message « non mémorisé »), retrait, examen → aucune erreur JS | OK | OK |
| 18 | localStorage indisponible (getter) | `window.localStorage` lui-même lève une exception : même parcours | OK | OK |
| 19 | `window.claude.use('downloads')` simulé | Export Word → `save({filename:"MEDOT_travaux.doc", data:"<html…"})` avec la saisie, message « enregistré » ; export .json → `save()` ; aucun téléchargement classique ; `save()` qui échoue → message de repli | OK | OK |

## Détail des KO

### KO 1 – Bandeau « cas concret » vide affiché en permanence (tests 12, PC et mobile)

- **Constat** : sans cas chargé, une bande bleue vide de 22 px (fond `#E3EDF7`, bordure basse bleue) s'affiche sous l'en-tête, dès l'ouverture puis après « Retirer le cas ». `renderCas()` met bien `hidden=true` et vide le contenu, mais l'élément reste affiché (`display:flex` calculé).
- **Cause** : `src/app.html` ligne 219, règle CSS `.cas-banner{…;display:flex;…}`. Une règle d'auteur `display` l'emporte sur la règle du navigateur `[hidden]{display:none}`, donc l'attribut `hidden` posé par `renderCas()` (ligne 767) et présent dans le HTML (ligne 258) n'a aucun effet. `.demo-banner` (ligne 89) n'a pas ce problème parce qu'elle ne fixe pas de `display`.
- **Correctif proposé** (une ligne, dans le CSS) :
  ```css
  .cas-banner[hidden]{display:none}
  ```
  ou, plus général, `[hidden]{display:none!important}` en tête de feuille de style.

### KO 2 – Une sauvegarde reprise pendant l'« Exemple fictif » est perdue sans prévenir (tests 15, PC et mobile)

- **Constat** : démo active → accueil → « Reprendre une sauvegarde » → message « Sauvegarde reprise. », les données s'affichent. Après « Revenir à mes travaux », les travaux d'avant l'import réapparaissent. La sauvegarde n'a été ni gardée en mémoire ni écrite dans localStorage : elle est perdue.
- **Cause** : `importJson()` (`src/app.html` ligne 747) remplace `S` (la copie de démonstration) et appelle `save()`, qui ne fait rien en mode démo (ligne 486 : `if(DEMO_ON)return;`). `setDemo(false)` (lignes 860-863) remet ensuite `S=USER`, c'est-à-dire l'ancien état. `resetAll()` (ligne 749) a le même défaut : en mode démo, « Tout effacer » vide seulement la copie de démonstration, alors que la boîte de dialogue annonce que « toutes tes saisies » seront supprimées.
- **Correctif proposé** : quitter le mode démo avant d'agir sur les travaux de l'utilisateur.
  ```js
  // importJson, dans r.onload, avant de remplacer S :
  if(DEMO_ON)setDemo(false);
  S=Object.assign({quiz:{},v:{},tab:{},tcidr:[],frise:[]},o);save();render();msg("Sauvegarde reprise.");
  ```
  ```js
  // resetAll, dans le bouton de confirmation :
  onclick="if(DEMO_ON)setDemo(false);S={quiz:{},v:{},tab:{},tcidr:[],frise:[],unlock:false};save();closeModal();go('accueil')"
  ```
  Autre option, plus stricte : désactiver « Reprendre une sauvegarde » et « Tout effacer » tant que la démo est active, avec une phrase d'explication.

## Observations hors KO (comportements à trancher, non bloquants)

- **Quiz en mode démo** : `setDemo(true)` partage `S.quiz` avec `USER.quiz` (même objet, ligne 861). Un test réussi pendant la démo n'est pas enregistré tout de suite (`save()` ne fait rien), mais il l'est à la première saisie suivante hors démo. Le comportement est cohérent avec « la démo ne touche pas aux saisies » pour les gabarits, mais pas pour les scores : il faut décider s'ils comptent et, si oui, les enregistrer tout de suite.
- **Réimport du même fichier** (test 14, OK) : `importJson` ne vide pas `inp.value`. Le cas est couvert par hasard, parce que `render()` reconstruit l'accueil et donc l'input. Un `inp.value=""` explicite, comme dans `importCas` (ligne 766), rendrait ce comportement indépendant du rendu.
- Aucune erreur JS n'a été relevée dans les 38 exécutions, y compris quand localStorage est inaccessible.
