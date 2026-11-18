# Format d’un fichier de cas (chargeur instructeur)

L’instructeur charge un cas depuis l’accueil : bouton **« Charger un cas (instructeur) »**, fichier `.json` encodé en UTF-8.
Le cas est mémorisé dans le navigateur (clé `localStorage` `medot-esorsem-cas-v1`, distincte des travaux du stagiaire) jusqu’à ce qu’on clique sur **« Retirer le cas »**. Si le stockage local est indisponible (certains navigateurs, version en ligne), le cas reste actif jusqu’à la fermeture de la page.

Une fois le cas chargé :
- un bandeau rappelle le titre et le résumé, avec un bouton **« Lire la situation »** ;
- dans l’onglet **Appliquer** de chaque étape ayant un corrigé, le bouton **« Voir le corrigé »** affiche, sous les gabarits et en lecture seule, les valeurs corrigées et le commentaire de l’instructeur. Les saisies du stagiaire ne sont jamais modifiées.

## Structure

```json
{
  "titre": "Titre du cas (obligatoire)",
  "resume": "Résumé en une ou deux phrases (facultatif, affiché dans le bandeau)",
  "situation": "Texte long de la situation (facultatif). Une ligne vide sépare deux paragraphes.",
  "corrige": {
    "<id du module>": {
      "texte": "Commentaire de l’instructeur (facultatif)",
      "v":   { "<id du bloc fields>": { "<clé du champ>": "valeur", "…": "…" } },
      "tab": { "<id du tableau>": [ { "<clé de colonne>": "valeur", "…": "…" } ] },
      "tcidr": [ { "y": "Tâche", "fo": "Interarmes", "l": "Libellé" } ],
      "frise": [ { "g": "J 06h00", "e": "Événement" } ]
    }
  }
}
```

Seuls `titre` et `corrige` sont obligatoires. Dans chaque module, toutes les rubriques sont facultatives. Les identifiants de module inconnus sont signalés au chargement puis ignorés.

`v`, `tab`, `tcidr` et `frise` reprennent **exactement** le modèle de données de l’application (celui des sauvegardes `.json` du stagiaire, objets `S.v` et `S.tab`). Le plus simple pour produire un corrigé : remplir les gabarits dans l’application, faire « Sauvegarder (fichier .json) », puis recopier les objets utiles sous l’identifiant de chaque module.

## Identifiants

| Module (`id`) | Blocs `v` (fields) | Tableaux `tab` |
|---|---|---|
| `vocab` | – | `fdc` |
| `prealable` | `ctxla` (et `tiers` : `r`, `c`, `m`) | `ctx` |
| `p1e1` | `mis`, `misla` | `taches` |
| `oi` | `oiv` | – |
| `p1e2` | `terz` | `ter`, `pc` |
| `p1e3` | `eni` | `seqeni` |
| `p1e4` | `amila` | `seqami` |
| `p1e5` | `confz` | `conf` |
| `syn` | `synv` | – |
| `p2e1` … `p2e6`, `dec`, `pm` | selon `src/p2.js` | `sync_<id>` (matrices), `cmp`, `mame`, `pdm` |

Clés des champs et des colonnes : voir le tableau `M` de `src/app.html` (propriétés `apply`) et `docs/SPEC_P2.md` pour la phase 2. Les champs ou tableaux qui ne correspondent à aucun gabarit de l’étape sont tout de même affichés, avec leur clé brute comme intitulé.

GDH : format « J 06h00 », « J+1 02h00 », « J-1 18h00 » (tri chronologique automatique de la frise).

## Exemple

`docs/exemple_cas_valdor.json` : situation fictive VALDOR, corrigés des étapes 1 (analyse de la mission), 2 (terrain ami) et 5 (confrontation des séquences) de la phase 1.
