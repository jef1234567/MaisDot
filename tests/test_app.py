#!/usr/bin/env python3
"""Tests fonctionnels automatisés de la webapp MaisDot (index.html, monofichier).

Playwright (sync API), Chromium, chargement en file://.
Chaque scénario est joué en 1366x768 (PC) et 390x844 (smartphone), dans un
contexte de navigateur neuf (localStorage vide au départ).

Exécution : python3 tests/test_app.py   (code retour 0 si tout est OK)
"""
import json
import pathlib
import sys
import tempfile
import time
import traceback

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = (ROOT / "index.html").as_uri()
CAS_FILE = ROOT / "docs" / "exemple_cas_valdor.json"
KEY = "medot-esorsem-v1"
CAS_KEY = "medot-esorsem-cas-v1"
EX_KEY = "medot-esorsem-exam-v1"
VIEWPORTS = {"PC 1366x768": (1366, 768), "Mobile 390x844": (390, 844)}
TMP = pathlib.Path(tempfile.mkdtemp(prefix="maisdot_tests_"))

RESULTS = []  # (test, viewport, ok, detail)


class Check(Exception):
    pass


def check(cond, msg):
    if not cond:
        raise Check(msg)


# ---------------------------------------------------------------- outils
class App:
    """Une page + son contexte, avec collecte des erreurs JS / console."""

    def __init__(self, browser, vp, init_script=None, mobile=False):
        w, h = vp
        self.mobile = w < 821
        self.ctx = browser.new_context(viewport={"width": w, "height": h},
                                       accept_downloads=True,
                                       has_touch=self.mobile, is_mobile=self.mobile)
        if init_script:
            self.ctx.add_init_script(init_script)
        self.page = self.ctx.new_page()
        self.page.set_default_timeout(6000)
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(f"pageerror: {e}"))
        self.page.on("console", lambda m: m.type == "error" and self.errors.append(f"console.error: {m.text}"))

    def open(self, hash_=""):
        self.page.goto(URL + (("#" + hash_) if hash_ else ""))
        # en mobile, le tiroir fermé est masqué (visibility:hidden) : on attend la présence, pas la visibilité
        self.page.wait_for_selector("#navList a", state="attached")
        return self

    def reload(self):
        self.page.reload()
        self.page.wait_for_selector("#navList a", state="attached")

    def js(self, expr, arg=None):
        return self.page.evaluate(expr, arg) if arg is not None else self.page.evaluate(expr)

    def go(self, mid, tab="c"):
        self.js(f"go('{mid}','{tab}')")

    def open_nav(self):
        if self.mobile and self.js("!document.getElementById('nav').classList.contains('open')"):
            self.page.click("#menuBtn")
            self.page.wait_for_timeout(250)  # transition .2s

    def nav_click(self, mid):
        self.open_nav()
        # menu à groupes repliables : déplier (comme un utilisateur) les groupes fermés qui contiennent le lien
        ks = self.js("id=>{const r=[];let d=document.querySelector(`#navList a[data-id='${id}']`).parentElement.closest('details');while(d){if(!d.open)r.unshift(d.dataset.k);d=d.parentElement.closest('details');}return r}", mid)
        for k in ks:
            self.page.locator(f"#navList details[data-k=\"{k}\"] > summary").first.click()
        self.page.click(f"#navList a[data-id='{mid}']")

    def stored(self):
        raw = self.js(f"localStorage.getItem('{KEY}')")
        return json.loads(raw) if raw else None

    def no_errors(self):
        check(not self.errors, "Erreurs JS : " + " | ".join(self.errors[:5]))

    def close(self):
        self.ctx.close()


def correct_text(app, mid, qtext):
    return app.js("""([mid,q])=>{const m=M.find(x=>x.id===mid);const z=m.quiz.find(x=>x.q===q);
                     return z?z.o[z.a]:null}""", [mid, qtext])


def answer_quiz(app, mid, right=True):
    """Répond à toutes les questions du quiz de mid (juste ou faux)."""
    app.go(mid, "e")
    n = app.page.locator("#main .qz").count()
    for i in range(n):
        card = app.page.locator("#main .qz").nth(i)
        q = card.locator(".qq").inner_text().split(". ", 1)[1]
        good = correct_text(app, mid, q)
        check(good is not None, f"question introuvable dans M : {q[:60]}")
        btns = card.locator("button.o")
        texts = btns.all_inner_texts()
        idx = texts.index(good) if right else next(k for k, t in enumerate(texts) if t != good)
        btns.nth(idx).click()
    return n


def fill_cell(app, tid, i, k, value):
    app.page.locator(f"[oninput^=\"setc('{tid}',{i},'{k}',\"]").fill(value)


def select_cell(app, tid, i, k, label):
    app.page.locator(f"[onchange^=\"setc('{tid}',{i},'{k}',\"]").select_option(label=label)


def rows_of(app, tid, k):
    return app.page.locator(f"[oninput^=\"setc('{tid}',\"][oninput*=\",'{k}',\"]").count()


def confirm_modal(app, label):
    app.page.locator("#modal.on button", has_text=label).click()


# ---------------------------------------------------------------- scénarios
def t_chargement(b, vp):
    a = App(b, vp).open()
    check(a.page.title() != "", "titre vide")
    check(a.page.locator("#main h2").count() >= 1, "accueil non rendu")
    n_nav = a.page.locator("#navList a").count()
    check(n_nav >= 20, f"menu incomplet ({n_nav} liens)")
    check(a.js("M.some(m=>m.id==='p2e1')&&!M.some(m=>m.soon)"), "intégration P2 absente (modules « à venir » encore là)")
    prog = a.page.locator("#progTxt").inner_text()
    check(prog.startswith("0 / "), f"progression initiale : {prog}")
    if a.mobile:
        check(a.page.locator("#menuBtn").is_visible(), "bouton menu invisible en mobile")
        check(a.page.locator("#demoSw").is_visible(), "#demoSw invisible en mobile")
    a.page.wait_for_timeout(300)
    a.no_errors()
    a.close()
    return f"{n_nav} liens de menu, aucune erreur console"


def t_navigation(b, vp):
    a = App(b, vp).open()
    mods = a.js("M.map(m=>({id:m.id,title:m.title,kind:m.kind||'',nq:(m.quiz||[]).length,na:(m.apply||[]).length}))")
    n_tabs = 0
    for m in mods:
        a.nav_click(m["id"])
        a.page.wait_for_function("id=>cur===id", arg=m["id"])
        check(a.js("document.getElementById('nav').classList.contains('open')") is False or not a.mobile,
              f"{m['id']} : le menu mobile ne se referme pas")
        check(a.page.locator(f"#navList a[data-id='{m['id']}'][aria-current='page']").count() == 1,
              f"{m['id']} : aria-current absent")
        if m["kind"]:
            check(len(a.page.locator("#main").inner_text()) > 20, f"{m['id']} vide")
            continue
        h2 = a.page.locator("#main h2").first.inner_text()
        check(m["title"] in h2, f"{m['id']} : titre « {h2} »")
        for k, tab in enumerate(["1 · Comprendre", "2 · S’entraîner", "3 · Appliquer"]):
            a.page.locator("#main .tabs button", has_text=tab).click()
            sel = a.page.locator("#main .tabs button[aria-current='step']").inner_text()
            check(sel == tab, f"{m['id']} : onglet actif « {sel} » au lieu de « {tab} »")
            body = a.page.locator("#main").inner_text()
            check(len(body) > 80, f"{m['id']}/{tab} : contenu vide")
            if k == 1:
                nq = a.page.locator("#main .qz").count()
                check(nq == m["nq"], f"{m['id']} : {nq} questions affichées / {m['nq']}")
            if k == 2 and m["na"]:
                check(a.page.locator("#main .card, #main p").count() > 0, f"{m['id']} : Appliquer vide")
            n_tabs += 1
    # navigation par l'ancre (hash)
    a.page.goto(URL + "#p2e4")
    a.page.wait_for_function("cur==='p2e4'")
    a.no_errors()
    a.close()
    return f"{len(mods)} modules, {n_tabs} onglets parcourus"


