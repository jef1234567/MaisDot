#!/usr/bin/env python3
"""Scénario complet MaisDot Classroom (Playwright, Chromium, file://), PC et smartphone :
professeur crée le groupe → 2 élèves fixent leur identité, travaillent et envoient → envoi modifié à la main →
professeur reçoit, contrôle, corrige → élève importe sa correction. Vérifie aussi l'absence du corrigé côté élève.
Exécution : python3 tests/test_classroom.py (code retour 0 si tout est OK)"""
import json, pathlib, sys, tempfile, traceback
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
EL = (ROOT / "classroom-eleve.html").as_uri()
PF = (ROOT / "classroom-professeur.html").as_uri()
TMP = pathlib.Path(tempfile.mkdtemp(prefix="maisdot_cls_"))
LONG = "Conquérir la zone entre L1 et L3 en fixant le bataillon ennemi de front puis en le débordant par le nord."
RES = []


def check(c, m):
    if not c:
        raise AssertionError(m)


class P:
    def __init__(self, b, url, vp):
        self.ctx = b.new_context(viewport={"width": vp[0], "height": vp[1]}, accept_downloads=True,
                                 is_mobile=vp[0] < 821, has_touch=vp[0] < 821)
        self.p = self.ctx.new_page()
        self.p.set_default_timeout(8000)
        self.err = []
        self.p.on("pageerror", lambda e: self.err.append(str(e)))
        self.p.on("console", lambda m: m.type == "error" and self.err.append(m.text))
        self.p.goto(url)
        self.p.wait_for_selector("#main h2", state="attached")

    def js(self, e, a=None):
        return self.p.evaluate(e, a)

    def click(self, txt):
        self.p.locator("#main button, #modal button", has_text=txt).first.click()

    def download(self, txt, name):
        with self.p.expect_download() as d:
            self.click(txt)
        f = TMP / name
        d.value.save_as(f)
        return f


def eleve(b, vp, code, nom, mat, longtxt):
    e = P(b, EL, vp)
    check(e.p.locator("#ciN").count() == 1, "page d'identité absente à la 1re ouverture")
    e.js("go('p1e1')")
    check(e.p.locator("#ciN").count() == 1, "identité contournable par la navigation")
    e.p.fill("#ciG", "CNE"); e.p.fill("#ciN", nom); e.p.fill("#ciP", "Jean"); e.p.fill("#ciM", mat)
    e.p.fill("#ciC", "ABCD-EFGH-JKLM-NPQR-STUV")
    e.click("Valider mon identité")
    check("Code du groupe invalide" in e.p.inner_text("#ciMsg"), "code faux accepté")
    e.p.fill("#ciC", code.lower())
    e.click("Valider mon identité")
    e.click("Confirmer")
    e.p.wait_for_selector("text=Envoyer mes travaux au professeur")
    check(nom.upper() in e.p.text_content("header") and nom.upper() in e.p.inner_text("#main"), "identité absente")
    check(e.p.locator("header .demo-sw").count() == 0, "bascule Exemple VIENNE présente côté élève")
    # gabarit rempli + test fait
    fb = e.js("(()=>{const b=M.find(m=>m.id==='p1e1').apply.find(b=>b.t==='fields'&&b.f.some(f=>f.a));return [b.id,b.f.find(f=>f.a).k];})()")
    e.js("go('p1e1','a')")
    e.p.fill(f"#f_{fb[0]}_{fb[1]}", longtxt + " 1")
    e.p.fill(f"#f_{fb[0]}_{fb[1]}", longtxt)
    check(e.p.locator("#main .cor").count() == 0 and "Voir le corrigé" not in e.p.inner_text("#main"), "corrigé visible côté élève")
    e.js("go('vocab','e')")
    for _ in range(40):
        o = e.p.locator("#main .qz button.o:not([disabled])")
        if o.count() == 0:
            break
        o.first.click()
    e.js("go('accueil')")
    check("Cas concret (instructeur)" not in e.p.inner_text("#main"), "chargement de cas présent côté élève")
    e.p.locator("header button", has_text="Sujet VIENNE").click()
    check("SITUATION GÉNÉRALE" in e.p.inner_text("#modal") and "AVERTISSEMENT" not in e.p.inner_text("#modal"), "sujet VIENNE incorrect")
    e.js("closeModal()")
    e.js("go('cls_envoi')")
    f = e.download("Préparer mon envoi", f"envoi_{mat}.json")
    o = json.loads(f.read_text())
    check(o["type"] == "maisdot-classroom-envoi" and o["id"]["mat"] == mat and o["sig"], "envoi mal formé")
    check(o["data"]["log"].get(fb[0], {}).get("n", 0) >= 2, "journal de saisie absent")
    return e, f, fb


