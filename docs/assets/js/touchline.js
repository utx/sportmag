/* Touchline — Send-to-Kindle button and small page niceties. */
(function () {
  "use strict";

  var cfg = window.TOUCHLINE_CONFIG || {};
  var body = document.body;
  var issue = body.getAttribute("data-issue");
  var epubHref = body.getAttribute("data-epub");
  var toastEl = document.querySelector(".toast");
  var toastTimer;

  function toast(html, ms) {
    if (!toastEl) return;
    toastEl.innerHTML = html;
    toastEl.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-on"); }, ms || 6000);
  }

  function setAll(state, label) {
    document.querySelectorAll("[data-kindle]").forEach(function (b) {
      if (!b.dataset.label) b.dataset.label = b.querySelector("span").innerHTML;
      b.dataset.state = state || "";
      b.disabled = state === "sending";
      b.querySelector("span").innerHTML = label || b.dataset.label;
    });
  }

  var downloadLink = '<a href="' + epubHref + '" download>download the Kindle file</a>';

  function send() {
    if (!cfg.kindleEndpoint) {
      toast("One-tap sending isn't switched on yet, so you'll need to " + downloadLink + " instead.", 9000);
      return;
    }
    setAll("sending", "Sending…");
    var url = cfg.kindleEndpoint + (cfg.kindleEndpoint.indexOf("?") > -1 ? "&" : "?") + "issue=" + encodeURIComponent(issue);
    fetch(url, { method: "GET", redirect: "follow" })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res && res.ok) {
          setAll("sent", "Sent ✓");
          toast("Sent! Issue " + Number(issue) + " should land on the Kindle in a few minutes. Make sure its Wi-Fi is on.", 8000);
        } else if (res && res.error === "too-soon") {
          setAll("", null);
          toast("Already sent a moment ago, so check the Kindle in a few minutes.", 7000);
        } else {
          throw new Error((res && res.error) || "unknown");
        }
      })
      .catch(function () {
        setAll("", null);
        toast("Hmm, the Kindle didn't answer. Try again in a minute, or " + downloadLink + ".", 10000);
      });
  }

  document.querySelectorAll("[data-kindle]").forEach(function (b) {
    b.addEventListener("click", send);
  });

  // Word Watch: tapping a highlighted word shows its meaning.
  var defs = {};
  document.querySelectorAll(".box--word dt").forEach(function (dt) {
    var dd = dt.nextElementSibling;
    var word = dt.childNodes[0].textContent.trim().toLowerCase();
    if (dd) defs[word] = dd.textContent.trim();
  });
  document.querySelectorAll(".ww").forEach(function (w) {
    var key = (w.getAttribute("data-word") || w.textContent).trim().toLowerCase();
    if (defs[key]) {
      w.setAttribute("title", defs[key]);
      w.addEventListener("click", function () { toast("<b>" + w.textContent + "</b>: " + defs[key], 7000); });
    }
  });
})();
