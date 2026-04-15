#!/usr/bin/env python3
"""
Synaptic CLI — AI Conversation Intelligence from the Terminal

Analyze your ChatGPT / Claude conversation exports:
  - Extract entities, topics, and relationships
  - Build a knowledge graph
  - Export to multiple formats (JSON, CSV, Mermaid, MemPalace)
  - Beautiful terminal output

Usage:
    python synaptic.py analyze conversations.json
    python synaptic.py analyze conversations.json --format csv --output report.csv
    python synaptic.py graph conversations.json --output graph.mermaid
    python synaptic.py stats conversations.json
    python synaptic.py export conversations.json --format mempalace

100% offline · Zero API calls · MIT License
"""

import json
import re
import sys
import os
import csv
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# ─── ANSI Colors ───
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLUE    = "\033[38;5;69m"
    PURPLE  = "\033[38;5;141m"
    CYAN    = "\033[38;5;43m"
    PINK    = "\033[38;5;205m"
    ORANGE  = "\033[38;5;208m"
    YELLOW  = "\033[38;5;221m"
    GREEN   = "\033[38;5;114m"
    GRAY    = "\033[38;5;245m"
    WHITE   = "\033[38;5;255m"
    BG_CARD = "\033[48;5;236m"

TYPE_COLORS = {
    "person":  C.BLUE,
    "tech":    C.PURPLE,
    "concept": C.CYAN,
    "org":     C.ORANGE,
    "place":   C.PINK,
    "topic":   C.YELLOW,
    "project": C.GREEN,
}

# ─── Stop words & tech terms ───
STOP_WORDS = {
    "the","a","an","is","are","was","were","be","been","being","have","has","had",
    "do","does","did","will","would","shall","should","may","might","can","could",
    "i","you","he","she","it","we","they","me","him","her","us","them","my","your",
    "his","its","our","their","this","that","these","those","what","which","who",
    "whom","where","when","why","how","not","no","nor","but","and","or","if","then",
    "else","for","from","to","in","on","at","by","with","about","as","of","into",
    "through","during","before","after","above","below","between","out","off","over",
    "under","again","further","just","also","very","often","too","so","than","some",
    "such","only","own","same","both","each","few","more","most","other","any","all",
    "here","there","up","down","get","got","make","made","like","know","think","want",
    "need","use","using","used","try","said","tell","told","help","really","thing",
    "things","going","way","much","well","back","one","two","even","new","because",
    "good","great","right","still","many","now","come","take","say","see","look",
    "give","let","something","sure","please","okay","thanks","thank","yeah","yes",
    "could","should","would","might","also","however","example","question","answer",
    "code","file","work","working","create","add","change","update","write","read",
    "time","real","first","step","perfect","great","system","based","support",
    "data","model","using","team","type","server","services","pipeline","local",
    "build","project","handle","tool","tools","layer","approach","pattern",
    "format","deploy","setup","process","client","query","queries","feature",
    "tracking","state","management","routing","testing","running","simple",
    "entire","function","directly","provides","instead","another","across",
    "application","combined","separate","different","specific","completely",
    "recommend","structure","integrate","implement","configure","conversion",
    "excellent","perfect","beautiful","handling","processing","environment",
}

TECH_TERMS = {
    "react","javascript","typescript","python","rust","golang","node","nextjs","vue",
    "angular","svelte","django","flask","fastapi","express","docker","kubernetes",
    "aws","gcp","azure","postgres","mongodb","redis","graphql","rest","api","css",
    "html","tailwind","webpack","vite","git","github","linux","tensorflow","pytorch",
    "openai","anthropic","claude","gpt","llm","langchain","vector","embedding",
    "chromadb","sqlite","supabase","vercel","netlify","figma","notion","slack",
    "mcp","rag","transformer","bert","diffusion","cuda","wasm","webgl",
    "pandas","numpy","scipy","matplotlib","jupyter","conda","pip","npm","yarn",
    "deno","bun","zig","elixir","phoenix","rails","ruby","swift","kotlin",
    "java","scala","haskell","ocaml","clojure","sql","nosql","firebase",
    "kafka","rabbitmq","nginx","terraform","ansible","prometheus","grafana",
    "postgresql","elasticsearch","sqlalchemy","clickhouse","timescaledb",
    "langchain","chromadb","mlflow","sagemaker","databricks","airflow",
    "celery","gunicorn","uvicorn","pydantic","alembic","mongoose",
    "prisma","drizzle","trpc","remix","astro","solid","qwik",
}