def t_quiz(b, vp):
    a = App(b, vp).open()
    total = a.js("steps.length")
    n = answer_quiz(a, "p1e1", right=True)
    sc = a.page.locator("#main .score").inner_text()
    check("Étape validée" in sc and sc.startswith(f"{n} / {n}"), f"score : {sc}")
    check(a.page.locator("#progTxt").inner_text() == f"1 / {total} étapes validées", "progression non mise à jour")
    check(a.page.locator("#navList a[data-id='p1e1'] .st.ok").count() == 1, "coche ✓ absente du menu")
    check(a.js("document.getElementById('progRole').getAttribute('aria-valuenow')") == "1", "aria-valuenow")
    st = a.stored()
    check(st and st["quiz"]["p1e1"]["best"] == 1, "score non enregistré")
    # échec sur une autre étape : pas de validation
    answer_quiz(a, "p1e2", right=False)
    check("Relis la synthèse" in a.page.locator("#main .score").inner_text(), "échec non signalé")
    check(a.page.locator("#progTxt").inner_text().startswith("1 /"), "étape échouée comptée validée")
    a.reload()
    check(a.page.locator("#progTxt").inner_text().startswith("1 /"), "progression perdue au rechargement")
    a.no_errors()
    a.close()
    return f"{n}/{n} sur p1e1, progression 1/{total} persistée"


def t_persistance(b, vp):
    a = App(b, vp).open()
    a.go("p1e1", "a")
    a.page.fill("#f_mis_msup", "MISSION_TEST")
    a.page.fill("#f_mis_bat", "Afin de tester")
    check("Forme conforme" in a.page.locator("#f_mis_bat >> xpath=..").inner_text(), "contrôle « Afin de » inactif")
    fill_cell(a, "taches", 0, "t", "TACHE_TEST")
    select_cell(a, "taches", 0, "n", "Induite")
    a.page.click("button:has-text('+ Ajouter une ligne')[onclick=\"addRow('taches')\"]")
    fill_cell(a, "taches", 1, "t", "TACHE_2")
    a.page.click("button:has-text('+ Ajouter un TCIDR')")
    a.page.locator("textarea[aria-label^='Libellé, ligne']").last.fill("TCIDR_TEST")
    a.page.locator("select[aria-label^='Type, ligne']").last.select_option("Contrainte")
    a.page.click("button:has-text('+ Ajouter un repère')")
    a.page.locator("input[aria-label^='GDH, ligne']").last.fill("J+1 06h00")
    a.page.locator("textarea[aria-label^='Événement, ligne']").last.fill("FRISE_TEST")
    a.reload()
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_msup") == "MISSION_TEST", "champ non persisté")
    check(a.page.locator("[oninput^=\"setc('taches',0,'t',\"]").input_value() == "TACHE_TEST", "tableau non persisté")
    check(a.page.locator("[onchange^=\"setc('taches',0,'n',\"]").input_value() == "Induite", "select de tableau non persisté")
    check(rows_of(a, "taches", "t") == 2, "ligne ajoutée perdue")
    check(a.page.locator("textarea[aria-label^='Libellé, ligne']").last.input_value() == "TCIDR_TEST", "TCIDR non persisté")
    check(a.page.locator("input[aria-label^='GDH, ligne']").last.input_value() == "J+1 06h00", "frise non persistée")
    st = a.stored()
    check(st["tcidr"][-1]["y"] == "Contrainte" and st["tcidr"][-1]["src"] == "p1e1", "TCIDR mal stocké")
    a.go("recap")
    check("FRISE_TEST" in a.page.locator("#main").inner_text(), "frise absente du récapitulatif")
    a.no_errors()
    a.close()
    return "fields, table (+ligne, select), TCIDR, frise relus après rechargement"


def t_demo(b, vp):
    a = App(b, vp).open()
    a.go("p1e1", "a")
    a.page.fill("#f_mis_bat", "Afin de SAISIE_USER")
    demo_val = a.js("DEMO.v.mis.bat")
    a.page.locator("#demoSw").check()
    check(a.page.locator("#demoBanner").is_visible(), "bandeau démo absent")
    check(a.page.input_value("#f_mis_bat") == demo_val, "exemple non affiché")
    a.page.fill("#f_mis_bat", "MODIF_EN_DEMO")  # ne doit pas être enregistrée
    a.go("p2e4", "a")
    check(a.page.locator("[data-chart='cmp'] .tot").count() == 2, "graphique cmp de démo absent")
    st = a.stored()
    check(st["v"]["mis"]["bat"] == "Afin de SAISIE_USER", "localStorage écrasé en mode démo")
    check("MODIF_EN_DEMO" not in json.dumps(st) and demo_val not in json.dumps(st), "données démo enregistrées")
    a.page.locator("#demoBanner button", has_text="Revenir à mes travaux").click()
    check(not a.page.locator("#demoSw").is_checked(), "case démo encore cochée")
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_bat") == "Afin de SAISIE_USER", "saisie utilisateur perdue après démo")
    a.reload()
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_bat") == "Afin de SAISIE_USER", "saisie perdue après rechargement")
    check(not a.page.locator("#demoSw").is_checked(), "démo active au rechargement")
    a.no_errors()
    a.close()
    return "saisies intactes (mémoire et localStorage)"


def t_sync(b, vp):
    a = App(b, vp).open()
    a.go("p2e1", "a")
    tid = "sync_me1"
    check(rows_of(a, tid, "u") == 1, "ligne initiale absente")
    chart = a.page.locator("[data-chart='sync:me1']")
    # Gantt replié tant que la matrice est vide : text_content (inner_text est vide si non rendu)
    check("Remplis la matrice" in chart.text_content(), "message vide du Gantt")
    data = [("SGTIA 1", "Freine", "Contact", "J 06h00", "J 12h00", "", ""),
            ("Génie", "Obstacle D17", "Appui (génie, feux, appui électronique)", "J-1 18h00", "J 04h00", "", "PD1"),
            ("A SUPPRIMER", "x", "Soutien", "J+1 02h00", "J+1 04h00", "", "")]
    for i, (u, ac, fo, d, f, ph, pd) in enumerate(data):
        if i:
            a.page.click(f"button[onclick=\"addRow('{tid}')\"]")
        check(rows_of(a, tid, "u") == i + 1, f"ajout de ligne {i+1}")
        fill_cell(a, tid, i, "u", u)
        fill_cell(a, tid, i, "a", ac)
        select_cell(a, tid, i, "fo", fo)
        fill_cell(a, tid, i, "d", d)
        fill_cell(a, tid, i, "f", f)
        if pd:
            fill_cell(a, tid, i, "pd", pd)
    check(chart.locator(".bar").count() == 3, f"{chart.locator('.bar').count()} barres / 3")
    check(chart.locator(".pd").count() == 1, "étoile du point de décision absente")
    labels = chart.locator(".gr[role=listitem] .lbl b").all_inner_texts()
    check(labels == ["Génie", "SGTIA 1", "A SUPPRIMER"], f"ordre du Gantt : {labels}")
    a.page.click(f"button[onclick=\"delRow('{tid}',2)\"]")
    check(rows_of(a, tid, "u") == 2, "suppression de ligne")
    check(a.page.locator("[data-chart='sync:me1'] .bar").count() == 2, "Gantt non rafraîchi après suppression")
    check(len(a.stored()["tab"][tid]) == 2, "suppression non enregistrée")
    # couleur de la barre = fonction opérationnelle
    col = a.js("getComputedStyle(document.querySelector(\"[data-chart='sync:me1'] .bar\")).backgroundColor")
    check(col == "rgb(194, 124, 14)", f"couleur FO génie : {col}")
    a.no_errors()
    a.close()
    return "3 lignes ajoutées, 1 supprimée, Gantt trié J-1→J→J+1, ★ PD"


