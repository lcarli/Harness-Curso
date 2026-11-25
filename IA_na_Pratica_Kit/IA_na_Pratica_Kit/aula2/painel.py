"""Painel da Aurora - a visual inspector for the API lesson (Aula 2).

Opens a local web page with a chat on the left and, on the right, tabs that show
what really travels to the model on every question:
  - Pedido:   the request (URL, headers with the key hidden, JSON body)
  - Resposta: the raw JSON that comes back
  - Memória:  the history the PROGRAM keeps and resends (the model keeps nothing)
  - Tokens:   input/output tokens per call, so the class sees the cost grow

Run from the kit root:
    python aula2/painel.py            # real calls, using BASE_URL / API_KEY / MODEL from .env
    python aula2/painel.py --simular  # no API key needed: simulated answers, same screens

Only the Python standard library is required (python-dotenv is used when installed).
The server listens on 127.0.0.1 only, and the API key is never sent to the page.
"""
import json
import os
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent


# ---------- 1) Configuration: the same 3 lines of .env used by every script ----------
def load_env():
    """Load .env the same way the other scripts do (python-dotenv), with a tiny fallback."""
    try:
        from dotenv import load_dotenv
        load_dotenv()  # searches from this script's folder upwards (aula2/.env, then the kit root)
        return
    except ImportError:
        pass
    for candidate in (HERE / ".env", HERE.parent / ".env", Path.cwd() / ".env"):
        if candidate.exists():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            return


load_env()
BASE_URL = os.getenv("BASE_URL", "").strip()
API_KEY = os.getenv("API_KEY", "").strip()
MODEL = os.getenv("MODEL", "").strip()
LOCAL = any(h in BASE_URL for h in ("localhost", "127.0.0.1"))
PLACEHOLDER_KEY = API_KEY.lower().startswith("cole_aqui")
SIMULATED = ("--simular" in sys.argv or not BASE_URL or not MODEL
             or ((not API_KEY or PLACEHOLDER_KEY) and not LOCAL))
ENDPOINT = (BASE_URL.rstrip("/") + "/chat/completions") if BASE_URL else "(simulado)/chat/completions"
PORT = int(os.getenv("PAINEL_PORTA", "8765"))

DEFAULT_SYSTEM = ("Você é a Aurora, assistente do Café Aurora. Responda em português, em até 3 frases. "
                  "Fatos: seg a sáb 7h às 19h; dom 8h às 13h; pão de queijo sai às 7h e às 16h; "
                  "pagamento: Pix, débito e crédito. Nunca prometa descontos.")

# Shared state for one instructor session (the page is single-user by design).
LOCK = threading.Lock()
STATE = {"system": DEFAULT_SYSTEM, "history": [], "calls": []}


# ---------- 2) Talking to the provider (or simulating it) ----------
FRIENDLY_ERRORS = {
    0: "Não consegui falar com o provedor: confira a internet e o BASE_URL.",
    400: "O provedor recusou o pedido. Veja os detalhes na aba Resposta.",
    401: "A chave não foi aceita: confira o API_KEY no .env.",
    403: "Sem permissão para este modelo ou recurso.",
    404: "Endereço ou modelo não encontrado: confira BASE_URL e MODEL.",
    429: "Limite de uso atingido: espere um pouco e tente de novo.",
}


def call_provider(payload):
    """POST the JSON body to <BASE_URL>/chat/completions, exactly like the .http file does."""
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(raw)
        except ValueError:
            return error.code, {"erro": raw[:2000]}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, {"erro": str(getattr(error, "reason", error))}