# ─── Helpers ───

def _safe_parse_date(value) -> datetime:
    """Safely parse a date string, returning datetime.now() on failure."""
    if not value:
        return datetime.now()
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        s = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError, OSError):
        return datetime.now()


# ─── Parsers ───

def parse_chatgpt(data: list) -> list:
    """Parse ChatGPT export format."""
    conversations = []
    for conv in data:
        if not isinstance(conv, dict):
            continue
        title = conv.get("title", "Untitled")
        created = conv.get("create_time")
        created_dt = datetime.fromtimestamp(created) if created else datetime.now()
        messages = []

        mapping = conv.get("mapping", {})
        if mapping:
            for node in mapping.values():
                msg = node.get("message")
                if not msg:
                    continue
                content_obj = msg.get("content", {})
                parts = content_obj.get("parts", [])
                text = " ".join(p for p in parts if isinstance(p, str)).strip()
                if text:
                    role = msg.get("author", {}).get("role", "unknown")
                    messages.append({"role": role, "content": text})
        elif "messages" in conv:
            for m in conv["messages"]:
                messages.append({
                    "role": m.get("role", m.get("sender", "unknown")),
                    "content": m.get("content", m.get("text", "")),
                })

        if messages:
            conversations.append({
                "title": title,
                "messages": messages,
                "created": created_dt,
                "source": "chatgpt",
            })
    return conversations


def parse_claude(data: list) -> list:
    """Parse Claude export format."""
    conversations = []
    for conv in data:
        if not isinstance(conv, dict):
            continue
        title = conv.get("name", conv.get("title", "Untitled"))
        msgs_raw = conv.get("chat_messages", conv.get("messages", []))
        messages = []
        for m in msgs_raw:
            text = m.get("text", m.get("content", ""))
            if isinstance(text, list):
                text = " ".join(t.get("text", "") if isinstance(t, dict) else str(t) for t in text)
            if text.strip():
                messages.append({
                    "role": m.get("sender", m.get("role", "unknown")),
                    "content": text.strip(),
                })
        if messages:
            conversations.append({
                "title": title,
                "messages": messages,
                "created": _safe_parse_date(conv.get("created_at")),
                "source": "claude",
            })
    return conversations


def parse_auto(data: Any) -> list:
    """Auto-detect and parse conversation data."""
    if isinstance(data, dict):
        for key in ("conversations", "chats", "data"):
            if key in data and isinstance(data[key], list):
                return parse_auto(data[key])
        return []

    if not isinstance(data, list) or len(data) == 0:
        return []

    first = data[0]
    if isinstance(first, dict):
        if "mapping" in first:
            return parse_chatgpt(data)
        if "chat_messages" in first:
            return parse_claude(data)
        if "messages" in first:
            return parse_chatgpt(data)  # Generic format similar to ChatGPT

    return []


# ─── Entity Extraction ───

_MULTI_WORD_TECH = {
    "react native", "vue.js", "next.js", "node.js", "ruby on rails",
    "apache kafka", "apache spark", "apache flink", "apache airflow",
    "google cloud", "amazon web", "azure devops", "visual studio",
    "machine learning", "deep learning", "natural language",
    "open source", "real time", "full stack", "front end", "back end",
    "red hat", "digital ocean", "cloud run", "app engine",
    "spring boot", "entity framework", "ruby rails",
}

_TITLE_CASE_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "for", "with", "from", "this",
    "that", "these", "those", "your", "our", "their", "its", "his", "her",
    "also", "just", "very", "some", "each", "both", "such", "when", "then",
    "here", "there", "will", "would", "could", "should", "might", "let",
    "use", "using", "first", "then", "next", "after", "before",
    "testing", "setting", "building", "running", "getting", "creating", "adding",
}


_HTML_DANGEROUS = {
    "script", "alert", "onclick", "onerror", "onload", "onmouseover",
    "onfocus", "onblur", "iframe", "embed", "vbscript", "expression",
    "applet",
}

_HTML_TAG_RE = re.compile(r"<[^>]{1,200}>")


