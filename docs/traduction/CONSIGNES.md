# Traduction de MaisDot (outil d'apprentissage de la MEDOT, méthode tactique française)

Public : officiers stagiaires étrangers d'écoles d'état-major. Registre : militaire, précis, sobre. Le tutoiement français
(« Rédige… », « ta mission ») devient l'impératif / la forme d'adresse directe usuelle de la langue cible (EN « you », DE « du »
accepté ou « Sie » cohérent sur tout l'outil, IT « tu », ES « tú », AR forme d'adresse directe neutre).

## Entrée / sortie
- Entrée : `/home/claude/i18n_work/src/part_01.json` … `part_16.json` — objet `{"id": "texte français"}`.
- Sortie : `/home/claude/i18n_work/<langue>/part_NN.json` — objet `{"id": "traduction"}` avec **exactement les mêmes id**.
- Traite les lots dans l'ordre. Écris chaque lot dès qu'il est traduit, puis vérifie-le :
  `python3 -c "import json,sys;a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]));assert a.keys()==b.keys();print('ok',len(b))" /home/claude/i18n_work/src/part_NN.json /home/claude/i18n_work/<langue>/part_NN.json`
- Si un fichier de sortie existe déjà et passe la vérification, ne le refais pas (reprise possible).
- Écris le JSON avec un petit script Python (json.dump, ensure_ascii=False) si tu crains les erreurs d'échappement.

## Règles
1. Conserve à l'identique : `{n}` (nombre inséré à l'affichage), les symboles ★ ▶ → ← ✓ ✗ • · – …, la ponctuation
   de début et de fin, les espaces de début/fin, les GDH (« J+1 04h00 »), les références de pages (« p. 23 » → abréviation usuelle de page).
2. Sigles français de la méthode : **ne pas traduire** (MEDOT, MA, ME, MAG, TCIDR, TCIDR-F, PS, OPO, BIA, GTIA, SGTIA, EEM,
   ESORSEM, PFT, BSM, MRO, PREO, PRR, PEMA, CTE, ZOP, ZOR, ZOAR, ZEF, ZIO, ZIP, ZDO, GPC, APPSIT, PD, ACIm, COPS, CCO, MANFUT…).
   Les sigles OTAN (FRAGO, WINGO, OPLAN, COPD, CCIR, PIR, FFIR, EEFI, HNIR, FOC, NAI, TAI, ROE) restent tels quels.
   Dans les tableaux de sigles, la définition est traduite, le sigle non.
3. Noms propres de l'exemple fictif (Valdor, Morlac, Vernes, Sarve, Saint-Ivre…) : inchangés.
4. Terminologie : équivalent OTAN dans la langue cible quand il existe ; sinon traduction littérale claire.
   Pivot anglais imposé (adapte-le dans ta langue et **garde le même terme partout**) :
   effet majeur = decisive effect · but à atteindre = purpose · action décisive = decisive action · moment clé = key moment ·
   zone clé = key area · point clé = key point · mode d'action ami / ennemi = friendly / enemy course of action ·
   mode d'action générique = generic course of action · conclusion tactique = tactical conclusion ·
   tâche spécifiée / induite = specified / implied task · contrainte = constraint · impératif = imperative · demande = request ·
   besoin en renseignement = intelligence requirement · présupposition = assumption · séquence = sequence ·
   réunion d'orientation préalable / initiale = preliminary / initial guidance briefing · réunion de synthèse = synthesis briefing ·
   réunion de décision = decision briefing · comparaison = comparison · confrontation = confrontation ·
   plan de manœuvre = manoeuvre plan · plan simplifié = simplified plan · ordre d'opération = operation order ·
   idée de manœuvre = scheme of manoeuvre · groupe plurifonctionnel de conception = multifunctional planning group ·
   fonction opérationnelle = operational function · liberté d'action = freedom of action · en mesure de = be prepared to ·
   matrice de synchronisation = synchronisation matrix · point de décision = decision point · centre de gravité = centre of gravity ·
   gestion de l'espace de bataille = battlespace management · rapport de force = force ratio · ennemi global / futur / initial /
   ultérieur = overall / future / initial / subsequent enemy · frise chronologique = timeline · règle du tiers-temps = one-third rule ·
   combat au contact = close combat · champs immatériels = non-physical fields · environnement humain des opérations = human
   environment of operations · modelage = shaping · phase préalable = preliminary phase · analyse-synthèse = analysis-synthesis ·
   séquence amie / ennemie = friendly / enemy sequence · étape = step · onglet = tab.
5. Textes très courts ou fragments (morceaux de phrase coupés par la mise en page) : traduis le fragment tel quel, sans compléter.
6. Ne résume pas, n'ajoute rien, ne commente pas. Une traduction par id.
7. À la fin, écris `/home/claude/i18n_work/<langue>/GLOSSAIRE.md` : les termes doctrinaux retenus dans ta langue (FR → langue)
   et les choix douteux à faire relire.
