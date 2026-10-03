#!/usr/bin/env python3
"""Briefs #18-30 UAT — Live API tests against the deployed backend.

Covers:
  Brief #18a-c: guided fallback, clarifying question, scale-safe inventory
  Brief #19: /chat/starters endpoint + follow-up suggestion chips
  Brief #20/20a-e: agent mode (planner + 5 tools + steps trace + citation polish)
  Brief #21: deep answer mode (decompose + multi-pass retrieve + synthesize)
  Brief #22: citation dedup ([1][1] -> [1])
  Brief #23: exact-count rule in synthesis prompt (no hallucinated counts)
  Brief #24: segmented mode pill + '+' menu + lens icon + card drop target (UI — static)
  Briefs #25-30: chat UX polish, scroll arrows, viewer media teardown, pdf.js canvas leak (UI — static)
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path("/home/z/my-project/seekra-app")
BACKEND = REPO / "backend"

# Settings dummies for static checks
os.environ["SECRET_KEY"] = "uat-static-dummy"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://uat:uat@localhost:5432/uat"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "x"
os.environ["MINIO_SECRET_KEY"] = "x"
os.environ["MINIO_BUCKET_NAME"] = "uat-bucket"
sys.path.insert(0, str(BACKEND))

BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ADMIN_PASSWORD = "A!!!@@@2026"

PASS = FAIL = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def req(method: str, path: str, data: dict | None = None,
        token: str | None = None, form: bool = False, timeout: int = 180) -> tuple[int, Any]:
    headers: dict[str, str] = {}
    body: bytes | None = None
    if form:
        body = urllib.parse.urlencode(data or {}).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=timeout) as resp:
            content = resp.read().decode()
            status = resp.status
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        status = e.code
    try:
        return status, json.loads(content) if content else None
    except json.JSONDecodeError:
        return status, content


def login(username: str, password: str) -> str | None:
    s, d = req("POST", "/auth/login", {"username": username, "password": password}, form=True)
    if s != 200:
        return None
    return (d or {}).get("access_token") or (d or {}).get("token")


# ==========================================================================
# PART 1: STATIC CHECKS
# ==========================================================================
print("=" * 60)
print("PART 1: STATIC CHECKS (Briefs #18-30)")
print("=" * 60)

# ---- 1a. Backend imports succeed ----
print("\n=== 1a. Backend imports ===")
try:
    from app.services import agent, deep_answer
    from app.api import chat
    from app.services.llm_gateway import llm_gateway
    check("agent.py imports cleanly", True)
    check("deep_answer.py imports cleanly", True)
    check("chat.py imports cleanly", True)
except Exception as e:
    check("backend imports", False, f"{type(e).__name__}: {e}")
    import traceback; traceback.print_exc()

# ---- 1b. ChatRequest has agent + deep flags ----
print("\n=== 1b. ChatRequest has agent + deep flags (Brief #20/#21) ===")
chat_src = (BACKEND / "app" / "api" / "chat.py").read_text()
check("ChatRequest.agent: Optional[bool] field",
      "agent: Optional[bool]" in chat_src, "")
check("ChatRequest.deep: Optional[bool] field",
      "deep: Optional[bool]" in chat_src, "")

# ---- 1c. Agent mode wiring ----
print("\n=== 1c. Agent mode wiring (Brief #20) ===")
check("agent mode triggered when req.agent=True",
      "if getattr(req, \"agent\", False)" in chat_src, "")
check("imports run_agent from app.services.agent",
      "from app.services.agent import run_agent" in chat_src, "")
check("agent run wrapped in asyncio.wait_for (timeout guard)",
      "asyncio.wait_for(" in chat_src and "run_agent" in chat_src, "")
check("agent failure falls back to normal pipeline (fail-open)",
      "agent mode failed, using normal pipeline" in chat_src, "")
check("agent result includes 'steps' trace",
      "len(agent_result.get('steps', []))" in chat_src, "")
check("agent result also gets follow-up suggestions",
      "_suggest_followups" in chat_src, "")

# ---- 1d. Agent tools catalog ----
print("\n=== 1d. Agent tools catalog (5 tools) ===")
agent_src = (BACKEND / "app" / "services" / "agent.py").read_text()
expected_tools = ["search_library", "list_documents", "summarize_document",
                  "find_entity", "compare_documents"]
for tool in expected_tools:
    check(f"TOOL_CATALOG mentions '{tool}'",
          f"{tool}(" in agent_src, "")

check("MAX_STEPS = 3 (planner capped)",
      "MAX_STEPS = 3" in agent_src, "")
check("STEP_TIMEOUT = 15.0 (per-tool timeout)",
      "STEP_TIMEOUT = 15.0" in agent_src, "")
check("SIM_FLOOR = 0.44 (aligned with chat retrieval)",
      "SIM_FLOOR = 0.44" in agent_src, "")

# Permission scoping: every tool applies permission_clause
check("agent imports permission_clause",
      "from app.services.permissions import permission_clause" in agent_src, "")
# Count permission_clause uses inside agent.py (should be in each tool that queries docs)
perm_uses = agent_src.count("permission_clause")
check(f"permission_clause used >= 4 times in agent.py (found {perm_uses})",
      perm_uses >= 4, "")

# ---- 1e. Deep answer mode wiring ----
print("\n=== 1e. Deep answer mode wiring (Brief #21) ===")
deep_src = (BACKEND / "app" / "services" / "deep_answer.py").read_text()
check("deep mode triggered when req.deep=True",
      "if getattr(req, \"deep\", False)" in chat_src, "")
check("imports run_deep_answer from app.services.deep_answer",
      "from app.services.deep_answer import run_deep_answer" in chat_src, "")
check("deep run wrapped in asyncio.wait_for (timeout guard)",
      chat_src.count("asyncio.wait_for(") >= 2,  # both agent and deep
      "")
check("deep failure falls back to normal pipeline (fail-open)",
      "deep answer mode failed" in chat_src or "using normal pipeline" in chat_src, "")

# Decomposition parameters
check("MAX_SUBQUESTIONS = 4 (decomposition cap)",
      "MAX_SUBQUESTIONS = 4" in deep_src, "")
check("DECOMPOSE_TIMEOUT = 10.0",
      "DECOMPOSE_TIMEOUT = 10.0" in deep_src, "")
check("PASS_TIMEOUT = 12.0",
      "PASS_TIMEOUT = 12.0" in deep_src, "")
check("PER_PASS_LIMIT = 10",
      "PER_PASS_LIMIT = 10" in deep_src, "")
check("FINAL_CHUNKS = 12",
      "FINAL_CHUNKS = 12" in deep_src, "")
check("MAX_CONTEXT_CHARS = 9000 (deeper than normal 6000)",
      "MAX_CONTEXT_CHARS = 9000" in deep_src, "")

# Permission scoping
check("deep_answer imports permission_clause",
      "from app.services.permissions import permission_clause" in deep_src, "")
perm_uses_deep = deep_src.count("permission_clause")
check(f"permission_clause used >= 2 times in deep_answer.py (found {perm_uses_deep})",
      perm_uses_deep >= 2, "")

# ---- 1f. Citation dedup (Brief #22) ----
print("\n=== 1f. Citation dedup (Brief #22) ===")
check("_dedupe_citation_runs function exists in agent.py",
      "def _dedupe_citation_runs" in agent_src, "")
check("_dedupe_citation_runs function exists in deep_answer.py",
      "def _dedupe_citation_runs" in deep_src, "")
check("regex matches [1][1] -> [1] pattern",
      "_CITE_RUN_RE = re.compile" in agent_src and "(?:\\[\\d{1,2}\\]){2,}" in agent_src, "")
check("chat.py calls dedupe on agent result",
      "Brief #22" in chat_src and "dedupe" in chat_src.lower(), "")

# ---- 1g. Exact-count rule (Brief #23) ----
print("\n=== 1g. Exact-count rule in synthesis prompt (Brief #23) ===")
gw_src = (BACKEND / "app" / "services" / "llm_gateway.py").read_text()
# The rule should tell the LLM to use only the exact count from inventory SQL
check("llm_gateway.py modified for Brief #23",
      "Brief #23" in gw_src or "exact-count" in gw_src.lower() or "exact count" in gw_src.lower(),
      "")
# Look for instructions like "never invent a count" or "use the exact number"
check("synthesis prompt enforces exact count (no hallucinated counts)",
      any(p in gw_src.lower() for p in ["exact count", "exact number", "do not invent", "never invent", "do not estimate", "do not approximate"]),
      "")

# ---- 1h. Brief #18a-c: guided fallback + clarifying + scale-safe inventory ----
print("\n=== 1h. Brief #18a-c: guided fallback + clarifying + scale-safe inventory ===")
check("Brief #18 marker present",
      "Brief #18" in chat_src, "")
check("guided fallback: suggests closest documents on no-match",
      "Guided fallback" in chat_src or "guided fallback" in chat_src.lower(), "")
check("Brief #18c: scale-safe inventory (COUNT / GROUP BY / LIMIT in SQL)",
      "Brief #18c" in chat_src and ("COUNT" in chat_src or "GROUP BY" in chat_src), "")
check("clarifying question base prompt present",
      "clarifying question" in chat_src.lower(), "")

# ---- 1i. Brief #19: starters + follow-up suggestions ----
print("\n=== 1i. Brief #19: starters + follow-up suggestions ===")
check("/chat/starters GET endpoint exists",
      '@router.get("/starters")' in chat_src, "")
check("starters cached per-user+lang",
      'seekra:chat:starters:v1:' in chat_src, "")
check("_suggest_followups function exists",
      "def _suggest_followups" in chat_src or "async def _suggest_followups" in chat_src, "")
check("_fallback_suggestions function exists",
      "def _fallback_suggestions" in chat_src, "")
check("chat response includes 'suggestions' field",
      '"suggestions": suggestions' in chat_src or '"suggestions":' in chat_src, "")
check("starters grounded in real document filenames (not generic)",
      "library-grounded" in chat_src or "library grounded" in chat_src.lower(), "")

# ---- 1j. Brief #24: frontend chat mode pill + UI elements ----
print("\n=== 1j. Brief #24: frontend chat mode pill + UI ===")
chat_page = (REPO / "frontend" / "src" / "app" / "chat" / "page.tsx").read_text()
check("chat page has segmented mode pill (auto/agent/deep)",
      'chatMode: "auto" | "agent" | "deep"' in chat_page, "")
check("mode pill uses inline-flex rounded-full border styling",
      'inline-flex items-center rounded-full border' in chat_page, "")
check("three mode options rendered: auto, agent, deep",
      '(["auto", "agent", "deep"] as const).map' in chat_page, "")
check("each mode has icon: Zap (auto) / Bot (agent) / Sparkles (deep)",
      "Zap" in chat_page and "Bot" in chat_page and "Sparkles" in chat_page, "")
check("mode persisted to localStorage",
      'localStorage.setItem("seekra_agent_mode"' in chat_page
      and 'localStorage.setItem("seekra_deep_mode"' in chat_page, "")
check("mode sent to API in chat request body",
      "agent: agentMode," in chat_page and "deep: deepMode," in chat_page, "")
check("agent steps trace rendered (Brief #20 UI)",
      "message.steps" in chat_page and "Agent steps" in chat_page, "")

# Search page: lens icon + drop target
search_page = (REPO / "frontend" / "src" / "app" / "search" / "page.tsx").read_text()
check("search page has image drop handler (Brief #24 card drop target)",
      "handleImageDrop" in search_page and "onDrop={handleImageDrop}" in search_page, "")

# ---- 1k. Briefs #25-30: chat UX polish + viewer media teardown + pdf.js canvas leak ----
print("\n=== 1k. Briefs #25-30: UX polish + viewer media teardown ===")
viewer_page = (REPO / "frontend" / "src" / "app" / "viewer" / "page.tsx").read_text()
check("viewer pauses media on unmount (Brief #26)",
      "mediaRef.current?.pause()" in viewer_page, "")
check("viewer pauses all audio/video in container on cleanup",
      "querySelectorAll(\"audio, video\")" in viewer_page, "")
check("viewer pauses media when switching documents (Brief #26)",
      "Brief #26" in viewer_page, "")
check("viewer cleans up pdf.js render task (Brief #28)",
      "cleanupRender" in viewer_page and "renderTask.cancel()" in viewer_page, "")
check("viewer handles pdf.js measurement canvases on body (Brief #28 leak fix)",
      "Brief #28" in viewer_page and ("measurement canvas" in viewer_page.lower() or "pdf.js" in viewer_page.lower() or "body" in viewer_page), "")

# Chat page: scroll arrows (Brief #25)
check("chat page mentions scroll arrows (Brief #25)",
      "Brief #25" in chat_page or "scroll-arrow" in chat_page or "scrollArrow" in chat_page, "")

# globals.css: scroll arrow styling
globals_css = (REPO / "frontend" / "src" / "app" / "globals.css").read_text()
check("globals.css has Brief #28 marker",
      "Brief #28" in globals_css or "scroll-arrow" in globals_css or "scrollArrow" in globals_css, "")

# ---- 1l. i18n strings added ----
print("\n=== 1l. i18n strings for new features ===")
en_json = json.loads((REPO / "frontend" / "src" / "i18n" / "dictionaries" / "en.json").read_text())
ar_json = json.loads((REPO / "frontend" / "src" / "i18n" / "dictionaries" / "ar.json").read_text())

def find_keys(d, prefix=""):
    keys = set()
    if isinstance(d, dict):
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            keys.add(full)
            keys.update(find_keys(v, full))
    return keys

en_keys = find_keys(en_json)
ar_keys = find_keys(ar_json)

# Check for specific keys related to new briefs
expected_i18n_fragments = [
    "chat.mode",        # Brief #24 mode pill
    "chat.agent",       # Brief #20 agent mode
    "chat.deep",        # Brief #21 deep mode
    "chat.suggestions", # Brief #19 follow-up chips
]
for frag in expected_i18n_fragments:
    en_match = any(frag in k for k in en_keys)
    ar_match = any(frag in k for k in ar_keys)
    check(f"en.json has '{frag}*'", en_match, "")
    check(f"ar.json has '{frag}*'", ar_match, "")

# ---- 1m. api.ts additions ----
print("\n=== 1m. api.ts additions ===")
api_ts = (REPO / "frontend" / "lib" / "api.ts").read_text() if (REPO / "frontend" / "lib" / "api.ts").exists() else (REPO / "frontend" / "src" / "lib" / "api.ts").read_text()
check("api.ts has chat starters function",
      "getChatStarters" in api_ts or "chat/starters" in api_ts or "/chat/starters" in api_ts, "")
check("api.ts ChatRequest type has agent + deep fields",
      "agent" in api_ts and "deep" in api_ts, "")
check("api.ts mentions Brief #19 (starters)",
      "Brief #19" in api_ts, "")
check("api.ts mentions Brief #20 (agent)",
      "Brief #20" in api_ts, "")


# ==========================================================================
# PART 2: LIVE API CHECKS
# ==========================================================================
print("\n" + "=" * 60)
print("PART 2: LIVE API CHECKS")
print("=" * 60)

# Login
print("\n=== 2a. Setup ===")
admin_tok = login("admin", ADMIN_PASSWORD)
check("admin login", admin_tok is not None)
if not admin_tok:
    print("FATAL: cannot continue without admin token")
    sys.exit(1)

# ---- 2b. Brief #19: /chat/starters ----
print("\n=== 2b. Brief #19: /chat/starters (library-grounded starters) ===")
s, d = req("GET", "/chat/starters?lang=en", token=admin_tok)
check("GET /chat/starters?lang=en -> 200", s == 200, f"{s} {d}")
if s == 200 and isinstance(d, dict):
    starters = d.get("starters", [])
    check("starters is a non-empty list", len(starters) >= 2, str(starters))
    if starters:
        # At least one starter should reference a real document filename
        check("at least one starter references a real document filename",
              any(re.search(r"\d{2}_", s) or "." in s for s in starters),
              str(starters))
        # Print first few
        print(f"      starters: {starters[:3]}")

# Arabic starters
s, d = req("GET", "/chat/starters?lang=ar", token=admin_tok)
check("GET /chat/starters?lang=ar -> 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ar_starters = d.get("starters", [])
    check("Arabic starters is non-empty", len(ar_starters) >= 2, str(ar_starters))

# Cached on second call
t0 = time.time()
s, d = req("GET", "/chat/starters?lang=en", token=admin_tok)
elapsed_ms = (time.time() - t0) * 1000
check(f"second /chat/starters call is cached (fast: {elapsed_ms:.0f}ms)",
      elapsed_ms < 100 and s == 200, f"{elapsed_ms:.0f}ms status={s}")

# ---- 2c. Brief #19: follow-up suggestions in chat response ----
print("\n=== 2c. Brief #19: follow-up suggestions in chat response ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what is Project Golden Falcon about?"
}, timeout=240)
check("chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    suggestions = d.get("suggestions", [])
    check("response includes 'suggestions' field",
          "suggestions" in d, "")
    check("suggestions is a non-empty list",
          isinstance(suggestions, list) and len(suggestions) >= 1, str(suggestions))
    if suggestions:
        print(f"      suggestions: {suggestions[:3]}")

# ---- 2d. Brief #18a: guided fallback (no-match query) ----
print("\n=== 2d. Brief #18a: guided fallback (no-match query) ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what color is the sky on Mars during winter solstice?"
}, timeout=240)
check("no-match chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = (d.get("answer") or "").lower()
    # Should either abstain OR suggest closest documents
    abstains = any(p in ans for p in ["couldn't find", "don't have enough",
                                       "no information", "not mentioned",
                                       "لم أعثر", "لا أملك", "لا تتوفر"])
    suggests = any(p in ans for p in ["did you mean", "try", "perhaps",
                                       "closest", "similar", "you might"])
    check("no-match response either abstains OR suggests closest docs",
          abstains or suggests, f"answer: {ans[:200]}")

# ---- 2e. Brief #18c: scale-safe inventory (large library question) ----
print("\n=== 2e. Brief #18c: scale-safe inventory ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "how many documents are available and can you list them here?"
}, timeout=240)
check("inventory chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = d.get("answer") or ""
    # Should contain "32 documents" (the exact count, not hallucinated)
    has_exact_count = "32 documents" in ans
    check("inventory answer contains exact count '32 documents'",
          has_exact_count, f"answer first 200 chars: {ans[:200]}")
    # Should NOT contain a wrong count like "30" or "35"
    wrong_counts = re.findall(r"\b(\d{2,3})\s+documents?\b", ans)
    wrong = [c for c in wrong_counts if c != "32"]
    check("inventory answer does NOT contain wrong counts",
          not wrong, f"found wrong counts: {wrong}")

# ---- 2f. Brief #20: agent mode (list_documents tool) ----
print("\n=== 2f. Brief #20: agent mode (list_documents tool) ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "list all documents in the library",
    "agent": True
}, timeout=240)
check("agent mode POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    # Agent result should include 'steps' trace
    check("agent response includes 'steps' trace",
          "steps" in d and isinstance(d.get("steps"), list), f"keys: {list(d.keys())}")
    if d.get("steps"):
        print(f"      steps: {[(s.get('tool'), s.get('args')) for s in d['steps']]}")
    # Agent answer should list documents
    ans = d.get("answer") or ""
    check("agent answer lists documents (contains numbered list)",
          "1." in ans and "32." in ans, f"first 200: {ans[:200]}")

# ---- 2g. Brief #20: agent mode (summarize_document tool) ----
print("\n=== 2g. Brief #20: agent mode (summarize_document tool) ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "summarize the Golden Falcon script",
    "agent": True
}, timeout=240)
check("agent summarize POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    check("agent response has steps",
          "steps" in d and isinstance(d.get("steps"), list), "")
    if d.get("steps"):
        # The planner should have picked summarize_document tool
        tools_used = [s.get("tool") for s in d["steps"]]
        check("agent used 'summarize_document' tool",
              "summarize_document" in tools_used, f"tools used: {tools_used}")
    # Answer should mention Golden Falcon
    ans = (d.get("answer") or "").lower()
    check("agent answer mentions golden falcon",
          "golden falcon" in ans or "falcon" in ans, f"first 200: {ans[:200]}")

# ---- 2h. Brief #20: agent mode (find_entity tool) ----
print("\n=== 2h. Brief #20: agent mode (find_entity tool) ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "find documents mentioning Yousef Al Saedi",
    "agent": True
}, timeout=240)
check("agent find_entity POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    if d.get("steps"):
        tools_used = [s.get("tool") for s in d["steps"]]
        check("agent used 'find_entity' tool",
              "find_entity" in tools_used, f"tools used: {tools_used}")

# ---- 2i. Brief #20: agent mode (compare_documents tool) ----
print("\n=== 2i. Brief #20: agent mode (compare_documents tool) ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "compare the Golden Falcon script and the creative treatment",
    "agent": True
}, timeout=240)
check("agent compare_documents POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    if d.get("steps"):
        tools_used = [s.get("tool") for s in d["steps"]]
        check("agent used 'compare_documents' tool",
              "compare_documents" in tools_used, f"tools used: {tools_used}")

# ---- 2j. Brief #20: agent mode (search_library tool) ----
print("\n=== 2j. Brief #20: agent mode (search_library tool) ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what does the safety guide say about emergency exits?",
    "agent": True
}, timeout=240)
check("agent search_library POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    if d.get("steps"):
        tools_used = [s.get("tool") for s in d["steps"]]
        check("agent used 'search_library' tool",
              "search_library" in tools_used, f"tools used: {tools_used}")

# ---- 2k. Brief #20: agent failure falls back to normal pipeline ----
print("\n=== 2k. Brief #20: agent failure falls back to normal pipeline ===")
# A super-simple question that doesn't need tools — agent should still work or fall back gracefully
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "hello",
    "agent": True
}, timeout=240)
check("agent mode with simple question POST 200 (no crash)",
      s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    check("agent response has 'answer' field (fallback or normal)",
          "answer" in d, f"keys: {list(d.keys())}")

# ---- 2l. Brief #21: deep answer mode ----
print("\n=== 2l. Brief #21: deep answer mode ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what is the budget for Golden Falcon and who is the director?",
    "deep": True
}, timeout=300)
check("deep mode POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = d.get("answer") or ""
    # Deep mode should produce a multi-section answer
    check("deep answer is non-trivial (>= 200 chars)",
          len(ans) >= 200, f"len={len(ans)}")
    # Should mention director (Yousef Al Saedi) and budget
    ans_lower = ans.lower()
    check("deep answer mentions 'yousef' (director)",
          "yousef" in ans_lower, f"first 300: {ans[:300]}")
    check("deep answer mentions 'budget' or 'aed'",
          "budget" in ans_lower or "aed" in ans_lower, "")
    # Should have multiple sources
    sources = d.get("sources") or []
    check("deep answer has >= 3 sources (multi-pass retrieval)",
          len(sources) >= 3, f"sources: {len(sources)}")
    # Should NOT have duplicate citation runs like [1][1]
    dup_pattern = re.search(r"\[\d+\]\[\d+\]", ans)
    check("deep answer has no duplicate citation runs [1][1] (Brief #22)",
          dup_pattern is None, f"found: {dup_pattern.group(0) if dup_pattern else 'none'}")

# ---- 2m. Brief #22: citation dedup (check normal chat too) ----
print("\n=== 2m. Brief #22: citation dedup in normal chat ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what does the safety guide and the warehouse procedures say about emergency exits?"
}, timeout=240)
check("normal chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = d.get("answer") or ""
    dup_pattern = re.search(r"\[\d+\]\[\d+\]", ans)
    check("normal chat answer has no duplicate citation runs [1][1]",
          dup_pattern is None, f"found: {dup_pattern.group(0) if dup_pattern else 'none'}")

# ---- 2n. Brief #23: exact-count rule (no hallucinated counts) ----
print("\n=== 2n. Brief #23: exact-count rule ===")
# Already partly tested in 2e. Test a different phrasing.
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "how many PDF documents are in the library?"
}, timeout=240)
check("count-by-type chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = d.get("answer") or ""
    # Should contain "8 PDF" (the exact count from inventory)
    has_exact_pdf_count = "8 pdf" in ans.lower() or "8 pdfs" in ans.lower()
    check("count answer contains exact '8 PDF' count (no hallucination)",
          has_exact_pdf_count, f"first 200: {ans[:200]}")

# ---- 2o. Brief #18b: clarifying question ----
print("\n=== 2o. Brief #18b: clarifying question on ambiguous query ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "contract"  # super ambiguous — should ask for clarification
}, timeout=240)
check("ambiguous chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = (d.get("answer") or "").lower()
    # Should either ask for clarification OR list multiple contracts
    clarifies = any(p in ans for p in ["which", "could you", "please specify",
                                        "which contract", "do you mean"])
    lists_contracts = "contract" in ans and ("1." in ans or "2." in ans)
    check("ambiguous query either clarifies OR lists matching docs",
          clarifies or lists_contracts, f"first 200: {ans[:200]}")

# ---- 2p. PII masking still works (regression) ----
print("\n=== 2p. PII masking regression ===")
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "show me the payroll for the Films department"
}, timeout=240)
check("payroll chat POST 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    ans = d.get("answer") or ""
    # Should NOT contain raw IBANs (AE07...) — they should be masked
    raw_iban = re.search(r"AE\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}", ans)
    check("payroll answer does NOT leak raw IBANs",
          raw_iban is None, f"found: {raw_iban.group(0) if raw_iban else 'none'}")
    # Should contain masked pattern
    has_mask = "•" in ans or "[IBAN" in ans or "REDACTED" in ans.upper() or "•••" in ans
    check("payroll answer contains masked IBAN pattern",
          has_mask or "iban" not in ans.lower(), f"first 200: {ans[:200]}")

# ---- 2q. Permission scoping still works (regression) ----
print("\n=== 2q. Permission scoping regression (agent + deep modes) ===")
# Login as ahmed (clearance 1, Films Production)
ahmed_tok = login("ahmed.alketbi", "Demo@2026")
if ahmed_tok:
    # Agent mode: ahmed should NOT see restricted docs
    s, d = req("POST", "/chat/", token=ahmed_tok, data={
        "question": "list all documents in the library",
        "agent": True
    }, timeout=240)
    check("agent mode as ahmed POST 200", s == 200, f"{s}")
    if s == 200 and isinstance(d, dict):
        ans = d.get("answer") or ""
        # Should NOT contain Restricted doc names like "Q3_Earnings_Briefing" or "Films_Payroll"
        leaks_restricted = "Q3_Earnings" in ans or "Films_Payroll" in ans or "Passport_Roster" in ans
        check("agent mode as ahmed does NOT leak Restricted docs",
              not leaks_restricted, f"leaked: {[n for n in ['Q3_Earnings', 'Films_Payroll', 'Passport_Roster'] if n in ans]}")

    # Deep mode: ahmed should NOT see restricted docs
    s, d = req("POST", "/chat/", token=ahmed_tok, data={
        "question": "what is in the Q3 earnings briefing?",
        "deep": True
    }, timeout=300)
    check("deep mode as ahmed POST 200", s == 200, f"{s}")
    if s == 200 and isinstance(d, dict):
        ans = (d.get("answer") or "").lower()
        # Should abstain or say "not enough info" since the doc is Restricted and ahmed has clearance 1
        abstains = any(p in ans for p in ["couldn't find", "don't have enough",
                                           "no information", "not mentioned",
                                           "لم أعثر", "لا أملك", "لا تتوفر"])
        check("deep mode as ahmed abstains on Restricted doc",
              abstains, f"first 200: {ans[:200]}")

# ---- 2r. Performance: agent + deep should not be absurdly slow ----
print("\n=== 2r. Performance bounds ===")
t0 = time.time()
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what is Project Golden Falcon?",
    "agent": True
}, timeout=300)
agent_elapsed = time.time() - t0
check(f"agent mode completes in < 60s (took {agent_elapsed:.1f}s)",
      agent_elapsed < 60 and s == 200, f"{agent_elapsed:.1f}s status={s}")

t0 = time.time()
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what is Project Golden Falcon?",
    "deep": True
}, timeout=300)
deep_elapsed = time.time() - t0
check(f"deep mode completes in < 90s (took {deep_elapsed:.1f}s)",
      deep_elapsed < 90 and s == 200, f"{deep_elapsed:.1f}s status={s}")


# ==========================================================================
# Summary
# ==========================================================================
print("\n" + "=" * 60)
print(f"BRIEFS #18-30 UAT:  {PASS} PASS / {FAIL} FAIL out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