def extract_entities(text: str) -> dict:
    """Extract named entities from text using pattern matching."""
    entities = {}

    # Strip HTML tags to prevent XSS-derived entity extraction
    text = _HTML_TAG_RE.sub(" ", text)

    # Proper nouns (capitalized multi-word)
    for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text):
        name = match.group(1)
        # Strip leading title-case stop words (e.g. "The Tailwind" -> "Tailwind")
        words = name.split()
        while words and words[0].lower() in _TITLE_CASE_STOPWORDS:
            words = words[1:]
        if len(words) < 2:
            continue  # Need at least 2 words for a proper noun phrase
        name = " ".join(words)
        key = name.lower()
        if key not in STOP_WORDS and len(name) > 3 and key not in _MULTI_WORD_TECH:
            entities.setdefault(key, {"name": name, "type": "person", "count": 0})
            entities[key]["count"] += 1

    # Tech terms — use ASCII-only fragments (no \b) to handle multilingual text
    # e.g. "FastAPIとJinja2テンプレート" → ["fastapi", "jinja2"]
    lower_text = text.lower()
    words = re.findall(r"[a-z][a-z0-9.#+]+", lower_text)
    for w in words:
        if w in TECH_TERMS:
            entities.setdefault(w, {"name": w, "type": "tech", "count": 0})
            entities[w]["count"] += 1

    # Quoted terms
    for match in re.finditer(r'"([^"]{3,40})"', text):
        term = match.group(1).strip().lower()
        if term not in STOP_WORDS and len(term) > 2:
            entities.setdefault(term, {"name": term, "type": "concept", "count": 0})
            entities[term]["count"] += 1

    # Frequent non-stop words (filter out HTML-dangerous words)
    freq = Counter(w for w in words if w not in STOP_WORDS and w not in TECH_TERMS and len(w) > 3 and w not in _HTML_DANGEROUS)
    for word, count in freq.most_common(30):
        if count >= 2 and word not in entities:
            entities[word] = {"name": word, "type": "concept", "count": count}

    return entities


def build_graph(conversations: list) -> dict:
    """Build a knowledge graph from conversations."""
    global_entities = {}
    cooccurrences = Counter()

    for ci, conv in enumerate(conversations):
        text = " ".join(m["content"] for m in conv["messages"])
        ents = extract_entities(text)

        keys = list(ents.keys())
        for k in keys:
            if k not in global_entities:
                global_entities[k] = {**ents[k], "conversations": set(), "id": k}
            global_entities[k]["count"] = global_entities[k].get("count", 0) + ents[k]["count"]
            global_entities[k]["conversations"].add(ci)

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                pair = tuple(sorted([keys[i], keys[j]]))
                cooccurrences[pair] += 1

    # Top entities
    sorted_entities = sorted(global_entities.values(), key=lambda e: e["count"], reverse=True)[:120]
    entity_set = {e["id"] for e in sorted_entities}

    # Links
    links = []
    for (s, t), weight in cooccurrences.most_common():
        if s in entity_set and t in entity_set:
            links.append({"source": s, "target": t, "weight": weight})
        if len(links) >= 300:
            break

    # Convert sets to lists for serialization
    for e in sorted_entities:
        e["conversations"] = list(e["conversations"])

    return {"entities": sorted_entities, "links": links}


# ─── Output Formatters ───

def print_header():
    """Print the Synaptic header."""
    print()
    print(f"  {C.BOLD}{C.BLUE}S Y N A P T I C{C.RESET}")
    print(f"  {C.DIM}AI Conversation Intelligence{C.RESET}")
    print(f"  {C.DIM}{'─' * 40}{C.RESET}")
    print()


def print_stats(conversations: list, graph: dict):
    """Print overview statistics."""
    entities = graph["entities"]
    links = graph["links"]

    total_msgs = sum(len(c["messages"]) for c in conversations)
    total_words = sum(len(m["content"].split()) for c in conversations for m in c["messages"])
    sources = Counter(c.get("source", "unknown") for c in conversations)

    print(f"  {C.BOLD}Overview{C.RESET}")
    print(f"  {C.GRAY}{'─' * 36}{C.RESET}")
    print(f"  Conversations    {C.BOLD}{C.WHITE}{len(conversations)}{C.RESET}")
    print(f"  Total messages   {C.BOLD}{C.WHITE}{total_msgs}{C.RESET}")
    print(f"  Total words      {C.BOLD}{C.WHITE}{total_words:,}{C.RESET}")
    print(f"  Entities found   {C.BOLD}{C.CYAN}{len(entities)}{C.RESET}")
    print(f"  Relationships    {C.BOLD}{C.PURPLE}{len(links)}{C.RESET}")
    print(f"  Sources          {C.GRAY}{', '.join(f'{k}({v})' for k, v in sources.items())}{C.RESET}")
    print()


