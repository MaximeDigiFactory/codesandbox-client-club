(function () {
  if (location.pathname.indexOf("/__csb") === 0) {
    return;
  }

  var base =
    "Aperçu indisponible : votre navigateur bloque une fonction nécessaire à l'affichage. Téléchargez le fichier, ou ouvrez cette conversation dans Chrome, Edge ou Firefox.";
  var braveExtra =
    " Sous Brave, ce blocage vient des protections du navigateur.";

  function showUnavailable() {
    var main = document.getElementById("preview-unavailable");
    if (!main) {
      return;
    }
    var braveNote = document.getElementById("preview-unavailable-brave");
    if (braveNote && navigator.brave && typeof navigator.brave.isBrave === "function") {
      navigator.brave.isBrave().then(function (isBrave) {
        if (isBrave) {
          braveNote.textContent = braveExtra;
        }
      });
    }
    document.body.style.display = "flex";
    main.hidden = false;
  }

  if (!("serviceWorker" in navigator)) {
    showUnavailable();
    return;
  }

  if (navigator.serviceWorker.controller) {
    return;
  }

  var settled = false;
  function once() {
    if (settled) {
      return;
    }
    settled = true;
    if (!navigator.serviceWorker.controller) {
      showUnavailable();
    }
  }

  navigator.serviceWorker
    .register("/__csb_sw.rpfsli6sirrzs1630o3lgzuxwlr2uqc.js", { scope: "/" })
    .catch(once);

  setTimeout(once, 2000);
})();
