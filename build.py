"""Assemble les fichiers livrés (monofichiers, hors ligne) à partir de src/ :
- index.html                 : MaisDot (inchangé)
- classroom-eleve.html       : MaisDot Classroom, version élève (SANS le corrigé VIENNE)
- classroom-professeur.html  : MaisDot Classroom, version professeur (avec le corrigé VIENNE)
"""
import base64, json, pathlib, re

root = pathlib.Path(__file__).parent
SRC = root / "src"
FILES = ["demo.js", "p2.js", "normes.js", "conduite.js", "ordres.js", "messagerie.js", "fonctions.js",
         "feux.js", "genie.js", "rens.js", "soutien.js", "symboles.js", "referentiels.js"]


def js_block_end(s, start):
    """Indice juste après l'accolade fermante du bloc qui s'ouvre au premier « { » après start (chaînes JS ignorées)."""
    i = s.index("{", start)
    depth, q = 0, None
    while i < len(s):
        c = s[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("bloc non fermé")


def strip_corrige(name, s):
    """Version élève : retire toutes les valeurs du corrigé VIENNE (l'énoncé DEMO_SITU est conservé)."""
    if name == "demo.js":
        i = s.index("const DEMO = {")
        e = js_block_end(s, i)
        assert s[e:].strip() in ("", ";"), "contenu inattendu après DEMO"
        return s[:i] + 'const DEMO={quiz:{},unlock:true,v:{},tab:{},tcidr:[],frise:[]};\n'
    if name == "p2.js":
        i = s.index("const DEMO_P2={")
        e = js_block_end(s, i)
        assert s[e:].strip() in ("", ";"), "contenu inattendu après DEMO_P2"
        return s[:i]
    out, pos = s, 0
    while True:
        i = out.find('if(typeof DEMO!=="undefined"){', pos)
        if i < 0:
            return out
        e = js_block_end(out, i)
        out = out[:i] + "/* corrigé retiré (version élève) */" + out[e:]
        pos = i


LIT = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`(?:[^`\\$]|\\.)*`')
SEPS = [" · ", " – ", " → ", " ; ", " : "]


def literals(code):
    out = set()
    for m in LIT.finditer(code):
        g = m.group(0)
        try:
            t = json.loads(g) if g[0] == '"' else json.loads('"' + g[1:-1].replace("\\'", "'").replace("\\`", "`").replace('"', '\\"') + '"')
        except Exception:
            t = g[1:-1]
        out.add(t)
    return out


def expand(S):
    out = set()
    for t in S:
        for x in [t] + [p for sp in SEPS for p in t.split(sp)] + t.split("\n"):
            x = x.strip()
            if x:
                out.add(x)
                out.add(re.sub(r"\d+(?:[.,]\d+)?", "{n}", x))
    return out


def demo_strings():
    """Toutes les chaînes du corrigé VIENNE complet (évalué avec node : DEMO, DEMO_P2 et blocs des modules)."""
    import subprocess
    parts = [(SRC / "demo.js").read_text(encoding="utf-8")]
    p2 = (SRC / "p2.js").read_text(encoding="utf-8")
    i = p2.index("const DEMO_P2={")
    parts.append(p2[i:js_block_end(p2, i)] + ";Object.assign(DEMO.v,DEMO_P2.v||{});Object.assign(DEMO.tab,DEMO_P2.tab||{});"
                 "DEMO.tcidr.push(...(DEMO_P2.tcidr||[]));DEMO.frise.push(...(DEMO_P2.frise||[]));")
    for f in FILES:
        t, pos = (SRC / f).read_text(encoding="utf-8"), 0
        while True:
            i = t.find('if(typeof DEMO!=="undefined"){', pos)
            if i < 0:
                break
            e = js_block_end(t, i)
            parts.append(t[i:e])
            pos = e
    js = "\n".join(parts) + "\nconst out=[];const w=x=>{if(typeof x==='string')out.push(x);else if(Array.isArray(x))x.forEach(w);" \
        "else if(x&&typeof x==='object')Object.values(x).forEach(w);};w(DEMO);process.stdout.write(JSON.stringify(out));"
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def build(mode=None):
    logo = base64.b64encode((SRC / "logo.webp").read_bytes()).decode()
    html = (SRC / "app.html").read_text(encoding="utf-8").replace("__LOGO__", logo)
    I = {jf.stem: json.loads(jf.read_text(encoding="utf-8")) for jf in sorted((SRC / "i18n").glob("*.json"))}
    if mode == "eleve":
        # les dictionnaires contiennent aussi le corrigé VIENNE (clés françaises) : on retire les clés propres au corrigé
        kept = [html, (SRC / "classroom.js").read_text(encoding="utf-8")] + \
            [strip_corrige(f, (SRC / f).read_text(encoding="utf-8")) for f in FILES]
        K = expand(set().union(*[literals(x) for x in kept]))
        R = expand(set(demo_strings())) - K
        for L in I.values():
            for k in [k for k in L if k not in K and (k in R or "(à valider)" in k or "(à valider)" in k
                                                       or any(x in R for x in expand({re.sub(r"^[★→•▶✓✗\s]+", "", k)})))]:
                del L[k]
    i18n = (SRC / "i18n.js").read_text(encoding="utf-8").replace(
        "/*__I18N__*/{}", json.dumps(I, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    html = html.replace("/*__i18n.js__*/", i18n)
    for f in FILES:
        p = SRC / f
        if p.exists():
            t = p.read_text(encoding="utf-8")
            if mode == "eleve":
                t = strip_corrige(f, t)
            html = html.replace(f"/*__{f}__*/", t)
    if mode:
        html = html.replace("/*__CLS_MODE__*/", f'var CLS_MODE="{mode}";')
        html = html.replace("/*__classroom.js__*/", (SRC / "classroom.js").read_text(encoding="utf-8"))
        html = re.sub(r"<title>[^<]*</title>", "<title>MaisDot Classroom – " +
                      ("version élève" if mode == "eleve" else "version professeur") + "</title>", html, count=1)
    else:
        html = html.replace("/*__CLS_MODE__*/", "").replace("/*__classroom.js__*/", "")
    return html


for mode, name in [(None, "index.html"), ("eleve", "classroom-eleve.html"), ("prof", "classroom-professeur.html")]:
    h = build(mode)
    if mode == "eleve":
        # contrôle : aucune valeur « (à valider) » du corrigé ne doit subsister
        assert "const DEMO_P2" not in h and 'if(typeof DEMO!=="undefined"){' not in h and "JE VEUX AVOI" not in h, "corrigé encore présent"
    (root / name).write_text(h, encoding="utf-8")
    print(name, len(h), "octets")