def print_top_entities(graph: dict, limit: int = 20):
    """Print top entities with bar chart."""
    entities = sorted(graph["entities"], key=lambda e: e["count"], reverse=True)[:limit]
    if not entities:
        return

    max_count = entities[0]["count"]
    max_bar = 30

    print(f"  {C.BOLD}Top Entities{C.RESET}")
    print(f"  {C.GRAY}{'─' * 36}{C.RESET}")

    for e in entities:
        bar_len = int((e["count"] / max_count) * max_bar)
        color = TYPE_COLORS.get(e["type"], C.GRAY)
        bar = "█" * bar_len + "░" * (max_bar - bar_len)
        name = e["name"][:20].ljust(20)
        print(f"  {color}●{C.RESET} {name} {color}{bar}{C.RESET} {C.DIM}{e['count']}{C.RESET}")

    print()


def print_connections(graph: dict, limit: int = 15):
    """Print top connections."""
    conn_count = Counter()
    for link in graph["links"]:
        conn_count[link["source"]] += 1
        conn_count[link["target"]] += 1

    entity_map = {e["id"]: e for e in graph["entities"]}
    top = conn_count.most_common(limit)

    if not top:
        return

    max_conn = top[0][1]

    print(f"  {C.BOLD}Hub Entities (Most Connected){C.RESET}")
    print(f"  {C.GRAY}{'─' * 36}{C.RESET}")

    for eid, count in top:
        e = entity_map.get(eid)
        if not e:
            continue
        bar_len = int((count / max_conn) * 25)
        color = TYPE_COLORS.get(e["type"], C.GRAY)
        name = e["name"][:20].ljust(20)
        print(f"  {color}◆{C.RESET} {name} {C.PURPLE}{'━' * bar_len}{C.RESET} {C.DIM}{count} links{C.RESET}")

    print()


def export_csv(graph: dict, output_path: str):
    """Export entities and links to CSV."""
    ent_path = output_path.replace(".csv", "_entities.csv")
    link_path = output_path.replace(".csv", "_links.csv")

    with open(ent_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "type", "count", "conversations"])
        for e in graph["entities"]:
            writer.writerow([e["id"], e["name"], e["type"], e["count"], len(e["conversations"])])

    with open(link_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "weight"])
        for l in graph["links"]:
            writer.writerow([l["source"], l["target"], l["weight"]])

    print(f"  {C.GREEN}✓{C.RESET} Entities → {ent_path}")
    print(f"  {C.GREEN}✓{C.RESET} Links    → {link_path}")


def export_mermaid(graph: dict, output_path: str):
    """Export as Mermaid diagram."""
    lines = ["graph TD"]

    # Add top 40 entities as nodes
    entities = sorted(graph["entities"], key=lambda e: e["count"], reverse=True)[:40]
    entity_ids = {e["id"] for e in entities}

    for e in entities:
        safe_id = re.sub(r"[^a-zA-Z0-9]", "_", e["id"])
        label = re.sub(r'["\(\)\[\]\{\}<>#]', "", e["name"])
        if e["type"] == "tech":
            lines.append(f'    {safe_id}["{label}"]:::tech')
        elif e["type"] == "person":
            lines.append(f'    {safe_id}("{label}"):::person')
        else:
            lines.append(f'    {safe_id}["{label}"]:::concept')

    # Add links
    for link in graph["links"][:80]:
        s = link["source"]
        t = link["target"]
        if s in entity_ids and t in entity_ids:
            safe_s = re.sub(r"[^a-zA-Z0-9]", "_", s)
            safe_t = re.sub(r"[^a-zA-Z0-9]", "_", t)
            if link["weight"] > 2:
                lines.append(f"    {safe_s} ==> {safe_t}")
            else:
                lines.append(f"    {safe_s} --> {safe_t}")

    # Styles
    lines.append("")
    lines.append("    classDef tech fill:#8b5cf6,stroke:#6d3fc7,color:white")
    lines.append("    classDef person fill:#4e7cff,stroke:#3a5ecc,color:white")
    lines.append("    classDef concept fill:#06d6a0,stroke:#04a37a,color:white")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  {C.GREEN}✓{C.RESET} Mermaid graph → {output_path}")


