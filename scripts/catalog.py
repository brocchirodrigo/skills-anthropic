#!/usr/bin/env python3
"""Catálogo de skills oficiais da Anthropic.

Uso:
  python3 scripts/catalog.py update [--no-fetch]   baixa os repositórios, varre as skills e atualiza data/skills.json
  python3 scripts/catalog.py build  [--allow-missing]  gera o index.html a partir de src/template.html e data/skills.json
  python3 scripts/catalog.py check                  mostra o que falta revisar (resumos, áreas, descrições alteradas)

Requisitos: Python 3.9+ e git. Nenhuma biblioteca externa.
"""
import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache")
CONFIG = os.path.join(ROOT, "config", "sources.json")
AREAS = os.path.join(ROOT, "config", "areas.json")
DATA = os.path.join(ROOT, "data", "skills.json")
REPORT = os.path.join(ROOT, "data", "report.json")
TEMPLATE = os.path.join(ROOT, "src", "template.html")
OUTPUT = os.path.join(ROOT, "index.html")

SCRIPT_EXT = {".py", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".rb", ".r", ".R", ".ps1"}
TEXT_EXT = SCRIPT_EXT | {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".html", ""}
SHELL_BLOCK = re.compile(r"```(?:bash|sh|shell|zsh|console|shellscript)\b", re.I)
CODE = re.compile(r"```[^\n]*\n(.*?)```|`([^`\n]+)`", re.S)
PKG = [
    (r"\bpip3?\s+install\s+([^\n`|&;#]+)", "pip"),
    (r"\buv\s+(?:pip\s+install|add|tool\s+install)\s+([^\n`|&;#]+)", "uv"),
    (r"\bpipx\s+install\s+([^\n`|&;#]+)", "pipx"),
    (r"\bconda\s+install\s+([^\n`|&;#]+)", "conda"),
    (r"\b(?:npm\s+(?:i|install|add)|pnpm\s+(?:add|install)|yarn\s+add|bun\s+add)\s+([^\n`|&;#]+)", "npm"),
    (r"\b(?:npx|bunx|pnpm\s+dlx)\s+(?:-y\s+|--yes\s+)?([@\w./-]+)", "npx"),
    (r"\buvx\s+([@\w./=-]+)", "uvx"),
    (r"\bbrew\s+install\s+([^\n`|&;#]+)", "brew"),
    (r"\bapt(?:-get)?\s+install\s+([^\n`|&;#]+)", "apt"),
    (r"\bcargo\s+install\s+([^\n`|&;#]+)", "cargo"),
    (r"\bgem\s+install\s+([^\n`|&;#]+)", "gem"),
    (r"\bgo\s+install\s+([^\n`|&;#]+)", "go"),
    (r"install\.packages\(([^)]+)\)", "R"),
]
STOP = {"npx", "requirements.txt", "the", "a", "an", "and", "or", "to", "it", "its", "this", "that", "unless",
        "not", "only", "told", "with", "for", "if", "then", "your", "you", "package", "packages", "dependencies",
        "deps", "them", "first", "locally", "globally", "via", "from", "in", "on"}
OKTOK = re.compile(r"^@?[A-Za-z0-9][\w.\-/@\[\]=<>~^:,]*$")


def log(msg):
    print(msg, file=sys.stderr)


# ---------- git ----------

def repo_dir(slug):
    return os.path.join(CACHE, slug.replace("/", "__"))


def fetch(slug, do_fetch, seen):
    """Clona (ou atualiza) um repositório público do GitHub em .cache/."""
    d = repo_dir(slug)
    if slug in seen:
        return d
    seen.add(slug)
    url = f"https://github.com/{slug}.git"
    if not os.path.isdir(os.path.join(d, ".git")):
        os.makedirs(CACHE, exist_ok=True)
        log(f"clonando {slug}")
        subprocess.run(["git", "clone", "-q", "--depth", "1", url, d], check=True)
    elif do_fetch:
        log(f"atualizando {slug}")
        subprocess.run(["git", "-C", d, "fetch", "-q", "--depth", "1", "origin"], check=True)
        subprocess.run(["git", "-C", d, "reset", "-q", "--hard", "FETCH_HEAD"], check=True)
    return d


def slug_from_url(url):
    p = urllib.parse.urlparse(url)
    parts = p.path.strip("/").removesuffix(".git").split("/")
    return "/".join(parts[:2]) if p.netloc.endswith("github.com") and len(parts) >= 2 else None


# ---------- parsing ----------