def t_cmp(b, vp):
    a = App(b, vp).open()
    a.go("syn", "a")
    a.page.fill("#f_synv_crit", "Rapidité\nSûreté")
    a.go("p2e4", "a")
    check("Rapidité" in a.page.locator("#main .but").first.inner_text(), "critères du chef non rappelés")
    rows = [("Rapidité", "3", "+", "−"), ("Sûreté", "2", "=", "+"), ("Logistique", "1", "−", "+"), ("Supprimé", "3", "+", "+")]
    for i, (c, w, s1, s2) in enumerate(rows):
        if i:
            a.page.click("button[onclick=\"addRow('cmp')\"]")
        fill_cell(a, "cmp", i, "c", c)
        select_cell(a, "cmp", i, "w", w)
        select_cell(a, "cmp", i, "s1", s1)
        select_cell(a, "cmp", i, "s2", s2)
    ch = a.page.locator("[data-chart='cmp']")
    tots = ch.locator(".tot b:last-child").all_inner_texts()
    # attendu avec 4 lignes : MA1 = 3+0-1+3 = 5 ; MA2 = -3+2+1+3 = 3 ; max = 9
    check(tots == ["+5", "+3"], f"totaux 4 lignes : {tots}")
    check("−9 … +9" in ch.inner_text(), "échelle max incorrecte (attendu 9)")
    a.page.click("button[onclick=\"delRow('cmp',3)\"]")
    tots = a.page.locator("[data-chart='cmp'] .tot b:last-child").all_inner_texts()
    # attendu : MA1 = 3×1 + 2×0 + 1×(−1) = 2 ; MA2 = 3×(−1) + 2×1 + 1×1 = 0 ; max = 6
    check(tots == ["+2", "0"], f"totaux après suppression : {tots}")
    txt = a.page.locator("[data-chart='cmp']").inner_text()
    check("−6 … +6" in txt, "échelle après suppression")
    check("MA1 l’emporte (+2 contre 0)" in txt, "verdict incorrect")
    js = a.js("cmpTot(S.tab.cmp.filter(r=>r.c))")
    check(js == {"t1": 2, "t2": 0, "max": 6}, f"cmpTot : {js}")
    # égalité
    select_cell(a, "cmp", 2, "s1", "+")   # MA1 = 4
    select_cell(a, "cmp", 0, "s2", "+")   # MA2 = 6
    select_cell(a, "cmp", 1, "s1", "+")   # MA1 = 6
    check("Égalité" in a.page.locator("[data-chart='cmp']").inner_text(), "égalité non détectée")
    # moins ASCII accepté par cmpS
    check(a.js("cmpS('-')===-1&&cmpS('−')===-1&&cmpS('=')===0&&cmpS('+')===1"), "cmpS")
    # export Word reprend les totaux
    rep = a.js("buildReport()")
    check("MA1 = 6 ; MA2 = 6" in rep, "totaux absents de l'export")
    a.no_errors()
    a.close()
    return "Σ poids×note vérifié (+5/+3 puis +2/0, égalité 6/6, max 9→6)"


def t_mame(b, vp):
    a = App(b, vp).open()
    a.go("p2e5", "a")
    rows = [("MA1", "ME1", "op", "", "am", "PD1"), ("MA1", "ME2", "", "risque", "", ""),
            ("MA2", "ME1", "op", "risque", "", ""), ("MA2", "ME2", "x", "y", "", "")]
    for i, (ma, me, o, r, am, pd) in enumerate(rows):
        if i:
            a.page.click("button[onclick=\"addRow('mame')\"]")
        select_cell(a, "mame", i, "ma", ma)
        select_cell(a, "mame", i, "me", me)
        for k, v in (("o", o), ("r", r), ("am", am), ("pd", pd)):
            if v:
                fill_cell(a, "mame", i, k, v)
    a.page.click("button[onclick=\"delRow('mame',3)\"]")
    cells = a.page.locator("[data-chart='mame'] .mc")
    check(cells.count() == 4, f"{cells.count()} cellules / 4")
    cls = [cells.nth(k).get_attribute("class").split() for k in range(4)]
    check("g" in cls[0] and "r" in cls[1] and "a" in cls[2] and len(cls[3]) == 1,
          f"couleurs : {cls}")
    check("Non confronté" in cells.nth(3).inner_text(), "case non confrontée")
    check("★ PD1" in cells.nth(0).inner_text(), "PD absent de la grille")
    ref = a.page.locator("[data-chart='mame'] p.ref").inner_text()
    check(ref.startswith("2 opportunité(s) · 2 risque(s) · 1 amendement(s) aux MA · 1 point(s)"), f"compteurs : {ref}")
    a.no_errors()
    a.close()
    return "grille vert/rouge/ambre/vide + compteurs après ajout/suppression"


def t_pdm_gdh(b, vp):
    a = App(b, vp).open()
    a.go("pm", "a")
    rows = [("1", "J+1 02h00", "H_JP1", "Risque"), ("2", "J 06h00", "H_J", "Opportunité"),
            ("3", "J-1 18h00", "H_JM1", "Risque"), ("4", "J 07h00", "A_SUPPR", "Risque")]
    for i, (n, g, h, cn) in enumerate(rows):
        if i:
            a.page.click("button[onclick=\"addRow('pdm')\"]")
        fill_cell(a, "pdm", i, "n", n)
        fill_cell(a, "pdm", i, "h", h)
        fill_cell(a, "pdm", i, "gpd", g)
        select_cell(a, "pdm", i, "cn", cn)
    a.page.click("button[onclick=\"delRow('pdm',3)\"]")
    order = a.page.locator("[data-chart='pdm'] li .g").all_inner_texts()
    check(order == ["J-1 18h00", "J 06h00", "J+1 02h00"], f"tri PdM : {order}")
    # frise consolidée
    a.go("p1e1", "a")
    for g, e in (("J+1 02h00", "F_JP1"), ("J 06h00", "F_J"), ("J−1 18h00", "F_JM1"), ("J 12h", "F_J12")):
        a.page.click("button:has-text('+ Ajouter un repère')")
        a.page.locator("input[aria-label^='GDH, ligne']").last.fill(g)
        a.page.locator("textarea[aria-label^='Événement, ligne']").last.fill(e)
    a.go("recap")
    tl = a.page.locator("[data-chart='frise'] li .e").all_inner_texts()
    check(tl == ["F_JM1", "F_J", "F_J12", "F_JP1"], f"tri frise : {tl}")
    ks = a.js("['J-1 18h00','J 06h00','J+1 02h00','J−1 18h00','J 12h','J+2 00h00'].map(gdhKey)")
    check(ks == [-360, 360, 1560, -360, 720, 2880], f"gdhKey : {ks}")
    a.no_errors()
    a.close()
    return "J-1 < J < J+1 (PdM, frise consolidée, gdhKey ; moins Unicode accepté)"