def export_json(graph: dict, conversations: list, output_path: str):
    """Export full analysis as JSON."""
    output = {
        "meta": {
            "generated_by": "synaptic",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "conversations_count": len(conversations),
        },
        "entities": graph["entities"],
        "links": graph["links"],
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"  {C.GREEN}✓{C.RESET} Full analysis → {output_path}")


def export_mempalace(graph: dict, conversations: list, output_path: str):
    """Export in a format compatible with MemPalace import."""
    # Structure entities into a palace hierarchy
    palace = {
        "palace_name": "synaptic_import",
        "generated_by": "synaptic",
        "version": "1.0.0",
        "wings": {},
    }

    # Group by entity type into wings
    type_groups = defaultdict(list)
    for e in graph["entities"]:
        type_groups[e["type"]].append(e)

    for etype, entities in type_groups.items():
        wing = {
            "name": etype,
            "rooms": {},
        }
        for e in entities[:30]:
            room = {
                "name": e["name"],
                "drawers": [],
            }
            # Add conversation excerpts as drawers
            for ci in e["conversations"][:5]:
                if ci < len(conversations):
                    conv = conversations[ci]
                    excerpt = " ".join(m["content"][:200] for m in conv["messages"][:2])
                    room["drawers"].append({
                        "source_conversation": conv["title"],
                        "content": excerpt[:500],
                    })
            wing["rooms"][e["name"]] = room
        palace["wings"][etype] = wing

    with open(output_path, "w") as f:
        json.dump(palace, f, indent=2, default=str)

    print(f"  {C.GREEN}✓{C.RESET} MemPalace format → {output_path}")


# ─── CLI Commands ───