def frontmatter(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    block = m.group(1)
    try:
        import yaml  # opcional
        data = yaml.safe_load(block)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    out, key, buf, mode = {}, None, [], None
    for line in block.split("\n"):
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km and not line.startswith(" "):
            if key and mode:
                out[key] = " ".join(x.strip() for x in buf).strip()
            key, val = km.group(1), km.group(2).strip()
            if val in (">", "|", ">-", "|-"):
                mode, buf = "block", []
            else:
                mode = None
                out[key] = val.strip("'\"")
        elif mode == "block":
            buf.append(line)
    if key and mode:
        out[key] = " ".join(x.strip() for x in buf).strip()
    return out


def author_of(obj):
    a = obj.get("author") if isinstance(obj, dict) else None
    if isinstance(a, dict):
        return a.get("name") or "", a.get("email") or ""
    if isinstance(a, str):
        return a, ""
    return "", ""


def is_anthropic(name, email=""):
    return "anthropic" in (name or "").lower() or (email or "").lower().endswith("@anthropic.com")


def is_coauthored(author):
    return bool(re.search(r"[/&+,]| and | e ", author or ""))


def load_json(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def skill_dirs(base, rel):
    root = os.path.normpath(os.path.join(base, rel))
    found = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [x for x in dn if x not in (".git", "node_modules")]
        if "SKILL.md" in fn:
            found.append(os.path.relpath(dp, base))
    return sorted(found)


# ---------- discovery ----------

def discover(cfg, do_fetch):
    seen = set()
    third = re.compile(r"(^|/)(" + "|".join(map(re.escape, cfg["third_party_dirs"])) + r")(/|$)")
    locs = {}  # (owner, repo, skill_path) -> loc

    def add(owner, repo, base, plugin_rel, sdir, plugin, market, market_repo, author):
        key = (owner, repo, sdir)
        loc = {"o": owner, "r": repo, "path": sdir, "p": plugin, "m": market, "mr": market_repo,
               "au": author, "co": is_coauthored(author), "_base": base, "_plugin_dir": plugin_rel}
        old = locs.get(key)
        same_repo = market_repo == f"{owner}/{repo}"
        if old is None or (same_repo and old["mr"] != f"{owner}/{repo}") or (old["m"] is None and market):
            locs[key] = loc

    for slug in cfg["marketplaces"]:
        d = fetch(slug, do_fetch, seen)
        owner, repo = slug.split("/")
        covered = set()
        mk = load_json(os.path.join(d, ".claude-plugin", "marketplace.json"), {})
        on, oe = author_of({"author": mk.get("owner", {})})
        owner_anth = is_anthropic(on, oe)
        for pl in mk.get("plugins", []):
            src = pl.get("source")
            if isinstance(src, str):
                po, pr, base, prel = owner, repo, d, os.path.normpath(src)
            elif isinstance(src, dict):
                ext = src.get("url") or (f"https://github.com/{src['repo']}" if src.get("repo") else None)
                ext_slug = slug_from_url(ext) if ext else None
                if not ext_slug:
                    continue
                po, pr = ext_slug.split("/")
                base, prel = None, os.path.normpath(src.get("path", "."))
            else:
                continue
            name, email = author_of(pl)
            if not name and base:
                name, email = author_of(load_json(os.path.join(base, prel, ".claude-plugin", "plugin.json"), {}))
            if not name and isinstance(src, str) and not third.search(prel) and owner_anth:
                name = "Anthropic"
            if not is_anthropic(name, email):
                continue
            if base is None:
                base = fetch(f"{po}/{pr}", do_fetch, seen)
                if not name:
                    name, _ = author_of(load_json(os.path.join(base, prel, ".claude-plugin", "plugin.json"), {}))
            dirs = ([os.path.normpath(os.path.join(prel, x)) for x in pl["skills"]] if pl.get("skills")
                    else skill_dirs(base, prel))
            for sd in dirs:
                if os.path.exists(os.path.join(base, sd, "SKILL.md")):
                    add(po, pr, base, prel, sd, pl["name"], mk.get("name"), slug, name)
            covered.add(prel)
        # plugins da Anthropic que existem no repositório mas não estão em nenhum marketplace
        for dp, dn, fn in os.walk(d):
            dn[:] = [x for x in dn if x not in (".git", "node_modules")]
            if os.path.basename(dp) == ".claude-plugin" and "plugin.json" in fn:
                prel = os.path.normpath(os.path.relpath(os.path.dirname(dp), d))
                if prel in covered or third.search(prel):
                    continue
                pj = load_json(os.path.join(dp, "plugin.json"), {})
                name, email = author_of(pj)
                if not is_anthropic(name, email):
                    continue
                for sd in skill_dirs(d, prel):
                    if (owner, repo, sd) not in locs:
                        add(owner, repo, d, prel, sd, pj.get("name", os.path.basename(prel)), None, None, name)
    return list(locs.values())


# ---------- scanning ----------

def clean_tokens(tok):
    out = []
    for t in re.split(r"\s+", tok.strip()):
        if not t or t.startswith("-") or t in ("install", "add", "-r", ".", "-e"):
            continue
        t = t.strip("\"'`(),")
        if not t or t.startswith("$") or t.startswith("<") or "{" in t:
            continue
        if (t.lower() in STOP or not OKTOK.match(t) or t.endswith(".")
                or re.search(r"\.(ts|js|txt|py|json|md|sh)$", t)
                or ("/" in t and not t.startswith("@") and not re.match(r"^[\w.-]+/[\w.-]+(/[\w.-]+)*(@[\w.]+)?$", t))):
            break
        out.append(t)
        if len(out) >= 6:
            break
    return out


def scan(loc, noise):
    d = os.path.join(loc["_base"], loc["path"])
    pkg, scripts, shell, text = collections.OrderedDict(), set(), False, ""
    for dp, dn, fn in os.walk(d):
        dn[:] = [x for x in dn if x not in (".git", "node_modules")]
        for f in fn:
            p = os.path.join(dp, f)
            ext = os.path.splitext(f)[1]
            rel = os.path.relpath(p, d)
            if ext in SCRIPT_EXT:
                scripts.add(rel)
            if ext not in TEXT_EXT:
                continue
            t = open(p, encoding="utf-8", errors="ignore").read()
            text += t
            if ext == ".md" and SHELL_BLOCK.search(t):
                shell = True
            src = t if ext != ".md" else "\n".join((m.group(1) or m.group(2) or "") for m in CODE.finditer(t))
            for rx, kind in PKG:
                for m in re.finditer(rx, src):
                    for name in clean_tokens(m.group(1)):
                        pkg.setdefault(f"{kind}: {name}", None)
            if f == "requirements.txt":
                for line in t.splitlines():
                    line = line.split("#")[0].strip()
                    if line and not line.startswith("-"):
                        pkg.setdefault("pip: " + re.split(r"[<>=!~\[ ;]", line)[0], None)
            if f == "package.json":
                j = load_json(p, {}) or {}
                for k in list(j.get("dependencies", {})) + list(j.get("devDependencies", {})):
                    pkg.setdefault("npm: " + k, None)
    dep = []
    if "CLAUDE_PLUGIN_ROOT" in text:
        dep.append("plugin_root")
    if re.search(r"\]\(\.\./|\.\./\.\./|\.\./(?:references|scripts|shared|skills)", text):
        dep.append("parent_path")
    if "~~" in text:
        dep.append("connector_placeholder")
    con = {}
    mcp = load_json(os.path.join(loc["_base"], loc["_plugin_dir"], ".mcp.json"))
    if isinstance(mcp, dict):
        servers = mcp.get("mcpServers", mcp)
        for k, v in servers.items():
            host = ""
            if isinstance(v, dict):
                if v.get("url"):
                    host = urllib.parse.urlparse(v["url"]).netloc
                elif v.get("command"):
                    host = "local: " + " ".join([v["command"]] + [a for a in v.get("args", []) if not str(a).startswith("-")][:2])
            con[k] = host
    return {"pkg": [x for x in pkg if x not in noise][:40], "cmd": sorted(scripts)[:30], "sh": shell,
            "dep": dep, "con": [{"k": k, "h": h} for k, h in con.items()]}


# ---------- update ----------

def cmd_update(args):
    cfg = load_json(CONFIG)
    areas = load_json(AREAS, {"plugin": {}, "skill": {}})
    old = load_json(DATA, []) or []
    noise = set(cfg.get("package_noise", []))
    locs = discover(cfg, not args.no_fetch)

    groups = collections.OrderedDict()
    for loc in sorted(locs, key=lambda l: (l["o"], l["r"], l["path"])):
        fm = frontmatter(os.path.join(loc["_base"], loc["path"], "SKILL.md"))
        name = str(fm.get("name") or os.path.basename(loc["path"])).strip()
        desc = " ".join(str(fm.get("description", "")).split())
        groups.setdefault((name, desc), []).append(loc)

    old_by_loc = {}
    for e in old:
        for l in e["loc"]:
            old_by_loc[(l["o"], l["r"], l["path"])] = e

    out, used_old, novos, revisar = [], set(), [], []
    for (name, desc), ls in groups.items():
        sc = {"pkg": [], "cmd": [], "sh": False, "dep": [], "con": []}
        for l in ls:
            s = scan(l, noise)
            for k in ("pkg", "cmd", "dep"):
                sc[k] += [x for x in s[k] if x not in sc[k]]
            sc["sh"] = sc["sh"] or s["sh"]
            have = {c["k"] for c in sc["con"]}
            sc["con"] += [c for c in s["con"] if c["k"] not in have]
        prev = next((old_by_loc[k] for k in ((l["o"], l["r"], l["path"]) for l in ls) if k in old_by_loc), None)
        l0 = ls[0]
        area = (prev or {}).get("a") or areas["skill"].get(name) if l0["r"] == "skills" else None
        if not area:
            area = (prev or {}).get("a") or areas["plugin"].get(f"{l0['r']}:{l0['p']}") or ""
        e = {"n": name, "pt": (prev or {}).get("pt", ""), "en": desc, "a": area,
             "loc": [{k: v for k, v in l.items() if not k.startswith("_")} for l in ls], **sc}
        if prev is None:
            e["status"] = "novo"
            novos.append(name)
        elif prev.get("en") != desc:
            e["status"] = "descricao_mudou"
            e["en_anterior"] = prev.get("en")
            revisar.append(name)
        elif prev.get("status") and not prev.get("pt"):
            e["status"] = prev["status"]
        if prev is not None:
            used_old.add(id(prev))
        out.append(e)

    removidos = [e["n"] for e in old if id(e) not in used_old]
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump(out, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    report = {
        "data": datetime.date.today().isoformat(),
        "total": len(out),
        "nomes_distintos": len({e["n"] for e in out}),
        "arquivos_skill": len(locs),
        "por_repositorio": dict(collections.Counter(f"{e['loc'][0]['o']}/{e['loc'][0]['r']}" for e in out)),
        "novos": novos,
        "descricao_mudou": revisar,
        "removidos": removidos,
        "sem_resumo": [e["n"] for e in out if not e["pt"]],
        "sem_area": [e["n"] for e in out if not e["a"]],
    }
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}, ensure_ascii=False, indent=1))
    if novos or revisar or removidos:
        print("\nPendências em data/report.json. Rode 'python3 scripts/catalog.py check' para ver os detalhes.")


