(function () {
  var script = document.currentScript;
  var app = script && script.getAttribute("data-app");
  if (!app) return;
  var endpoint = new URL(script.src).origin + "/api/public/chat";
  var MAX = 2000;

  function sessionId() {
    try {
      var k = "hermes-chat-session", v = sessionStorage.getItem(k);
      if (!v) {
        var a = new Uint8Array(12);
        crypto.getRandomValues(a);
        v = Array.prototype.map.call(a, function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
        sessionStorage.setItem(k, v);
      }
      return v;
    } catch (e) { return ""; }
  }

  var host = document.createElement("div");
  host.style.cssText = "all:initial;position:fixed;right:16px;bottom:16px;z-index:2147483000;";
  var root = host.attachShadow({ mode: "open" });
  var style = document.createElement("style");
  style.textContent =
    ":host{font:14px system-ui,sans-serif}" +
    ".fab{width:56px;height:56px;border-radius:50%;border:0;background:#2259bc;color:#fff;font-size:24px;cursor:pointer;box-shadow:0 4px 16px #0004}" +
    ".panel{position:absolute;right:0;bottom:68px;width:min(360px,calc(100vw - 32px));height:min(480px,70vh);background:#fff;color:#172033;border-radius:14px;box-shadow:0 8px 32px #0004;display:none;flex-direction:column;overflow:hidden}" +
    ".panel.open{display:flex}" +
    "header{background:#14213d;color:#fff;padding:12px 14px;font-weight:700}" +
    ".msgs{flex:1;overflow:auto;padding:12px;background:#f4f6fa}" +
    ".m{padding:8px 10px;margin:6px 0;border-radius:10px;white-space:pre-wrap;line-height:1.45}" +
    ".u{background:#e7f0ff;margin-left:18%}.a{background:#fff;margin-right:10%}" +
    "form{display:flex;gap:6px;padding:10px;border-top:1px solid #ddd}" +
    "input{flex:1;padding:9px;border:1px solid #ccc;border-radius:8px;font:inherit}" +
    "button.send{background:#2259bc;color:#fff;border:0;border-radius:8px;padding:0 14px;cursor:pointer}" +
    "button:disabled{opacity:.5}small{padding:0 12px 8px;color:#667}";
  root.appendChild(style);

  var fab = document.createElement("button");
  fab.className = "fab";
  fab.setAttribute("aria-label", "Mở trợ lý hướng dẫn");
  fab.textContent = "?";
  var panel = document.createElement("section");
  panel.className = "panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Trợ lý hướng dẫn sử dụng");
  var head = document.createElement("header");
  head.textContent = "Trợ lý hướng dẫn";
  var msgs = document.createElement("div");
  msgs.className = "msgs";
  msgs.setAttribute("aria-live", "polite");
  var form = document.createElement("form");
  var input = document.createElement("input");
  input.maxLength = MAX;
  input.placeholder = "Nhập câu hỏi...";
  input.setAttribute("aria-label", "Câu hỏi");
  input.autocomplete = "off";
  var send = document.createElement("button");
  send.className = "send";
  send.textContent = "Gửi";
  var note = document.createElement("small");
  note.textContent = "Không nhập mật khẩu, mã OTP hoặc dữ liệu bệnh nhân.";
  form.appendChild(input);
  form.appendChild(send);
  panel.appendChild(head);
  panel.appendChild(msgs);
  panel.appendChild(form);
  panel.appendChild(note);
  root.appendChild(panel);
  root.appendChild(fab);

  function add(kind, text) {
    var d = document.createElement("div");
    d.className = "m " + kind;
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
  }
  add("a", "Xin chào! Tôi hướng dẫn đăng nhập và đăng ký tài khoản.");

  function toggle(open) {
    panel.classList.toggle("open", open);
    if (open) input.focus(); else fab.focus();
  }
  fab.addEventListener("click", function () { toggle(!panel.classList.contains("open")); });
  panel.addEventListener("keydown", function (e) { if (e.key === "Escape") toggle(false); });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) return;
    input.value = "";
    add("u", q);
    send.disabled = true;
    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ app: app, message: q, session: sessionId() })
    }).then(function (r) {
      return r.json().then(function (b) { return { ok: r.ok, status: r.status, body: b }; });
    }).then(function (res) {
      if (res.ok) add("a", res.body.answer);
      else add("a", res.body.error || "Có lỗi xảy ra. Vui lòng thử lại.");
    }).catch(function () {
      add("a", "Không nhận được phản hồi hợp lệ từ máy chủ. Vui lòng thử lại sau.");
    }).then(function () { send.disabled = false; input.focus(); });
  });

  document.body.appendChild(host);
})();