def _parse_args(args: list, defaults: dict = None) -> dict:
    """Parse --key value pairs from argument list. Returns dict of parsed flags."""
    result = defaults or {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            key = args[i][2:]  # strip --
            result[key] = args[i + 1]
            i += 2
        else:
            i += 1
    return result


def _load_json(filepath: str):
    """Safely load a JSON file. Returns (data, None) on success or (None, error_msg) on failure."""
    if not os.path.isfile(filepath):
        return None, f"File not found: {filepath}"
    try:
        with open(filepath) as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"
    except PermissionError:
        return None, f"Permission denied: {filepath}"
    except OSError as e:
        return None, f"Could not read file: {e}"


def _load_conversations(filepath: str):
    """Load and parse conversations from a file. Returns (conversations, graph) or prints error and returns None."""
    print(f"  {C.DIM}Loading {filepath}...{C.RESET}")
    data, err = _load_json(filepath)
    if err:
        print(f"  {C.PINK}Error:{C.RESET} {err}")
        sys.exit(2)

    conversations = parse_auto(data)
    if not conversations:
        print(f"  {C.PINK}Error:{C.RESET} Could not parse conversations from file.")
        print(f"  {C.DIM}Ensure it's a ChatGPT or Claude JSON export.{C.RESET}")
        sys.exit(2)

    print(f"  {C.GREEN}✓{C.RESET} Parsed {len(conversations)} conversations")
    graph = build_graph(conversations)
    return conversations, graph


def _safe_write(fn, *args, **kwargs):
    """Wrap an export function with error handling for write operations."""
    try:
        fn(*args, **kwargs)
    except PermissionError:
        print(f"  {C.PINK}Error:{C.RESET} Permission denied writing output file")
    except OSError as e:
        print(f"  {C.PINK}Error:{C.RESET} Could not write file: {e}")


def cmd_analyze(args: list):
    """Analyze conversations and show results."""
    if not args:
        print(f"  {C.PINK}Error:{C.RESET} Please provide a JSON file path")
        return

    filepath = args[0]
    flags = _parse_args(args[1:], {"format": "terminal"})
    fmt = flags.get("format", "terminal")
    output = flags.get("output")

    conversations, graph = _load_conversations(filepath)
    if not conversations:
        return

    print()

    if fmt == "terminal" or not output:
        print_stats(conversations, graph)
        print_top_entities(graph)
        print_connections(graph)
    elif fmt == "csv":
        _safe_write(export_csv, graph, output or "synaptic_report.csv")
    elif fmt == "json":
        _safe_write(export_json, graph, conversations, output or "synaptic_analysis.json")
    elif fmt == "mempalace":
        _safe_write(export_mempalace, graph, conversations, output or "synaptic_mempalace.json")
    else:
        print(f"  {C.PINK}Error:{C.RESET} Unknown format '{fmt}'. Use: terminal, csv, json, mempalace")


def cmd_graph(args: list):
    """Generate a knowledge graph in Mermaid format."""
    if not args:
        print(f"  {C.PINK}Error:{C.RESET} Please provide a JSON file path")
        return

    filepath = args[0]
    flags = _parse_args(args[1:], {"output": "synaptic_graph.mermaid"})
    output = flags.get("output", "synaptic_graph.mermaid")

    conversations, graph = _load_conversations(filepath)
    if not conversations:
        return

    _safe_write(export_mermaid, graph, output)


def cmd_stats(args: list):
    """Show quick statistics."""
    if not args:
        print(f"  {C.PINK}Error:{C.RESET} Please provide a JSON file path")
        return

    conversations, graph = _load_conversations(args[0])
    if not conversations:
        return

    print()
    print_stats(conversations, graph)


def cmd_export(args: list):
    """Export to various formats."""
    if len(args) < 1:
        print(f"  {C.PINK}Error:{C.RESET} Usage: synaptic export <file> --format <json|csv|mermaid|mempalace>")
        return

    filepath = args[0]
    flags = _parse_args(args[1:], {"format": "json"})
    fmt = flags.get("format", "json")
    output = flags.get("output")

    conversations, graph = _load_conversations(filepath)
    if not conversations:
        return

    if fmt == "csv":
        _safe_write(export_csv, graph, output or "synaptic_export.csv")
    elif fmt == "mermaid":
        _safe_write(export_mermaid, graph, output or "synaptic_graph.mermaid")
    elif fmt == "mempalace":
        _safe_write(export_mempalace, graph, conversations, output or "synaptic_mempalace.json")
    elif fmt == "json":
        _safe_write(export_json, graph, conversations, output or "synaptic_analysis.json")
    else:
        print(f"  {C.PINK}Error:{C.RESET} Unknown format '{fmt}'. Use: json, csv, mermaid, mempalace")


def cmd_help():
    """Print help."""
    print(f"""
  {C.BOLD}Commands:{C.RESET}

    {C.CYAN}analyze{C.RESET} <file>                    Analyze & display results
      --format <terminal|csv|json>     Output format (default: terminal)
      --output <path>                  Output file path

    {C.CYAN}graph{C.RESET} <file>                      Generate Mermaid knowledge graph
      --output <path>                  Output file (default: synaptic_graph.mermaid)

    {C.CYAN}stats{C.RESET} <file>                      Quick statistics

    {C.CYAN}export{C.RESET} <file>                     Export analysis
      --format <json|csv|mermaid|mempalace>
      --output <path>

    {C.CYAN}help{C.RESET}                              Show this help

  {C.BOLD}Supported Formats:{C.RESET}
    ChatGPT export (Settings > Data Controls > Export)
    Claude export (Settings > Privacy > Export)
    Any JSON with a conversations/messages array

  {C.BOLD}Examples:{C.RESET}
    {C.DIM}python synaptic.py analyze conversations.json{C.RESET}
    {C.DIM}python synaptic.py graph export.json --output my_graph.mermaid{C.RESET}
    {C.DIM}python synaptic.py export data.json --format mempalace{C.RESET}
""")


def main():
    print_header()

    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "analyze": cmd_analyze,
        "graph": cmd_graph,
        "stats": cmd_stats,
        "export": cmd_export,
        "help": lambda _: cmd_help(),
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"  {C.PINK}Unknown command:{C.RESET} {command}")
        cmd_help()

    print()


if __name__ == "__main__":
    main()