def t_exam(b, vp):
    a = App(b, vp).open()
    a.nav_click("exam")
    a.page.click("#main button:has-text('Commencer l’examen')")
    check(a.page.locator("#main .qz").count() == 30, "30 questions attendues")
    qs = a.js("EX.qs.map(x=>({mid:x.mid,qi:x.qi}))")
    check(len({(q["mid"], q["qi"]) for q in qs}) == 30, "questions en double")
    check(len({q["mid"] for q in qs}) >= 10, "tirage peu réparti")
    good = a.js("EX.qs.map(x=>M.find(m=>m.id===x.mid).quiz[x.qi].a)")
    for i in range(5):
        a.page.click(f"#exq_{i} button[data-o='{good[i]}']")
    # changer d'avis sur la 6e : d'abord juste puis faux
    wrong6 = (good[5] + 1) % 4
    a.page.click(f"#exq_5 button[data-o='{good[5]}']")
    a.page.click(f"#exq_5 button[data-o='{wrong6}']")
    check(a.page.locator("#exC").inner_text() == "6", "compteur de réponses")
    check(a.page.locator("#exq_5 button[aria-pressed='true']").count() == 1, "sélection multiple")
    t = a.page.locator("#exT").inner_text()
    check(t.startswith("29:") or t.startswith("30:"), f"chrono : {t}")
    a.page.click("#main button:has-text('Terminer et corriger')")
    check("24 questions sans réponse" in a.page.locator("#modal").inner_text(), "avertissement fin anticipée")
    confirm_modal(a, "Terminer et corriger")
    sc = a.page.locator("#main .score").inner_text()
    check(sc.startswith("5 / 30 – 17 %"), f"score : {sc}")
    check("Erreurs à revoir (25)" in a.page.locator("#main").inner_text(), "liste des erreurs")
    exb = json.loads(a.js(f"localStorage.getItem('{EX_KEY}')"))
    check(exb["tout"]["best"] == 17, f"meilleur résultat (périmètre « tout ») : {exb}")
    check(a.js("EXtimer!==null") and a.js("EX.res.expired") is False, "état fin")
    a.go("accueil")
    check("Meilleur résultat : 17 %" in a.page.locator("#main").inner_text(), "rappel du meilleur score à l'accueil")
    a.no_errors()
    a.close()
    return "30 questions, fin anticipée à 6/30, score 5/30 = 17 %"


def t_cas(b, vp):
    a = App(b, vp).open()
    a.page.set_input_files("#fCas", str(CAS_FILE))
    a.page.wait_for_selector("#casMsg .ok-msg")
    msg = a.page.locator("#casMsg").inner_text()
    check("corrigé pour 3 étape(s)" in msg, f"message : {msg}")
    check(a.page.locator("#casBanner").is_visible() and "VALDOR" in a.page.locator("#casBanner").inner_text(), "bandeau cas absent")
    a.page.locator("#casBanner button", has_text="Lire la situation").click()
    check("MISSION DE LA BIA ORION" in a.page.locator("#modal").inner_text(), "situation non affichée")
    a.page.keyboard.press("Escape")
    a.go("p1e1", "a")
    btn = a.page.locator("#main button", has_text="Voir le corrigé")
    check(btn.count() == 1, "bouton « Voir le corrigé » absent")
    btn.click()
    check(a.page.locator("#cor_p1e1").is_visible(), "corrigé non affiché")
    check(a.page.locator("#main button", has_text="Masquer le corrigé").get_attribute("aria-expanded") == "true", "aria-expanded")
    check("Commentaire de l’instructeur" in a.page.locator("#cor_p1e1").inner_text(), "texte instructeur absent")
    a.go("p1e3", "a")
    check("ne contient pas de corrigé" in a.page.locator("#main").inner_text(), "étape sans corrigé")
    a.reload()
    check(a.page.locator("#casBanner").is_visible(), "cas non mémorisé")
    a.page.locator("#casBanner button", has_text="Retirer le cas").click()
    confirm_modal(a, "Oui, retirer le cas")
    check(a.js("document.getElementById('casBanner').hidden&&!document.getElementById('casBanner').innerHTML"),
          "bandeau non réinitialisé (attribut hidden)")
    check(a.js(f"localStorage.getItem('{CAS_KEY}')") is None, "cas encore en localStorage")
    a.go("p1e1", "a")
    check(a.page.locator("#main button", has_text="Voir le corrigé").count() == 0, "corrigé encore proposé")
    # fichier invalide
    a.go("accueil")
    bad = TMP / "bad.json"
    bad.write_text('{"x":1}', encoding="utf-8")
    a.page.set_input_files("#fCas", str(bad))
    a.page.wait_for_selector("#casMsg .warn")
    a.no_errors()
    a.close()
    return "import, situation, corrigé (affiché/masqué), persistance, retrait, fichier invalide refusé"


def t_bandeau_cas_masque(b, vp):
    """Sans cas chargé (au chargement, puis après « Retirer le cas »), le bandeau
    #casBanner ne doit pas être affiché."""
    a = App(b, vp).open()
    bb = a.page.locator("#casBanner").bounding_box()
    h0 = bb["height"] if bb else 0
    a.page.set_input_files("#fCas", str(CAS_FILE))
    a.page.wait_for_selector("#casMsg .ok-msg")
    a.page.locator("#casBanner button", has_text="Retirer le cas").click()
    confirm_modal(a, "Oui, retirer le cas")
    bb = a.page.locator("#casBanner").bounding_box()
    h1 = bb["height"] if bb else 0
    disp = a.js("getComputedStyle(document.getElementById('casBanner')).display")
    a.close()
    check(h0 == 0 and h1 == 0, f"bandeau vide affiché alors que hidden=true (display:{disp}, "
                               f"hauteur {h0:.0f} px au chargement, {h1:.0f} px après retrait)")
    return "bandeau masqué"


def t_export_import(b, vp):
    a = App(b, vp).open()
    a.go("p1e1", "a")
    a.page.fill("#f_mis_msup", "SAUVEGARDE_TEST")
    answer_quiz(a, "p1e1", True)
    a.go("accueil")
    with a.page.expect_download() as dl:
        a.page.click("#main button:has-text('Sauvegarder (fichier .json)')")
    path = TMP / f"save_{vp[0]}.json"
    dl.value.save_as(str(path))
    check(dl.value.suggested_filename == "MEDOT_sauvegarde.json", "nom de fichier")
    data = json.loads(path.read_text(encoding="utf-8"))
    check(data["v"]["mis"]["msup"] == "SAUVEGARDE_TEST" and data["quiz"]["p1e1"]["best"] == 1, "contenu exporté")
    # Word (hors ligne : lien classique)
    with a.page.expect_download() as dw:
        a.page.click("#main button:has-text('Exporter mes travaux (Word)')")
    check(dw.value.suggested_filename == "MEDOT_travaux.doc", "export Word hors ligne")
    # tout effacer
    a.page.click("#main button:has-text('Tout effacer')")
    confirm_modal(a, "Oui, tout effacer")
    st = a.stored()
    check(st["v"] == {} and st["quiz"] == {} and st["tab"] == {}, "Tout effacer incomplet")
    check(a.page.locator("#progTxt").inner_text().startswith("0 /"), "progression non remise à 0")
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_msup") == "", "champ non effacé")
    # réimport
    a.go("accueil")
    a.page.set_input_files("#fImp", str(path))
    a.page.wait_for_function("document.getElementById('ioMsg')&&document.getElementById('ioMsg').innerText.includes('Sauvegarde reprise')")
    check(a.page.locator("#progTxt").inner_text().startswith("1 /"), "progression non reprise")
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_msup") == "SAUVEGARDE_TEST", "champ non repris")
    a.reload()
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_msup") == "SAUVEGARDE_TEST", "réimport non persisté")
    # fichier non reconnu
    a.go("accueil")
    bad = TMP / "bad_save.json"
    bad.write_text('{"foo":1}', encoding="utf-8")
    a.page.set_input_files("#fImp", str(bad))
    a.page.wait_for_function("document.getElementById('ioMsg').innerText.includes('non reconnu')")
    a.no_errors()
    a.close()
    return "export .json + .doc, Tout effacer, réimport (et refus d'un fichier invalide)"