def t_scenario(b, vp):
    pr = P(b, PF, vp)
    pr.js("go('cls_groupe')")
    pr.p.fill("#gN", "Groupe test")
    pr.click("Créer le groupe")
    code = pr.p.inner_text(".cls-code").strip()
    check(len(code) == 24, "code du groupe : " + code)
    e1, f1, fb = eleve(b, vp, code, "Dupont", "1234567890", LONG)
    e2, f2, _ = eleve(b, vp, code, "Martin", "2234567890", LONG)
    # envoi modifié à la main
    o = json.loads(f2.read_text()); o["data"]["quiz"]["vocab"] = {"best": 1, "last": 1}
    f3 = TMP / "triche.json"; f3.write_text(json.dumps(o))
    pr.p.set_input_files("#fEnv", [str(f1), str(f3)])
    pr.p.wait_for_selector("#envMsg p >> nth=1")
    m = pr.p.inner_text("#envMsg")
    check("Signature invalide" in m and "contrôle correct" in m, "contrôle des envois : " + m)
    t = pr.p.inner_text("#main")
    check("Travaux très proches" in t, "similarité non détectée")
    check("DUPONT" in t and "MARTIN" in t, "élèves absents du tableau")
    # correction de l'élève 1
    pr.p.locator("tr", has_text="DUPONT").locator("button", has_text="Corriger").click()
    pr.p.wait_for_selector("#cGen")
    pr.p.locator("#cm_p1e1 details.cls-cor summary").click()
    check("Corrigé VIENNE" in pr.p.inner_text("#main") and LONG in pr.p.inner_text("#main") and "Conquérir la zone entre L1 et L3" in pr.p.inner_text("#cm_p1e1 details.cls-cor"), "vue de correction incomplète")
    pr.click("Appliquer les suggestions")
    pr.p.locator("#cm_p1e1 input[value='NA']").check()
    pr.p.fill("#cc_p1e1", "Le but à atteindre doit commencer par « En vue de ».")
    pr.p.fill("#cGen", "Bon début.")
    fc = pr.download("Exporter la correction", "correction.json")
    c = json.loads(fc.read_text())
    check(c["items"]["p1e1"]["s"] == "NA" and c["items"].get("vocab", {}).get("s") in ("A", "NA"), "correction mal formée : " + json.dumps(c["items"]))
    pr.js("go('cls_synth')")
    check("Exporter la synthèse" in pr.p.inner_text("#main"), "synthèse absente")
    # l'élève 2 ne peut pas importer la correction de l'élève 1
    e2.js("go('cls_envoi')")
    e2.p.set_input_files("#fCor", str(fc))
    e2.p.wait_for_selector("#corMsg p")
    check("autre élève" in e2.p.inner_text("#corMsg"), "correction d'un autre élève acceptée")
    # l'élève 1 importe sa correction
    e1.js("go('cls_envoi')")
    e1.p.set_input_files("#fCor", str(fc))
    e1.p.wait_for_selector("text=Points non maîtrisés")
    t = e1.p.inner_text("#main")
    check("En vue de" in t and "Bon début." in t, "correction non affichée")
    e1.p.locator("#main button", has_text="Revoir l’étape").first.click()
    check("non acquis" in e1.p.inner_text("#main .cls-bn"), "bandeau de correction absent")
    check(e1.p.locator("#navList .cls-nav-na").count() >= 1, "repère non acquis absent du menu")
    # persistance prof (IndexedDB)
    pr.p.reload(); pr.p.wait_for_function("PR&&PR.grp"); pr.js("go('cls_groupe')"); pr.p.wait_for_selector("#main h2")
    check("DUPONT" in pr.p.inner_text("#main"), "groupe non conservé au rechargement : " + pr.js("JSON.stringify(Object.keys(PR.st))+' '+cur"))
    for x in (pr, e1, e2):
        check(not x.err, "erreurs JS : " + "; ".join(x.err[:3]))
        x.ctx.close()


def t_corrige_absent(b, vp):
    h = (ROOT / "classroom-eleve.html").read_text(encoding="utf-8")
    for w in ["SPRAT en secours", "JE VEUX AVOIR DÉTRUIT le 233", "const DEMO_P2", "Ennemi global : 23(MI)BRIMECA"]:
        check(w not in h, "corrigé présent dans la version élève : " + w)
    e = P(b, EL, vp)
    check(e.js("Object.keys(DEMO.v).length+Object.keys(DEMO.tab).length+DEMO.tcidr.length+DEMO.frise.length") == 0, "DEMO non vide")
    check(not e.err, "erreurs JS : " + "; ".join(e.err[:3]))
    e.ctx.close()


def t_langue(b, vp):
    e = P(b, EL, vp)
    e.js("localStorage.setItem('medot-esorsem-lang','en')"); e.p.reload(); e.p.wait_for_timeout(300)
    check("Validate my identity" in e.p.inner_text("#main") or "Confirm my identity" in e.p.inner_text("#main") or "identity" in e.p.inner_text("#main"), "page d’identité non traduite")
    check(not e.err, "erreurs JS : " + "; ".join(e.err[:3]))
    e.ctx.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for vn, vp in {"PC": (1366, 768), "Mobile": (390, 844)}.items():
            for t in (t_corrige_absent, t_scenario, t_langue):
                try:
                    t(b, vp); RES.append((t.__name__, vn, True, ""))
                except Exception as ex:
                    RES.append((t.__name__, vn, False, str(ex) or traceback.format_exc(limit=2)))
        b.close()
    for n, v, ok, d in RES:
        print(("OK  " if ok else "ÉCHEC"), n, v, d[:300])
    print(f"{sum(r[2] for r in RES)}/{len(RES)}")
    sys.exit(0 if all(r[2] for r in RES) else 1)
