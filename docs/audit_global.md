# Audit global du fond et de la forme – 20/11/2026

Audit fait sur l’outil entier : 82 modules et 948 questions, dans les 6 langues, sur PC (1366 × 768) et sur mobile (390 × 844).

## Méthode

- **Données :** extraction du tableau M après assemblage. Contrôles automatiques :
  - index des réponses, options vides ou en double, explications manquantes ;
  - questions identiques d’un module à l’autre ;
  - renvois « Voir : » et boutons d’étape, table des vidéos ;
  - réserves de questions de chaque examen blanc.
- **Rédaction :** recherche des références de publications, des numéros de page et des noms de sources (interdits depuis le 17/11). Contrôle typographique sur les 10 012 textes affichés. Recherche des sigles employés mais absents du lexique.
- **Affichage :** parcours de toutes les vues (3 onglets par module, plus l’onglet Appliquer avec l’exemple VIENNE). Recherche des erreurs JavaScript et des débordements horizontaux sur mobile.
- **Traduction :** pour chaque texte affiché, recherche de sa traduction dans les 5 dictionnaires.
- **Accessibilité :** axe-core 4 (règles WCAG 2.0 à 2.2, niveaux A et AA) sur toutes les vues, en PC et en mobile.
- **Examens blancs :** 30 tirages par examen, pour vérifier qu’aucune question n’y figure deux fois.

## Constats et corrections

| Domaine | Constat | Correction |
|---|---|---|
| Fond | La question « Où figurent les ME dans l’OPO ? » de l’étape 1 de la phase 2 donnait une réponse fausse (§ 1.a.iii, qui correspond à l’ennemi initial). Son explication citait un « § 2.23 » du PS, lui aussi faux. Elle doublait en outre la même question de la phase 3, dont la réponse est juste. | La question porte désormais sur le plan simplifié : la réponse est le § 25, Modes d’action ennemis. L’explication renvoie au § 1.A.V de l’OPO. |
| Fond | Il restait des références de publications : PFT 5.1, MFT 5.2.1 et RFT 3.2.1, dans 7 textes (accueil, critères interarmes, réunion de décision, définition de l’effet majeur). | Elles sont remplacées par « la méthode » ou par « définition en vigueur ». |
| Quiz | Dans 45 % des questions, la bonne réponse était la plus longue des quatre (430 sur 948). Un stagiaire pouvait la deviner à la longueur. | Les distracteurs de 198 questions ont été réécrits. Ils font désormais entre 75 % et 115 % de la longueur de la bonne réponse et sont vérifiés comme faux. La bonne réponse n’est plus la plus longue que dans 30 % des cas, pour 25 % attendus au hasard. Les questions sur les symboles ne sont pas touchées. |
| Examens | 3 questions sont posées dans deux modules : rédaction des paragraphes logistiques, commandement d’un secteur de franchissement, délai de décontamination. Elles pouvaient sortir deux fois dans le même examen. | Ces questions jumelles sont détectées automatiquement : une seule sort par examen. Sur 30 tirages par examen, aucun doublon. |
| Lexique | 45 sigles étaient employés dans l’outil sans figurer dans le lexique, dont NRBC (employé 136 fois). Les autres : ENI/AMI, RAPFOR, ROE, VAB, PFM, LRU, MEPAC, LCC, BOI, ASA, ROIM, MGRS, SICS, ATLAS, MARTHA, SAER, NEB, PC TAC, PAC, KLE, SITACREF… | Les 45 sigles sont ajoutés, avec leur définition traduite dans les 5 langues. |
| Traduction | Environ 380 libellés n’avaient pas de traduction. Il s’agissait des intitulés « colonne, ligne n » de 5 tableaux de la conduite (lus par les lecteurs d’écran), des options de quiz de la forme « La FLOT » ou « L’OPCOM », et de « Terrain » et « Manœuvres » dans le schéma du cycle. | Les traductions sont ajoutées. |
| Traduction | L’exemple VIENNE n’était pas traduit. | Les textes affichés de l’exemple VIENNE sont traduits : la situation et les cellules des tableaux du corrigé. Les valeurs préremplies dans les champs restent en français. |
| Accessibilité | Les nœuds du schéma du cycle avaient un nom accessible différent du texte affiché (WCAG 2.5.3). | Le nom accessible reprend désormais le texte affiché, traduit. axe-core ne relève plus aucune violation. |
| Divers | Le lien GitHub Pages du README était écrit avec une casse erronée (« MaisDot »). | Il est corrigé en « maisdot ». |

## Ce qui est conforme

- Aucune erreur JavaScript, sur aucune vue.
- Aucun débordement horizontal à 390 px.
- Aucun renvoi cassé.
- Toutes les réserves des examens sont suffisantes.
- La typographie française est propre : aucune espace manquante avant ; : ? !, aucune apostrophe droite, aucun « oe » non ligaturé dans les textes affichés.
- Les 48 tests passent.

## Points laissés à JF

- **Relecture des distracteurs réécrits.** Les agents de relecture ont signalé 9 questions où le distracteur réécrit peut prêter à discussion : f3_ci3d n° 3, ac_ir n° 3, or_opo n° 6 et n° 10, p1e1 n° 10, f3_art n° 7, gn_cied n° 9, ms_gt1 n° 9, gn_fb n° 9. Pour gn_fb n° 9, le distracteur « colonel adjoint » est un piège volontaire : c’est la zone de franchissement, et non le secteur, qui est à ses ordres. Les distracteurs des modules de méthode (vocab, phases 1 et 2) n’ont pas d’équivalent mot pour mot dans la base doctrinale. Ils ont été contrôlés par rapport aux explications de l’outil.
- **Terminologie des traductions.** C’est la même liste qu’avant, dans la section « Lot … » des glossaires. Il s’y ajoute les choix signalés pour cet audit (section « Audit global »). Ces points ont été tranchés le 20/11 : voir la section « Décisions du 20/11 » de chaque glossaire (34 harmonisations de termes, soit 244 chaînes modifiées dans les 5 dictionnaires).
- **Contradictions internes à la BIA à soumettre à l’EEM.** La liste n’a pas changé (document de passation).