def t_import_meme_fichier(b, vp):
    """Reprendre deux fois de suite la même sauvegarde sans recharger la page
    (ex. : reprise, « Tout effacer », reprise du même fichier). Dans un vrai
    navigateur, l'événement change ne part que si input.value a changé : le
    gestionnaire doit donc vider la valeur après lecture, comme le fait
    importCas. Playwright force l'événement ; on vérifie donc la valeur."""
    a = App(b, vp).open()
    a.go("accueil")
    with a.page.expect_download() as dl:
        a.page.click("#main button:has-text('Sauvegarder (fichier .json)')")
    path = TMP / f"save2_{vp[0]}.json"
    dl.value.save_as(str(path))
    a.page.set_input_files("#fImp", str(path))
    a.page.wait_for_function("document.getElementById('ioMsg').innerText.includes('Sauvegarde reprise')")
    v_imp = a.js("document.getElementById('fImp').value")
    a.page.set_input_files("#fCas", str(CAS_FILE))
    a.page.wait_for_selector("#casMsg .ok-msg")
    v_cas = a.js("document.getElementById('fCas').value")
    a.close()
    check(v_cas == "", "#fCas non vidé (référence)")
    check(v_imp == "", f"#fImp.value reste « {v_imp} » après importJson : choisir à nouveau le même fichier "
                       "ne déclenchera pas onchange")
    return "#fImp vidé après lecture"


def t_import_pendant_demo(b, vp):
    """Reprendre une sauvegarde alors que l'exemple VIENNE est affiché :
    importJson() quitte automatiquement l'exemple VIENNE (bandeau masqué,
    interrupteur décoché), puis la sauvegarde reprise doit être là, en mémoire
    et après rechargement."""
    a = App(b, vp).open()
    a.go("p1e1", "a")
    a.page.fill("#f_mis_msup", "DANS_SAUVEGARDE")
    a.go("accueil")
    with a.page.expect_download() as dl:
        a.page.click("#main button:has-text('Sauvegarder (fichier .json)')")
    path = TMP / f"save3_{vp[0]}.json"
    dl.value.save_as(str(path))
    a.page.click("#main button:has-text('Tout effacer')")
    confirm_modal(a, "Oui, tout effacer")
    a.page.locator("#demoSw").check()
    a.go("accueil")
    a.page.set_input_files("#fImp", str(path))
    a.page.wait_for_function("document.getElementById('ioMsg').innerText.includes('Sauvegarde reprise')")
    check(a.js("DEMO_ON") is False, "l'exemple VIENNE est resté actif après la reprise")
    check(not a.page.locator("#demoSw").is_checked(), "interrupteur « Exemple VIENNE » encore coché")
    check(not a.page.locator("#demoBanner").is_visible(), "bandeau de l'exemple VIENNE encore affiché")
    mem = a.js("(S.v.mis||{}).msup||''")
    a.reload()
    disk = a.js("(S.v.mis||{}).msup||''")
    a.no_errors()
    a.close()
    check(mem == "DANS_SAUVEGARDE" and disk == "DANS_SAUVEGARDE",
          f"sauvegarde reprise en mode démo perdue (mémoire « {mem} », après rechargement « {disk} ») "
          "alors que le message annonce « Sauvegarde reprise »")
    return "sauvegarde conservée"


def t_recherche(b, vp):
    a = App(b, vp).open()
    a.open_nav()
    a.page.fill("#srchIn", "gtia")
    res = a.page.locator("#sres").text_content()  # inner_text applique text-transform:uppercase
    check("Sigles" in res and "GTIA" in res, f"sigle GTIA non trouvé : {res[:80]}")
    a.page.fill("#srchIn", "effet majeur")
    check("Définitions" in a.page.locator("#sres").text_content(), "définition non trouvée")
    a.page.fill("#srchIn", "presupposition")  # sans accent
    check("Présupposition" in a.page.locator("#sres").inner_text(), "recherche insensible aux accents")
    a.page.fill("#srchIn", "zzqx")
    check("Aucun résultat" in a.page.locator("#sres").inner_text(), "absence de résultat")
    a.page.fill("#srchIn", "a")
    check(a.page.locator("#sres").inner_text() == "", "1 caractère : pas de recherche")
    a.page.fill("#srchIn", "Comparaison des MA")
    a.page.locator("#sres a[data-id='p2e4']").click()
    a.page.wait_for_function("cur==='p2e4'")
    a.open_nav()
    a.page.fill("#srchIn", "Confrontation")
    a.page.locator("#sres a[data-card]").first.click()
    a.page.wait_for_function("cur==='vocab'")
    check(a.page.locator(".fcd.flip").count() == 1, "carte de définition non retournée")
    a.open_nav()
    a.page.fill("#srchIn", "BSM")
    a.page.locator("#sres a[data-lex]").first.click()
    a.page.wait_for_function("cur==='lex'")
    check(a.page.locator("tr.hl").count() == 1, "sigle non surligné")
    a.no_errors()
    a.close()
    return "sigles, définitions, étapes, accents, navigation depuis les résultats"


LS_THROW_STORAGE = """
(()=>{const f=()=>{throw new DOMException('Accès refusé','SecurityError')};
 Storage.prototype.getItem=f;Storage.prototype.setItem=f;Storage.prototype.removeItem=f;})();
"""
LS_THROW_GETTER = """
(()=>{try{Object.defineProperty(window,'localStorage',{configurable:true,
 get(){throw new DOMException('Accès refusé','SecurityError')}});}catch(e){}})();
"""


def _ls_scenario(b, vp, script):
    a = App(b, vp, init_script=script).open()
    check(a.js("(()=>{try{localStorage.getItem('x');return false}catch(e){return true}})()"), "simulation inactive")
    a.go("p1e1", "a")
    a.page.fill("#f_mis_msup", "SANS_STOCKAGE")
    a.page.click("button:has-text('+ Ajouter un TCIDR')")
    answer_quiz(a, "p1e1", True)
    check(a.page.locator("#progTxt").inner_text().startswith("1 /"), "quiz non comptabilisé")
    a.go("p2e4", "a")
    fill_cell(a, "cmp", 0, "c", "X")
    a.page.locator("#demoSw").check()
    a.page.locator("#demoSw").uncheck()
    a.go("p1e1", "a")
    check(a.page.input_value("#f_mis_msup") == "SANS_STOCKAGE", "saisie perdue en mémoire")
    a.go("accueil")
    a.page.set_input_files("#fCas", str(CAS_FILE))
    a.page.wait_for_selector("#casMsg .ok-msg")
    check("non mémorisé" in a.page.locator("#casMsg").inner_text(), "avertissement « non mémorisé » absent")
    a.page.locator("#casBanner button", has_text="Retirer le cas").click()
    confirm_modal(a, "Oui, retirer le cas")
    a.go("exam")
    a.page.click("#main button:has-text('Commencer l’examen')")
    a.page.click("#main button:has-text('Terminer et corriger')")
    confirm_modal(a, "Terminer et corriger")
    check(a.page.locator("#main .score").count() == 1, "examen non corrigé")
    a.no_errors()
    a.close()


