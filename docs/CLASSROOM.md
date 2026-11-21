# MaisDot Classroom – mode d’emploi

Deux fichiers, générés par `python3 build.py` à partir des mêmes sources que MaisDot :

| Fichier | Pour qui | Contenu |
|---|---|---|
| `classroom-eleve.html` | chaque élève (fichier personnel) | tout MaisDot **sans le corrigé VIENNE** (l’énoncé reste : bouton « Sujet VIENNE ») ; envoi des travaux ; import de la correction |
| `classroom-professeur.html` | le professeur du groupe | tout MaisDot avec le corrigé VIENNE ; groupe de 30 élèves au plus ; réception, contrôle et correction des envois ; synthèse du groupe |

Les deux fonctionnent hors ligne (Intradef) : copier le fichier et le dossier `videos/` côte à côte, puis l’ouvrir dans le navigateur.
Rien n’est transmis en ligne : les échanges passent par des fichiers `.json` joints aux messages.

## Déroulé

1. **Professeur** – « Mon groupe » → nom du groupe → « Créer le groupe ». Un **code du groupe** (5 blocs de 4 caractères) s’affiche : le donner aux élèves.
2. **Élève** – à la première ouverture : grade, nom, prénom, numéro matricule et code du groupe. L’identité est ensuite fixée (la changer impose d’effacer les travaux).
3. **Élève** – travaille au fil des séances (gabarits, tests, examens blancs), puis « Envoyer mes travaux » → « Préparer mon envoi (.json) » et joint le fichier au message adressé au professeur. L’envoi contient tout : gabarits, TCIDR, frise, résultats des tests et de chaque examen blanc. Il peut envoyer plusieurs fois ; seul le dernier envoi compte.
4. **Professeur** – « Mon groupe » → dépose les fichiers reçus (plusieurs à la fois). Le tableau du groupe montre pour chaque élève le dernier envoi, les étapes remplies, les tests validés, le meilleur examen, le contrôle et l’état de la correction.
5. **Professeur** – « Corriger » : pour chaque étape travaillée, le travail de l’élève à côté du corrigé VIENNE, le score du test, une suggestion automatique (tests et examens), puis **acquis / non acquis** et une explication. « Exporter la correction (.json) » produit le fichier à renvoyer à l’élève.
6. **Élève** – « Envoyer mes travaux » → « Importer ma correction » : page « Ma correction » (points non maîtrisés, avec boutons « Revoir l’étape », « Refaire le test », « Reprendre mes gabarits »), bandeau de correction sur chaque étape concernée, repère ✗ dans le menu.
7. **Professeur** – « Synthèse du groupe » : étapes classées de la moins maîtrisée à la plus maîtrisée, élèves en difficulté ; export Word. Le tableau du groupe s’exporte en .csv (Excel).

## Contrôles (anti-fraude)

- Chaque envoi, correction et sauvegarde est **signé** (HMAC-SHA256) avec le code du groupe : un fichier modifié à la main ou venu d’un autre groupe est signalé (« Signature invalide ») ou refusé.
- Une correction ne s’importe que chez l’élève dont elle porte le matricule ; une sauvegarde élève ne se reprend que sur le même matricule.
- Numéro d’envoi croissant ; identité différente pour un même matricule signalée.
- **Travaux très proches** : le professeur est alerté quand deux élèves ont rendu des textes longs identiques.
- Journal de saisie joint à l’envoi : nombre de modifications et de collages par bloc, affiché au professeur.

Limite : le code du groupe est connu des élèves ; ces contrôles détectent les manipulations courantes, ils ne rendent pas la fraude impossible.

## Données

- Élève : navigateur du poste (localStorage) + fichiers envoyés. Bouton « Sauvegarder » pour changer de poste.
- Professeur : navigateur du poste (IndexedDB). **Sauvegarder le groupe** régulièrement : la sauvegarde contient le code du groupe, à garder pour soi.

## Tests

`python3 tests/test_classroom.py` : scénario complet professeur → 2 élèves → envoi modifié → correction → retour, en PC et smartphone, et contrôle de l’absence du corrigé dans la version élève.