def cmd_check(args):
    data = load_json(DATA, [])
    pend = [e for e in data if not e.get("pt") or not e.get("a") or e.get("status")]
    if not pend:
        print("Nada pendente.")
        return
    for e in pend:
        l = e["loc"][0]
        print(f"[{e.get('status') or 'incompleto'}] {e['n']}  ({l['o']}/{l['r']} {l['path']})")
        if not e.get("a"):
            print("  falta área")
        if not e.get("pt"):
            print("  falta resumo em português")
        if e.get("en_anterior"):
            print(f"  descrição anterior: {e['en_anterior'][:200]}")
        print(f"  descrição atual: {e['en'][:300]}")


# ---------- build ----------

def cmd_build(args):
    data = load_json(DATA, [])
    missing = [e["n"] for e in data if not e.get("pt") or not e.get("a")]
    if missing and not args.allow_missing:
        sys.exit("Faltam resumo ou área em: " + ", ".join(missing) + "\nPreencha em data/skills.json ou use --allow-missing.")
    pub = []
    for e in data:
        e = {k: v for k, v in e.items() if k not in ("status", "en_anterior")}
        if not e.get("pt"):
            e["pt"] = e["en"][:220]
        if not e.get("a"):
            e["a"] = "Outras"
        pub.append(e)
    tpl = open(TEMPLATE, encoding="utf-8").read()
    payload = json.dumps(pub, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = tpl.replace("__DATA__", payload).replace("__DATE__", datetime.date.today().strftime("%d/%m/%Y"))
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"index.html gerado com {len(pub)} skills.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update")
    u.add_argument("--no-fetch", action="store_true", help="usa o que já está em .cache sem baixar de novo")
    b = sub.add_parser("build")
    b.add_argument("--allow-missing", action="store_true", help="gera mesmo com resumo ou área faltando")
    sub.add_parser("check")
    a = ap.parse_args()
    {"update": cmd_update, "build": cmd_build, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