def t_ls_storage(b, vp):
    _ls_scenario(b, vp, LS_THROW_STORAGE)
    return "Storage.getItem/setItem/removeItem lèvent une exception : appli utilisable"


def t_ls_getter(b, vp):
    _ls_scenario(b, vp, LS_THROW_GETTER)
    return "window.localStorage inaccessible (getter qui lève) : appli utilisable"


MOCK_DL = """
window.__saved=[];window.__uses=[];
window.claude={use:(n)=>{window.__uses.push(n);return Promise.resolve(n==='downloads'?{save:async(o)=>{window.__saved.push({filename:o.filename,type:typeof o.data,len:String(o.data).length,data:String(o.data)});}}:null);}};
"""


def t_downloads(b, vp):
    a = App(b, vp, init_script=MOCK_DL).open()
    a.go("p1e1", "a")
    a.page.fill("#f_mis_msup", "VIA_SAVE")
    a.go("accueil")
    downloads = []
    a.page.on("download", lambda d: downloads.append(d))
    a.page.click("#main button:has-text('Exporter mes travaux (Word)')")
    a.page.wait_for_function("window.__saved.length===1")
    s = a.js("window.__saved[0]")
    check(a.js("window.__uses") == ["downloads"], "use('downloads') non appelé")
    check(s["filename"] == "MEDOT_travaux.doc", f"nom : {s['filename']}")
    check(s["type"] == "string" and s["data"].startswith("<html") and "VIA_SAVE" in s["data"], "contenu Word")
    a.page.wait_for_function("document.getElementById('ioMsg').innerText.includes('enregistré')")
    a.page.click("#main button:has-text('Sauvegarder (fichier .json)')")
    a.page.wait_for_function("window.__saved.length===2")
    check(a.js("window.__saved[1].filename") == "MEDOT_sauvegarde.json", "export json via save()")
    a.page.wait_for_timeout(300)
    check(not downloads, "un téléchargement classique a aussi été déclenché")
    # save() qui échoue → message de repli
    a.js("window.claude={use:()=>Promise.resolve({save:async()=>{throw new Error('refus')}})}")
    a.page.click("#main button:has-text('Exporter mes travaux (Word)')")
    a.page.wait_for_function("document.getElementById('ioMsg').innerText.includes('Copier mes travaux')")
    a.no_errors()
    a.close()
    return "Word et .json passent par save(), aucun téléchargement classique, refus géré"


def t_langues(b, vp):
    """Menu Paramètres, bascule de langue (dont arabe RTL), saisies conservées en français."""
    a = App(b, vp).open("p1e1")
    langs = a.js("Object.keys(I18N)")
    check(len(langs) >= 1, "aucun dictionnaire de langue embarqué")
    a.page.click(".setbtn")
    check(a.page.locator("#langSel option").count() == len(langs) + 1, "sélecteur de langue incomplet")
    a.page.keyboard.press("Escape")
    # une saisie de liste déroulante en français, puis bascule
    a.js("go('p1e1','a')")
    sel = a.page.locator("#main select").first
    first_opt = sel.locator("option").nth(1).get_attribute("value")
    sel.select_option(first_opt)
    out = []
    for lg in langs:
        a.js(f"localStorage.setItem('medot-esorsem-lang','{lg}')")
        a.reload()
        a.js("go('p1e1','c')"); a.page.wait_for_timeout(200)
        h2 = a.page.locator("#main h2").first.inner_text()
        check(a.js("document.documentElement.lang") == lg, f"lang non appliquée ({lg})")
        check(a.js("getComputedStyle(document.getElementById('main')).direction") == ("rtl" if lg == "ar" else "ltr"), f"sens d'écriture ({lg})")
        check("Analyse de la mission" not in h2, f"titre non traduit en {lg} : {h2}")
        a.js("go('p1e1','a')"); a.page.wait_for_timeout(150)
        v = a.page.locator("#main select").first.input_value()
        check(v == first_opt, f"valeur enregistrée modifiée par la traduction ({lg}) : {v}")
        out.append(lg)
    a.js("localStorage.setItem('medot-esorsem-lang','fr')"); a.reload()
    check(a.js("getComputedStyle(document.getElementById('main')).direction") == "ltr", "retour au français")
    a.no_errors()
    a.close()
    return "langues testées : " + ", ".join(out)


def t_conduite(b, vp):
    """Rubrique « Appropriation et conduite » : à part du cycle MEDOT et de l'examen « tout », aide OPO / FRAGO."""
    a = App(b, vp).open("ac_as")
    ids = a.js("M.filter(m=>m.grp==='Appropriation et conduite').map(m=>m.id)")
    check(ids == ["ac_mb", "ac_bb", "ac_rh", "ac_ps", "ac_as", "ac_mg", "ac_sr", "ac_ir", "ac_co"], f"modules : {ids}")
    check(a.js("M.findIndex(m=>m.id==='pm')<M.findIndex(m=>m.id==='ac_mb')&&M.findIndex(m=>m.id==='ac_co')<M.findIndex(m=>m.grp==='Outils')"), "ordre du menu")
    check(not a.js("cycleSvg().includes('ac_')") and "Mission brief" not in a.js("cycleSvg()"), "rubrique présente dans le schéma du cycle")
    for sc, want_ac in (("tout", False), ("ac", True)):
        a.js(f"EXS='{sc}'")
        mids = set(a.js("exPick().map(q=>q.mid)"))
        has_ac = any(m.startswith("ac_") for m in mids)
        check(has_ac == want_ac and (not want_ac or all(m.startswith("ac_") for m in mids)), f"examen {sc} : {sorted(mids)}")
    check(a.js("!M.find(m=>m.id==='pm').quiz.some(q=>/MA est à amender/.test(q.q))"), "règle OPO/FRAGO restée dans le plan de manœuvre")
    a.js("go('ac_as','a')")
    a.page.locator("text=Le MA est à amender partiellement").first.click()
    check("FRAGO" in a.page.locator("#main .card.chk p[role=status]").last.inner_text(), "aide : FRAGO attendu")
    a.page.locator("text=La mission change").first.click()
    check("Nouvel OPO" in a.page.locator("#main .card.chk p[role=status]").last.inner_text(), "aide : OPO attendu")
    check(a.js("LEX.some(x=>x[0]==='MANFUT')"), "sigles de la rubrique absents")
    a.no_errors()
    a.close()
    return "9 modules hors cycle (dont messagerie), examen « tout » sans la rubrique, examen dédié, aide OPO / FRAGO"


