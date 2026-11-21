# MaisDot – Parcours d’apprentissage de la MEDOT

Webapp pédagogique d’accompagnement à l’apprentissage de la **MEDOT** (méthode d’élaboration d’une décision opérationnelle tactique), niveaux 3 et 4 (brigade – GTIA), pour les stagiaires de l’**ESORSEM** et de l’**EEM**.

Outil pédagogique : il ne se substitue pas aux documents doctrinaux en vigueur.

## Utilisation

- **Hors ligne / Intradef** : copier `index.html` **et le dossier `videos/`** côte à côte sur le poste, puis ouvrir `index.html` dans le navigateur. Sans le dossier `videos/`, l’outil fonctionne mais les vidéos de cours affichent « Vidéo indisponible ».
- **En ligne** : https://jef1234567.github.io/maisdot/ (GitHub Pages, branche `main`).
- **Appli sur téléphone ou PC** : depuis le site, menu du navigateur → « Installer l’application » (Chrome, Edge) ou « Sur l’écran d’accueil » (Safari). L’appli s’ouvre en plein écran et fonctionne hors ligne ; les vidéos restent lues en ligne (non stockées).

Chaque étape se travaille en trois onglets :

1. **Comprendre** : la vidéo de cours de l’étape (quand elle existe), le but, la question directrice, les conclusions attendues, les points de vigilance et le canevas de réunion.
2. **S’entraîner** : un quiz corrigé. À partir de 70 %, l’étape est cochée comme validée. La navigation reste libre.
3. **Appliquer** : les gabarits à remplir. Les TCIDR et la frise sont consolidés dans un onglet dédié, avec des graphiques.

Le bouton **« Exemple VIENNE »** affiche le thème d’exercice VIENNE (version originale du dossier, brigade étudiée : 33(AZ)BB) dans tous les gabarits. Les faits viennent du dossier (OPORD n° 1 de la 3(AZ)DB et annexes) ; les analyses du chef de brigade sont des propositions marquées « (à valider) » ; « PM » signale une donnée absente du dossier. Il ne touche pas aux saisies du stagiaire. Les textes affichés de l’exemple sont traduits ; les valeurs préremplies dans les champs restent en français.

**Langues** : bouton ⚙ (Paramètres) en haut de page → français, anglais, italien, espagnol, arabe (de droite à gauche) ou allemand. Le français est la langue source ; les traductions (`src/i18n/<langue>.json`, texte français exact → traduction) sont appliquées à l’affichage, les travaux enregistrés ne changent pas. Les vidéos restent en français. Traduction en cours de relecture.

Les saisies sont enregistrées dans le navigateur (localStorage). Trois exports sont proposés : Word, copie dans le presse-papiers et sauvegarde .json (qu’on peut ensuite reprendre).

## MaisDot Classroom

Déclinaison pour un groupe (30 élèves au plus, un professeur) : `classroom-eleve.html` (fichier personnel, sans le corrigé VIENNE) et `classroom-professeur.html` (réception, contrôle et correction acquis / non acquis des envois .json, retour signé à l’élève, synthèse du groupe). Mode d’emploi : `docs/CLASSROOM.md`.

## Structure

```
index.html      fichier livré (généré, ne pas éditer à la main)
src/app.html    page source (HTML, CSS, JS, contenu doctrinal dans le tableau M)
src/demo.js     exemple VIENNE – 33(AZ)BB (phase préalable, phase 1)
src/p2.js       phase 2 : modules, quiz et exemple VIENNE (suite)
src/normes.js   module « Normes et délais » : fiche par rubriques, calculateur de délais (report dans la frise), rapport de forces, quiz
src/conduite.js rubrique « Appropriation et conduite » (hors cycle MEDOT) : mission brief, back brief, rehearsal, point de situation, APPSIT (aide nouvel OPO / FRAGO), rôles au sein du CO de GTIA ; examen blanc dédié
src/i18n.js     changement de langue (Paramètres), traduction à l’affichage, arabe RTL
src/i18n/       dictionnaires en, it, es, ar, de (texte français → traduction)
docs/           spécification, format des cas, exemple de cas
tests/          tests automatisés (Playwright)
src/logo.webp   insigne ESORSEM
videos/         14 vidéos de cours (MP4 H.264 720p), associées aux étapes par la table VID de src/app.html
manifest.webmanifest, sw.js, icons/   installation de l’appli (PWA)
src/classroom.js MaisDot Classroom (versions élève et professeur)
build.py        assemble index.html, classroom-eleve.html (corrigé VIENNE retiré) et classroom-professeur.html
```

Pour reconstruire : `python3 build.py`

## Feuille de route

- [x] Livraison 1 : vocabulaire, phase préalable, phase 1 et ses réunions
- [x] Navigation libre, exemple (fictif, remplacé par VIENNE), graphiques, accessibilité smartphone et PC
- [x] v2.0 : phase 2 (ME, MA, manœuvres fonctionnelles, comparaison pondérée, confrontation MA-ME, finalisation), réunion de décision, plan de manœuvre ; matrices de synchronisation (Gantt), examen blanc, fiches réflexes, recherche, chargeur et créateur de cas (instructeur), export en ligne ; audits fond / pédagogie / forme-accessibilité ; tests automatisés (`python3 tests/test_app.py`)
- [x] v2.1 : compléments (sections « Compléments », points de vigilance, 49 questions, 7 cartes de vocabulaire, 13 sigles, repères de délais, MRO)
- [x] v2.2 : interface et contenu traduits en anglais, italien, espagnol, arabe et allemand (menu Paramètres)
- [x] v2.3 : module « Normes et délais » (Outils) : normes d’engagement et délais par rubriques, calculateur de délais avec report dans la frise, contrôle du rapport de forces, 25 questions (3 dans l’examen blanc), liens depuis les étapes concernées
- [ ] Relecture des traductions par des stagiaires étrangers ; vidéos traduites
- [ ] Cas concret « thème Vienne » : à charger via « Charger un cas » (format : `docs/FORMAT_CAS.md`)
- [ ] Charte EEM (en plus de la charte ESORSEM)