def plain(text):
    """Lowercase and remove accents, to make the simulated answers easy to match."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


NAME_STATEMENT = re.compile(r"(?:meu nome (?:e|eh)|me chamo)\s+([a-z]+)")
NAME_QUESTION = ("qual e meu nome", "qual e o meu nome", "qual o meu nome", "qual meu nome",
                 "como eu me chamo", "como me chamo", "sabe meu nome", "lembra meu nome", "lembra do meu nome")
SWEET_NAMES = ["Trufa Nascer do Sol", "Bombom Manhã Dourada", "Brigadeiro Aurora Boreal",
               "Pudim Primeiro Raio", "Torta Alvorada", "Bem-casado Céu de Outubro"]


def estimate_tokens(text):
    return max(1, len(text) // 4)


def simulate(payload):
    """Rule-based answers that behave like the real thing for the classroom demos."""
    messages = payload["messages"]
    question = plain(messages[-1]["content"])
    if any(q in question for q in NAME_QUESTION):
        # The "model" only knows what was SENT in this request: that is the whole point.
        name = None
        for m in messages[:-1]:
            if m["role"] == "user":
                found = NAME_STATEMENT.search(plain(m["content"]))
                if found:
                    name = found.group(1).capitalize()
        answer = f"Você é {name}! Como posso ajudar?" if name else "Ainda não sei o seu nome. Pode me contar?"
    elif NAME_STATEMENT.search(question):
        answer = f"Prazer, {NAME_STATEMENT.search(question).group(1).capitalize()}! Como posso ajudar?"
    elif "doce" in question and ("nome" in question or "batiz" in question):
        temperature = float(payload.get("temperature", 0.3))
        answer = "Doce Aurora" if temperature <= 0.3 else random.choice(SWEET_NAMES)
    elif "pao de queijo" in question:
        answer = "O pão de queijo sai quentinho às 7h e às 16h!"
    elif any(w in question for w in ("horario", "abre", "abrem", "fecha", "domingo", "sabado")):
        answer = "Abrimos de segunda a sábado, das 7h às 19h, e aos domingos, das 8h às 13h."
    elif any(w in question for w in ("pagamento", "pix", "cartao", "credito", "debito")):
        answer = "Aceitamos Pix, débito e crédito."
    elif "desconto" in question:
        answer = "Desculpe, não posso oferecer descontos. Posso ajudar com outra coisa?"
    else:
        answer = ("(modo simulado) Sou a Aurora. Pergunte sobre horários, pão de queijo, pagamento "
                  "ou peça um nome para um doce novo. Com uma chave de API, eu respondo de verdade.")
    prompt_tokens = sum(estimate_tokens(m["content"]) + 4 for m in messages)
    completion_tokens = estimate_tokens(answer)
    return {
        "id": f"simulado-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": payload["model"],
        "choices": [{"index": 0, "message": {"role": "assistant", "content": answer}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                  "total_tokens": prompt_tokens + completion_tokens},
    }


def friendly_error(status, body):
    text = json.dumps(body, ensure_ascii=False) if not isinstance(body, str) else body
    if status == 400 and "temperature" in text.lower():
        return "Este modelo não aceita ajustar a temperatura. Volte o controle para 1 ou troque o MODEL."
    if status >= 500:
        return "O provedor está com problemas agora. Tente de novo em instantes."
    return FRIENDLY_ERRORS.get(status, f"O provedor respondeu com erro ({status}). Veja a aba Resposta.")


# ---------- 3) One question = one call (this is the heart of the lesson) ----------
def ask(text, temperature, memory_on, system):
    with LOCK:
        STATE["system"] = system or DEFAULT_SYSTEM
        messages = [{"role": "system", "content": STATE["system"]}]
        if memory_on:
            messages += STATE["history"]  # the program resends the whole conversation
        messages.append({"role": "user", "content": text})
        payload = {"model": MODEL or "modelo-simulado", "temperature": temperature, "messages": messages}

    started = time.time()
    status, body = (200, simulate(payload)) if SIMULATED else call_provider(payload)
    elapsed_ms = int((time.time() - started) * 1000)

    ok = status == 200 and isinstance(body, dict) and bool(body.get("choices"))
    answer = body["choices"][0]["message"].get("content") if ok else None
    usage = (body.get("usage") or {}) if isinstance(body, dict) else {}
    details = usage.get("prompt_tokens_details") or {}
    estimated = SIMULATED or not usage
    call = {
        "n": len(STATE["calls"]) + 1,
        "mensagens": len(messages),
        "entrada": usage.get("prompt_tokens") or sum(estimate_tokens(m["content"]) + 4 for m in messages),
        "saida": usage.get("completion_tokens") or (estimate_tokens(answer) if answer else 0),
        "cache": details.get("cached_tokens"),
        "estimado": estimated,
        "ms": elapsed_ms,
        "ok": ok,
    }
    with LOCK:
        if ok and memory_on:
            STATE["history"] += [{"role": "user", "content": text}, {"role": "assistant", "content": answer or ""}]
        STATE["calls"].append(call)
        memory = [{"role": "system", "content": STATE["system"]}] + STATE["history"]
        calls = list(STATE["calls"])

    return {
        "ok": ok,
        "resposta": answer,
        "erro": None if ok else friendly_error(status, body),
        "status": status,
        "pedido": {
            "metodo": "POST",
            "url": ENDPOINT,
            "cabecalhos": {"Authorization": "Bearer ************ (chave escondida)", "Content-Type": "application/json"},
            "corpo": payload,
        },
        "resposta_bruta": body,
        "memoria": memory,
        "memoria_ligada": memory_on,
        "chamadas": calls,
    }


def snapshot():
    with LOCK:
        return {
            "modo": "simulado" if SIMULATED else "real",
            "provedor": urlparse(BASE_URL).netloc if BASE_URL else "(nenhum)",
            "modelo": MODEL or "modelo-simulado",
            "url": ENDPOINT,
            "sistema": STATE["system"],
            "memoria": [{"role": "system", "content": STATE["system"]}] + STATE["history"],
            "chamadas": list(STATE["calls"]),
        }


# ---------- 4) A tiny local web server ----------
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data, content_type="application/json; charset=utf-8"):
        raw = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except ValueError:
            return {}

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/api/estado":
            self._send(200, snapshot())
        else:
            self._send(404, {"erro": "não encontrado"})

    def do_POST(self):
        data = self._json_body()
        if self.path == "/api/enviar":
            text = str(data.get("texto", "")).strip()
            if not text:
                self._send(400, {"erro": "Digite uma pergunta."})
                return
            try:
                temperature = max(0.0, min(2.0, float(data.get("temperatura", 0.3))))
            except (TypeError, ValueError):
                temperature = 0.3
            self._send(200, ask(text, temperature, bool(data.get("memoria", True)), str(data.get("sistema") or "")))
        elif self.path == "/api/nova":
            with LOCK:
                STATE["history"], STATE["calls"] = [], []
            self._send(200, snapshot())
        else:
            self._send(404, {"erro": "não encontrado"})

    def log_message(self, *args):  # keep the terminal clean for the class
        pass


PAGE = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel da Aurora</title>
<style>
  :root { --navy:#0B1B33; --bg:#F4F6FA; --ink:#14202E; --muted:#4A5568; --blue:#0F6CBD; --tint:#DCE9F7;
          --amber:#FFB900; --line:#D5DCE6; --code:#1E1E1E; --codetx:#D4D4D4; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Segoe UI", system-ui, sans-serif; background:var(--bg); color:var(--ink); }
  header { background:var(--navy); color:#fff; padding:14px 24px; display:flex; align-items:center; gap:18px; flex-wrap:wrap; }
  header h1 { font-size:20px; margin:0; }
  header .sub { color:#AFC3DD; font-size:14px; }
  .badge { padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:1px; }
  .badge.real { background:#107C10; color:#fff; } .badge.simulado { background:var(--amber); color:var(--ink); }
  main { display:grid; grid-template-columns: minmax(340px, 5fr) 7fr; gap:18px; padding:18px 24px; height:calc(100vh - 64px); }
  section { background:#fff; border-radius:10px; box-shadow:0 2px 8px rgba(20,32,46,.10); display:flex; flex-direction:column; min-height:0; }
  .controls { padding:14px 16px; border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:14px; align-items:center; font-size:14px; }
  .controls label { display:flex; align-items:center; gap:6px; }
  .controls input[type=range] { width:120px; }
  .temp { font-weight:700; min-width:28px; }
  button { font:inherit; border:0; border-radius:6px; padding:8px 14px; cursor:pointer; background:var(--tint); color:var(--navy); font-weight:600; }
  button.primary { background:var(--blue); color:#fff; }
  details { width:100%; } summary { cursor:pointer; color:var(--muted); }
  textarea { width:100%; min-height:70px; margin-top:8px; font:13px Consolas, monospace; border:1px solid var(--line); border-radius:6px; padding:8px; }
  .chips { padding:10px 16px 0; display:flex; flex-wrap:wrap; gap:8px; }
  .chips button { padding:5px 10px; font-size:13px; background:#EEF1F5; color:var(--ink); font-weight:500; }
  #msgs { flex:1; overflow:auto; padding:16px; display:flex; flex-direction:column; gap:10px; }
  .bubble { max-width:85%; padding:10px 14px; border-radius:12px; line-height:1.4; font-size:15px; white-space:pre-wrap; }
  .user { align-self:flex-end; background:var(--blue); color:#fff; border-bottom-right-radius:3px; }
  .assistant { align-self:flex-start; background:#EEF1F5; border-bottom-left-radius:3px; }
  .error { align-self:stretch; background:#FBE3E7; color:#8A1C2F; }
  .note { align-self:center; color:var(--muted); font-size:12px; }
  form { display:flex; gap:8px; padding:12px 16px; border-top:1px solid var(--line); }
  form input { flex:1; font:inherit; padding:10px; border:1px solid var(--line); border-radius:6px; }
  nav { display:flex; gap:4px; padding:10px 12px 0; border-bottom:1px solid var(--line); }
  nav button { background:transparent; border-radius:6px 6px 0 0; color:var(--muted); }
  nav button.on { background:var(--navy); color:#fff; }
  .caption { padding:10px 16px; font-size:14px; color:var(--muted); background:#F8FAFC; border-bottom:1px solid var(--line); }
  .pane { flex:1; overflow:auto; padding:14px 16px; }
  pre { background:var(--code); color:var(--codetx); padding:14px; border-radius:8px; font:13px/1.45 Consolas, monospace; white-space:pre-wrap; word-break:break-word; margin:0 0 12px; }
  .key { color:#9CDCFE; } .str { color:#FFD580; } .num { color:#B5CEA8; } .lit { color:#C586C0; }
  .hint { color:var(--muted); font-size:14px; }
  .role { display:inline-block; min-width:86px; text-align:center; padding:3px 8px; border-radius:999px; font-size:12px; font-weight:700; margin-right:10px; }
  .r-system { background:var(--navy); color:#fff; } .r-user { background:var(--amber); color:var(--ink); } .r-assistant { background:var(--blue); color:#fff; }
  .mem { display:flex; align-items:flex-start; padding:9px 0; border-bottom:1px solid var(--line); font-size:14px; }
  .banner { background:#FFF4CE; padding:10px 12px; border-radius:6px; margin-bottom:12px; font-size:14px; }
  table { border-collapse:collapse; width:100%; font-size:14px; margin-bottom:14px; }
  th, td { text-align:left; padding:7px 8px; border-bottom:1px solid var(--line); }
  .bar { height:14px; background:var(--blue); border-radius:3px; }
  .bar.out { background:var(--amber); }
  .prices { display:flex; gap:12px; flex-wrap:wrap; align-items:center; font-size:14px; }
  .prices input { width:90px; padding:6px; border:1px solid var(--line); border-radius:6px; }
</style>
</head>
<body>
<header>
  <h1>Painel da Aurora</h1>
  <span id="modo" class="badge"></span>
  <span class="sub" id="info"></span>
</header>
<main>
  <section>
    <div class="controls">
      <label><input type="checkbox" id="memoria" checked> Memória ligada</label>
      <label>Temperatura <input type="range" id="temp" min="0" max="1.5" step="0.1" value="0.3"> <span class="temp" id="tempv">0.3</span></label>
      <button id="nova">Nova conversa</button>
      <details><summary>Instruções (mensagem system)</summary><textarea id="sistema"></textarea></details>
    </div>
    <div class="chips" id="chips"></div>
    <div id="msgs"></div>
    <form id="f"><input id="txt" autocomplete="off" placeholder="Pergunte algo à Aurora..."><button class="primary">Enviar</button></form>
  </section>
  <section>
    <nav id="tabs"></nav>
    <div class="caption" id="cap"></div>
    <div class="pane" id="pane"></div>
  </section>
</main>
<script>
const TABS = {
  pedido:   ["Pedido enviado", "É isto que o programa envia ao provedor a cada pergunta: o endereço, os cabeçalhos (a chave fica escondida) e o corpo em JSON com o modelo, a temperatura e TODAS as mensagens."],
  resposta: ["Resposta recebida", "É o JSON que volta do provedor. O texto da Aurora está em choices[0].message.content; o consumo, em usage."],
  memoria:  ["Memória", "O modelo não guarda nada entre perguntas. Quem guarda a conversa é o programa, e ele reenvia tudo a cada nova pergunta."],
  tokens:   ["Tokens e custo", "Cada chamada envia mais tokens que a anterior, porque o histórico vai junto. Mais tokens = mais custo e mais demora."]
};
const EXAMPLES = ["Meu nome é Ana.", "Qual é meu nome?", "Que horas vocês abrem no domingo?", "Dê um nome para o novo doce da Aurora."];
let tab = "pedido", last = null, state = null;
const prices = {pin: "", pout: ""};
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
function pretty(obj) {
  const text = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
  return esc(text).replace(/("(\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(\.\d+)?([eE][+-]?\d+)?)/g, (m) => {
    let cls = "num";
    if (m.startsWith('"')) cls = m.trimEnd().endsWith(":") ? "key" : "str";
    else if (/^(true|false|null)$/.test(m)) cls = "lit";
    return '<span class="' + cls + '">' + m + "</span>";
  });
}
async function api(path, body) {
  const r = await fetch(path, body ? {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)} : {});
  return r.json();
}
function bubble(cls, text) {
  const div = document.createElement("div");
  div.className = "bubble " + cls;
  div.textContent = text;
  $("#msgs").appendChild(div);
  $("#msgs").scrollTop = $("#msgs").scrollHeight;
}
function drawTabs() {
  $("#tabs").innerHTML = "";
  for (const [id, [name]] of Object.entries(TABS)) {
    const b = document.createElement("button");
    b.textContent = name;
    b.className = id === tab ? "on" : "";
    b.onclick = () => { tab = id; drawTabs(); drawPane(); };
    $("#tabs").appendChild(b);
  }
  $("#cap").textContent = TABS[tab][1];
}
function drawPane() {
  const pane = $("#pane");
  const memory = (last && last.memoria) || (state && state.memoria) || [];
  const calls = (last && last.chamadas) || (state && state.chamadas) || [];
  if (tab === "pedido") {
    if (!last) { pane.innerHTML = '<p class="hint">Envie uma pergunta para ver o pedido.</p>'; return; }
    const p = last.pedido;
    pane.innerHTML = "<pre>" + esc(p.metodo + " " + p.url) + "</pre><pre>" + pretty(p.cabecalhos) + "</pre><pre>" + pretty(p.corpo) + "</pre>" +
      '<p class="hint">Mensagens enviadas nesta chamada: <b>' + p.corpo.messages.length + "</b></p>";
  } else if (tab === "resposta") {
    if (!last) { pane.innerHTML = '<p class="hint">Envie uma pergunta para ver a resposta.</p>'; return; }
    pane.innerHTML = (last.erro ? '<div class="banner">' + esc(last.erro) + "</div>" : "") + "<pre>" + pretty(last.resposta_bruta) + "</pre>";
  } else if (tab === "memoria") {
    const on = $("#memoria").checked;
    let html = on ? "" : '<div class="banner">Memória desligada: o programa não está reenviando o histórico abaixo. Cada pergunta vai sozinha (só com a mensagem system).</div>';
    html += '<p class="hint">Na próxima pergunta, o programa vai enviar <b>' + (on ? memory.length + 1 : 2) + "</b> mensagens.</p>";
    for (const m of memory) html += '<div class="mem"><span class="role r-' + m.role + '">' + m.role + "</span><span>" + esc(m.content) + "</span></div>";
    pane.innerHTML = html;
  } else {
    if (!calls.length) { pane.innerHTML = '<p class="hint">Envie perguntas para ver os tokens crescendo.</p>'; return; }
    const max = Math.max(...calls.map((c) => c.entrada + c.saida));
    let html = "<table><tr><th>#</th><th>Mensagens</th><th>Entrada</th><th>Saída</th><th style='width:40%'></th></tr>";
    let tin = 0, tout = 0, cached = false, est = false;
    for (const c of calls) {
      tin += c.entrada; tout += c.saida; est = est || c.estimado;
      if (c.cache) cached = true;
      html += "<tr><td>" + c.n + "</td><td>" + c.mensagens + "</td><td>" + c.entrada + (c.cache ? " (" + c.cache + " em cache)" : "") + "</td><td>" + c.saida +
        '</td><td><div style="display:flex;gap:2px"><div class="bar" style="width:' + (100 * c.entrada / max) + '%"></div><div class="bar out" style="width:' + (100 * c.saida / max) + '%"></div></div></td></tr>';
    }
    html += "</table><p class='hint'>Total: <b>" + tin + "</b> tokens de entrada (azul) e <b>" + tout + "</b> de saída (amarelo)." +
      (est ? " Valores estimados (modo simulado ou provedor sem usage)." : "") +
      (cached ? " Alguns provedores reaproveitam o começo repetido do pedido (cache) e cobram menos por ele." : "") + "</p>";
    html += '<div class="prices">Preço por 1 milhão de tokens: entrada <input id="pin" type="number" step="0.01" placeholder="ex.: 0.40"> saída <input id="pout" type="number" step="0.01" placeholder="ex.: 1.60"> <span id="cost"></span></div>' +
      "<p class='hint'>Use o preço atual do seu provedor (veja a documentação).</p>";
    pane.innerHTML = html;
    const update = () => {
      const pin = parseFloat($("#pin").value) || 0, pout = parseFloat($("#pout").value) || 0;
      $("#cost").textContent = (pin || pout) ? "Custo estimado: " + ((tin / 1e6) * pin + (tout / 1e6) * pout).toFixed(6) : "";
    };
    $("#pin").value = prices.pin; $("#pout").value = prices.pout;
    $("#pin").oninput = () => { prices.pin = $("#pin").value; update(); };
    $("#pout").oninput = () => { prices.pout = $("#pout").value; update(); };
    update();
  }
}
async function send(text) {
  if (!text.trim()) return;
  bubble("user", text);
  $("#txt").value = "";
  const body = {texto: text, temperatura: parseFloat($("#temp").value), memoria: $("#memoria").checked, sistema: $("#sistema").value};
  const waiting = document.createElement("div"); waiting.className = "note"; waiting.textContent = "Aurora está pensando...";
  $("#msgs").appendChild(waiting);
  try {
    last = await api("/api/enviar", body);
  } catch (e) {
    last = null; waiting.remove(); bubble("error", "O painel parou de responder. Veja o terminal."); return;
  }
  waiting.remove();
  if (last.ok) bubble("assistant", last.resposta);
  else bubble("error", last.erro || "Erro.");
  drawPane();
}
async function init() {
  state = await api("/api/estado");
  $("#modo").textContent = state.modo === "real" ? "REAL" : "SIMULADO";
  $("#modo").className = "badge " + state.modo;
  $("#info").textContent = "Provedor: " + state.provedor + "  ·  Modelo: " + state.modelo;
  $("#sistema").value = state.sistema;
  for (const e of EXAMPLES) {
    const b = document.createElement("button"); b.type = "button"; b.textContent = e; b.onclick = () => send(e);
    $("#chips").appendChild(b);
  }
  if (state.modo !== "real") bubble("note", "Modo simulado: as respostas são de exemplo, mas o pedido, a memória e os tokens mostram o que aconteceria de verdade.");
  drawTabs(); drawPane();
}
$("#f").onsubmit = (e) => { e.preventDefault(); send($("#txt").value); };
$("#temp").oninput = () => { $("#tempv").textContent = $("#temp").value; };
$("#memoria").onchange = () => { bubble("note", $("#memoria").checked ? "Memória ligada: o histórico volta a ser reenviado." : "Memória desligada: cada pergunta vai sozinha."); drawPane(); };
$("#nova").onclick = async () => { state = await api("/api/nova", {}); last = null; $("#msgs").innerHTML = ""; bubble("note", "Nova conversa: a memória foi apagada."); drawPane(); };
init();
</script>
</body>
</html>
"""


def main():
    server, port = None, PORT
    for candidate in range(PORT, PORT + 10):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    if server is None:
        sys.exit("Não encontrei uma porta livre entre %d e %d." % (PORT, PORT + 9))
    url = f"http://127.0.0.1:{port}"
    print("Painel da Aurora")
    print(f"  Modo:     {'SIMULADO (sem chamar a API)' if SIMULATED else 'REAL'}")
    print(f"  Provedor: {urlparse(BASE_URL).netloc or '(nenhum)'}   Modelo: {MODEL or 'modelo-simulado'}")
    print(f"  Abra no navegador: {url}   (Ctrl+C para sair)")
    if "--sem-navegador" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAté a próxima!")


if __name__ == "__main__":
    main()