def t_ordres(b, vp):
    """Phase 3 – Rédaction des ordres : dans le cycle et l'examen, gabarits assemblés (ordre et message)."""
    a = App(b, vp).open("or_ps")
    ids = a.js("M.filter(m=>m.grp==='Phase 3 – Rédaction des ordres').map(m=>m.id)")
    check(ids == ["or_regles", "or_ps", "or_calque", "or_wingo", "or_opo", "or_frago", "or_ovo", "or_sup"], f"modules : {ids}")
    check(a.js("M.findIndex(m=>m.id==='pm')+1===M.findIndex(m=>m.id==='or_regles')&&M.findIndex(m=>m.id==='or_sup')<M.findIndex(m=>m.id==='ac_mb')"), "ordre du menu")
    check(a.js("cycleSvg().includes(\"tryGo('or_opo')\")"), "phase 3 absente du schéma du cycle")
    a.js("EXS='tout'")
    mids = a.js("exPick().map(q=>q.mid)")
    check(len(mids) == 30 and sum(1 for m in mids if m.startswith("or_")) == 5, f"examen tout : {mids}")
    a.js("EXS='p3'")
    mids = a.js("exPick().map(q=>q.mid)")
    check(len(mids) == 30 and all(m.startswith("or_") for m in mids), "examen phase 3")
    a.js("go('or_ps','a')")
    a.page.fill("#f_orps_m", "Saisir O1 pour H+12")
    fill_cell(a, "orps_art", 0, "u", "511(AZ)BATMECA")
    bi = a.js("M.find(m=>m.id==='or_ps').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('or_ps',{bi})")
    check("Saisir O1 pour H+12" in h and "511(AZ)BATMECA" in h and "Plan simplifié" in h, "plan simplifié non assemblé")
    a.js("go('ac_sr','a')")
    a.page.fill("#f_msr_a", "de1680/de1975")
    a.page.fill("#f_msr_h1", "14(FR)BC/120415Z/MECA/CIE/DE5321/EN MVT VERS LE NORD\n30(FR)BI/120345Z/CHAR/CIE/DE4523/-")
    bi = a.js("M.find(m=>m.id==='ac_sr').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('ac_sr',{bi})")
    for want in ("A/DE1680/DE1975//", "H/11/14(FR)BC/120415Z", "H/12/30(FR)BI", "BT//", "TXT", "EXERCICE/EXERCICE/EXERCICE//"):
        check(want in h, f"message : {want} absent")
    check("C/1/" not in h, "rubrique vide reprise")
    check(a.page.locator("text=Exporter le document (Word)").count() >= 2, "boutons d'export")
    check(a.js("LEX.some(x=>x[0]==='PNVA')&&LEX.some(x=>x[0]==='EFDT')"), "sigles phase 3 / messagerie")
    a.no_errors()
    a.close()
    return "8 modules dans le cycle et l'examen, PS et SITREP assemblés"


def t_fonctions(b, vp):
    """Rubrique « Contributions des fonctions » : hors cycle, examen dédié, encarts dans le cycle, gabarits assemblés."""
    a = App(b, vp).open("fx_dec")
    ids = a.js("M.filter(m=>m.grp==='Contributions des fonctions').map(m=>m.id)")
    check(ids == ["fx_ecim", "fx_dec", "fx_inf", "fx_psy", "fx_cim", "fx_utmc", "fx_ae", "f3_art", "f3_fscc", "f3_coord", "f3_cas", "f3_dsa", "f3_ci3d", "gn_emp", "gn_cmob", "gn_fb", "gn_cied", "rn_b2", "rn_cap", "al_emp", "al_man", "ap_ac4d", "ap_mvt", "nr_men", "nr_def", "nr_dct", "sl_gen", "sl_div", "sl_bsd", "sl_mco", "sl_san", "sl_sdc"], f"modules : {ids}")
    check(a.js("M.findIndex(m=>m.id==='ac_co')<M.findIndex(m=>m.id==='fx_ecim')&&M.findIndex(m=>m.id==='ap_mvt')<M.findIndex(m=>m.grp==='Outils')"), "ordre du menu")
    check(not a.js("cycleSvg().includes('fx_')"), "rubrique présente dans le schéma du cycle")
    for sc, want in (("tout", False), ("fx", True)):
        a.js(f"EXS='{sc}'")
        mids = a.js("exPick().map(q=>q.mid)")
        has = any(m.startswith(("fx_", "f3_", "gn_", "rn_", "al_", "ap_", "nr_", "sl_")) for m in mids)
        check(len(mids) == 30 and has == want and (not want or all(m.startswith(("fx_", "f3_", "gn_", "rn_", "al_", "ap_", "nr_", "sl_")) for m in mids)), f"examen {sc} : {sorted(set(mids))}")
    a.js("EXS='f3'")
    mids = a.js("exPick().map(q=>q.mid)")
    check(len(mids) == 30 and all(m.startswith("f3_") for m in mids) and len(set(mids)) == 6, f"examen f3 : {sorted(set(mids))}")
    n = a.js("['p1e1','p1e2','p1e3','p1e4','p1e5','p2e3','p2e6'].filter(id=>M.find(m=>m.id===id).sections.some(s=>s.go&&s.go.includes('f3_fscc'))).length")
    check(n == 7, f"encarts FSCC : {n}/7")
    a.js("go('f3_fscc','a')")
    fill_cell(a, "f3f_ph", 0, "a", "Cloisonner l'ENI")
    a.page.fill("#f_f3f_rep", "30 % / 60 % / 10 %")
    bi = a.js("M.find(m=>m.id==='f3_fscc').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('f3_fscc',{bi})")
    check("Cloisonner" in h and "30 % / 60 % / 10 %" in h, "planification des feux non assemblée")
    n = a.js("['prealable','p1e1','p1e2','p1e3','p1e5','p2e2','p2e3','dec'].filter(id=>M.find(m=>m.id===id).sections.some(s=>s.go)).length")
    check(n == 8, f"encarts : {n}/8")
    a.js("go('p1e3')")
    a.page.locator("#main .card.enc button", has_text="Déception").first.click()
    check(a.js("cur") == "fx_dec", "lien de l'encart")
    a.js("go('fx_dec','a')")
    a.page.fill("#f_fxd_obj", "Fixer la 232 BM face à l'EST")
    select_cell(a, "fxd_d2is", 0, "c", "Simulation")
    fill_cell(a, "fxd_d2is", 0, "a", "Site de franchissement factice")
    bi = a.js("M.find(m=>m.id==='fx_dec').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('fx_dec',{bi})")
    check("Fixer la 232 BM" in h and "Site de franchissement factice" in h and "Simulation" in h, "OPDEC non assemblée")
    a.js("go('fx_inf','a')")
    fill_cell(a, "fxi_kle", 0, "c", "Maire de Z")
    bi = a.js("M.find(m=>m.id==='fx_inf').apply.findIndex(b=>b.t==='doc')")
    check("Maire de Z" in a.js(f"docHTML('fx_inf',{bi})"), "matrice KLE non assemblée")
    check(a.js("LEX.some(x=>x[0]==='OPDEC')&&LEX.some(x=>x[0]==='DTMC')"), "sigles de la rubrique")
    check(a.js("M.filter(m=>m.grp==='Contributions des fonctions').reduce((s,m)=>s+m.quiz.length,0)") >= 120, "moins de 120 questions")
    check(a.js("LEX.some(x=>x[0]==='FSCL')&&LEX.some(x=>x[0]==='HIDACZ')"), "sigles feux et 3D")
    a.js("EXS='gn'")
    mids = a.js("exPick().map(q=>q.mid)")
    check(len(mids) == 30 and all(m.startswith("gn_") for m in mids) and len(set(mids)) == 4, f"examen gn : {sorted(set(mids))}")
    n = a.js("['p1e1','p1e2','p1e3','p1e4','p2e2','p2e3','p2e5'].filter(id=>M.find(m=>m.id===id).sections.some(s=>s.go&&s.go.some(g=>g.startsWith('gn_')))).length")
    check(n == 7, f"encarts génie : {n}/7")
    a.js("go('p2e5')")
    a.page.locator("#main .card.enc button", has_text="Franchissement et bréchage").first.click()
    check(a.js("cur") == "gn_fb", "lien de l'encart génie")
    a.js("go('gn_fb','a')")
    a.page.fill("#f_gnfb_cp", "CHARENTE 20 m")
    select_cell(a, "gnfb_b", 0, "e", "Assaut 1er échelon")
    fill_cell(a, "gnfb_b", 0, "u", "332 BATCHAR")
    bi = a.js("M.find(m=>m.id==='gn_fb').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('gn_fb',{bi})")
    check("CHARENTE 20 m" in h and "332 BATCHAR" in h and "Assaut 1er échelon" in h, "plan de bréchage non assemblé")
    check(a.js("DEMO.tab.gnfb_b.length>=6&&DEMO.v.gnfb.ty.includes('(à valider)')"), "corrigé VIENNE génie")
    check(a.js("LEX.some(x=>x[0]==='SPRAT')&&LEX.some(x=>x[0]==='ZTR')"), "sigles génie")
    for sc, n_mod in (("rn", 2), ("al", 2)):
        a.js(f"EXS='{sc}'")
        mids = a.js("exPick().map(q=>q.mid)")
        check(len(mids) == 30 and all(m.startswith(sc + "_") for m in mids) and len(set(mids)) == n_mod, f"examen {sc} : {sorted(set(mids))}")
    n = a.js("['p1e1','p1e3','p1e4','p2e1','p2e2','p2e3','p2e5','or_opo'].filter(id=>M.find(m=>m.id===id).sections.some(s=>s.go&&s.go.some(g=>/^(rn|al|ap)_/.test(g)))).length")
    check(n == 8, f"encarts renseignement / aérocombat : {n}/8")
    a.js("go('p2e5')")
    a.page.locator("#main .card.enc button", has_text="Aérocombat dans la manœuvre").first.click()
    check(a.js("cur") == "al_man", "lien de l'encart aérocombat")
    a.js("go('al_man','a')")
    fill_cell(a, "alman", 0, "z", "ZEA NORD")
    select_cell(a, "alman", 0, "s", "TACON")
    bi = a.js("M.find(m=>m.id==='al_man').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('al_man',{bi})")
    check("ZEA NORD" in h and "TACON" in h, "emploi de l'aérocombat non assemblé")
    a.js("go('rn_b2','a')")
    a.page.fill("#f_rnz_zrr", "ZRR de la brigade")
    fill_cell(a, "rnbpr", 0, "q", "Attitude du 233 BM")
    bi = a.js("M.find(m=>m.id==='rn_b2').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('rn_b2',{bi})")
    check("ZRR de la brigade" in h and "Attitude du 233 BM" in h, "besoins en renseignement non assemblés")
    check(a.js("DEMO.tab.alman.length>=2&&DEMO.tab.rncap.every(r=>r.r.includes('(à valider)'))"), "corrigé VIENNE aérocombat / capteurs")
    check(a.js("LEX.some(x=>x[0]==='SGRM')&&LEX.some(x=>x[0]==='ETB')&&LEX.some(x=>x[0]==='EEI')"), "sigles 6d-1")
    for sc, n_mod in (("nr", 3), ("sl", 6)):
        a.js(f"EXS='{sc}'")
        mids = a.js("exPick().map(q=>q.mid)")
        check(len(mids) == 30 and all(m.startswith(sc + "_") for m in mids) and len(set(mids)) == n_mod, f"examen {sc} : {sorted(set(mids))}")
    n = a.js("['p1e2','p1e3','p1e4','p2e2','p2e3','p2e5','or_opo'].filter(id=>M.find(m=>m.id===id).sections.some(s=>s.go&&s.go.some(g=>/^(nr|sl)_/.test(g)))).length")
    check(n == 7, f"encarts NRBC / soutien : {n}/7")
    a.js("go('p2e5')")
    a.page.locator("#main .card.enc button", has_text="La brigade de soutien divisionnaire").first.click()
    check(a.js("cur") == "sl_bsd", "lien de l'encart soutien")
    a.js("go('nr_dct','a')")
    a.page.fill("#f_nrdp_pil", "GTIA 2 pilote, région de Z")
    select_cell(a, "nrsite", 0, "e", "Point initial")
    fill_cell(a, "nrsite", 0, "l", "Carrefour C12")
    bi = a.js("M.find(m=>m.id==='nr_dct').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('nr_dct',{bi})")
    check("GTIA 2 pilote" in h and "Carrefour C12" in h and "Point initial" in h, "plan de décontamination non assemblé")
    a.js("go('sl_div','a')")
    fill_cell(a, "slcs", 0, "ph", "Phase 1")
    select_cell(a, "slcs", 0, "f", "Flux tirés")
    bi = a.js("M.find(m=>m.id==='sl_div').apply.findIndex(b=>b.t==='doc')")
    h = a.js(f"docHTML('sl_div',{bi})")
    check("Phase 1" in h and "Flux tirés" in h, "concept de soutien non assemblé")
    check(a.js("LEX.some(x=>x[0]==='SIDEC')&&LEX.some(x=>x[0]==='PRMAR')&&LEX.some(x=>x[0]==='DAS')"), "sigles 6d-2")
    check(a.js("new Set(LEX.map(x=>x[0])).size===LEX.length"), "sigles en double")
    a.no_errors()
    a.close()
    return "32 modules hors cycle (dont 6 Feux et 3D, 4 Génie, 2 Renseignement, 2 Aérocombat, 2 Appuis, 3 NRBC, 6 Soutien), examens fx, f3, gn, rn, al, nr et sl, encarts liés, gabarits assemblés"


TESTS = [
    ("Chargement sans erreur console", t_chargement),
    ("Navigation modules × 3 onglets", t_navigation),
    ("Quiz → étape validée + progression", t_quiz),
    ("Persistance fields/table/TCIDR/frise", t_persistance),
    ("Exemple VIENNE n'écrase pas les saisies", t_demo),
    ("Bloc sync (lignes + Gantt)", t_sync),
    ("Bloc cmp (total pondéré)", t_cmp),
    ("Bloc mame (grille MA × ME)", t_mame),
    ("Bloc pdm + tri GDH", t_pdm_gdh),
    ("Examen blanc (30 q, fin anticipée)", t_exam),
    ("Chargeur de cas (Valdor)", t_cas),
    ("Bandeau cas masqué sans cas", t_bandeau_cas_masque),
    ("Export JSON / Tout effacer / réimport", t_export_import),
    ("Réimport du même fichier .json", t_import_meme_fichier),
    ("Reprise de sauvegarde pendant l'exemple VIENNE", t_import_pendant_demo),
    ("Recherche", t_recherche),
    ("localStorage indisponible (méthodes)", t_ls_storage),
    ("localStorage indisponible (getter)", t_ls_getter),
    ("window.claude.use('downloads') → save()", t_downloads),
    ("Rubrique Appropriation et conduite", t_conduite),
    ("Phase 3 – Rédaction des ordres et messagerie", t_ordres),
    ("Rubrique Contributions des fonctions", t_fonctions),
    ("Langues (Paramètres, RTL, saisies conservées)", t_langues),
]


def main():
    only = sys.argv[1:]
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, fn in TESTS:
            if only and not any(o.lower() in (name + fn.__name__).lower() for o in only):
                continue
            for vpn, vp in VIEWPORTS.items():
                try:
                    detail = fn(b, vp)
                    RESULTS.append((name, vpn, True, detail or ""))
                except Check as e:
                    RESULTS.append((name, vpn, False, str(e)))
                except Exception as e:  # erreur Playwright (sélecteur, timeout…)
                    tb = traceback.format_exc().strip().splitlines()
                    where = next((l.strip() for l in reversed(tb) if "test_app.py" in l), "")
                    RESULTS.append((name, vpn, False, f"{type(e).__name__}: {str(e).splitlines()[0]} [{where}]"))
                print(("OK " if RESULTS[-1][2] else "KO ") + f"{name} [{vpn}] – {RESULTS[-1][3]}", flush=True)
        b.close()
    ok = sum(1 for r in RESULTS if r[2])
    ko = len(RESULTS) - ok
    print(f"\n{ok} OK / {ko} KO ({len(RESULTS)} tests, {time.time()-t0:.0f} s)")
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())
