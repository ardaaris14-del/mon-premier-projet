/* ---------- Clients ---------- */
const formuleClient = c => c.formule === "kit" ? '<span class="tag">Kit seul</span>'
  : c.suivi ? '<span class="tag new">Avec suivi</span>' : '<span class="tag">Suivi arrêté</span>';
async function chargerClients() {
  try {
    const mois = maintenant().slice(0, 7);
    const [clients, posts] = await Promise.all([
      sb.from("clients").select("*").order("cree_le").then(verifier),
      sb.from("publications").select("*").eq("mois", mois).then(verifier),
    ]);
    $("clients-liste").innerHTML = clients.length ? clients.map(c => `<div class="run"><div><b>${esc(c.nom)}</b> ${formuleClient(c)}
      <div class="muted">${esc(metiers()[c.metier] || c.metier)}${c.ville ? " · " + esc(c.ville) : ""}${c.telephone ? " · " + esc(c.telephone) : ""}</div></div>
      <div class="actions" style="margin:0">${c.formule === "kit" ? "" : `<button data-suivi="${esc(c.id)}" data-actif="${c.suivi}">${c.suivi ? "Arrêter le suivi" : "Reprendre le suivi"}</button>`}
      <button data-retirer="${esc(c.id)}">Retirer</button></div></div>`).join("") : '<p class="muted">Aucun client pour l\'instant.</p>';
    const noms = Object.fromEntries(clients.map(c => [c.id, c.nom]));
    $("clients-posts").innerHTML = posts.map(x => `<div class="bloc"><b>${esc(noms[x.client_id] || "")}</b>${
      x.posts.map((p, i) => `<div class="post"><b>Semaine ${i + 1} — ${esc(p.titre)}</b><p>${esc(p.texte)}</p>
      <p class="muted">Visuel : ${esc(p.visuel)}</p><button data-copie="${esc(p.texte)}">Copier</button></div>`).join("")}</div>`).join("")
      || '<p class="muted">Les publications apparaissent après le prochain passage de la machine.</p>';
  } catch (e) {
    $("clients-liste").innerHTML = `<p class="msg ko">${esc(e.message)}</p>`;
  }
}
$("client-ajout").addEventListener("submit", async e => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  const bouton = e.target.querySelector("button");
  bouton.disabled = true;
  try {
    await sb.from("clients").insert({ nom: f.nom.trim(), metier: f.metier, ville: f.ville.trim(), telephone: f.telephone.trim() || null,
      formule: f.formule, suivi: f.formule === "kit+suivi" }).then(verifier);
    e.target.reset();
    message("clients-msg", f.formule === "kit" ? "Client ajouté ✓" : "Client ajouté ✓ Ses publications apparaîtront après le prochain passage de la machine.", true);
    chargerClients();
  } catch (err) {
    message("clients-msg", err.message, false);
  }
  bouton.disabled = false;
});
$("clients-liste").addEventListener("click", async e => {
  const s = e.target.closest("[data-suivi]");
  if (s) {
    const actif = s.dataset.actif === "true";
    if (actif && !confirm("Arrêter le suivi de ce client ? La machine ne rédigera plus ses publications. S'il paie par Stripe, résilie aussi son abonnement dans Stripe (la résiliation Stripe arrête le suivi ici toute seule).")) return;
    try { await sb.from("clients").update({ suivi: !actif }).eq("id", s.dataset.suivi).then(verifier); chargerClients(); }
    catch (err) { message("clients-msg", err.message, false); }
    return;
  }
  const b = e.target.closest("[data-retirer]");
  if (!b || !confirm("Retirer ce client de ta liste ? Ses ventes restent dans l'onglet Ventes.")) return;
  try { await sb.from("clients").delete().eq("id", b.dataset.retirer).then(verifier); chargerClients(); }
  catch (err) { message("clients-msg", err.message, false); }
});
$("clients-posts").addEventListener("click", async e => {
  const b = e.target.closest("button[data-copie]");
  if (!b) return;
  try { await navigator.clipboard.writeText(b.dataset.copie); b.textContent = "Copié !"; } catch (err) {}
});

/* ---------- Réglages ---------- */
function remplirReglages() {
  const d = R.data || {};
  for (const champ of $("reglages").querySelectorAll("[name]")) {
    const [a, b] = champ.name.split(".");
    const v = b ? (d[a] || {})[b] : d[a];
    champ.value = Array.isArray(v) ? v.join("\n") : (v ?? "");
  }
  const cantons = new Set((d.zone || {}).cantons || []);
  $("cases-cantons").innerHTML = Object.entries(CANTONS).map(([k, n]) =>
    `<label><input type="checkbox" value="${k}" ${cantons.has(k) ? "checked" : ""}> ${n}</label>`).join("");
  const choix = (d.zone || {}).metiers;
  $("tous-metiers").checked = choix === "tous";
  const actifs = new Set(Array.isArray(choix) ? choix : []);
  $("cases-metiers").innerHTML = Object.entries(metiers()).map(([k, n]) =>
    `<label><input type="checkbox" value="${k}" ${actifs.has(k) ? "checked" : ""}> ${esc(n)}</label>`).join("");
  $("cases-metiers").hidden = $("tous-metiers").checked;
}
$("tous-metiers").addEventListener("change", e => { $("cases-metiers").hidden = e.target.checked; });
$("reglages").addEventListener("submit", async e => {
  e.preventDefault();
  const bouton = e.target.querySelector("button[type=submit]");
  bouton.disabled = true;
  try {
    const d = JSON.parse(JSON.stringify(R.data || {}));
    for (const champ of e.target.querySelectorAll("[name]")) {
      const [a, b] = champ.name.split(".");
      let v = champ.value.trim();
      if (champ.type === "number") v = Number(v);
      if (a === "exclus") v = v.split(/\s+/).map(x => x.replace(/^CHE-?/i, "").replace(/\D/g, "")).filter(Boolean);
      if (b) d[a] = { ...(d[a] || {}), [b]: v }; else d[a] = v;
    }
    const cantons = [...$("cases-cantons").querySelectorAll("input:checked")].map(i => i.value);
    const choix = $("tous-metiers").checked ? "tous" : [...$("cases-metiers").querySelectorAll("input:checked")].map(i => i.value);
    if (!cantons.length) throw new Error("Choisis au moins un canton.");
    if (Array.isArray(choix) && !choix.length) throw new Error("Choisis au moins un métier, ou « Tous les métiers ».");
    d.zone = { ...(d.zone || {}), cantons, metiers: choix };
    await sb.from("reglages").update({ data: d, maj: maintenant() }).eq("id", 1).then(verifier);
    await sb.from("demandes").insert({ cree_le: maintenant() }).then(verifier);
    R.data = d;
    dessiner(false);
    message("reglages-msg", "Enregistré ✓ La machine repasse dans les 15 minutes pour appliquer tes réglages (kits, prix, messages).", true);
  } catch (err) {
    message("reglages-msg", err.message, false);
  }
  bouton.disabled = false;
});
$("compte").addEventListener("submit", async e => {
  e.preventDefault();
  const { error } = await sb.auth.updateUser({ password: e.target.mdp.value });
  if (error) message("compte-msg", error.message, false);
  else { e.target.reset(); message("compte-msg", "Mot de passe changé ✓", true); }
});

/* ---------- Machine ---------- */
let minuteur;
async function chargerMachine() {
  clearTimeout(minuteur);
  try {
    const [passages, demandes] = await Promise.all([
      sb.from("passages").select("*").order("debut", { ascending: false }).limit(8).then(verifier),
      sb.from("demandes").select("id").is("traitee_le", null).then(verifier),
    ]);
    const attente = demandes.length ? '<div class="run"><div><b>Lancement demandé</b><div class="muted">Démarre dans les 15 minutes</div></div><span class="pastille encours">En attente</span></div>' : "";
    $("runs").innerHTML = attente + (passages.map(x => {
      const [texte, classe] = { "réussi": ["Réussi", "ok"], "échec": ["Échec", "ko"] }[x.statut] || ["En cours…", "encours"];
      const d = x.details || {};
      const detail = x.statut === "réussi" ? `${d.kits ?? 0} kits · ${d.nouveaux ?? 0} nouvelles entreprises` : x.statut === "échec" ? esc(d.erreur || "") : "Recherche en cours";
      return `<div class="run"><div><b>${new Date(x.debut).toLocaleString("fr-CH", { dateStyle: "short", timeStyle: "short" })}</b>
        <div class="muted">${detail}</div></div><span class="pastille ${classe}">${texte}</span></div>`;
    }).join("") || '<p class="muted">Aucun passage enregistré pour l\'instant.</p>');
    if ((demandes.length || passages.some(x => x.statut === "en cours")) && !document.querySelector('[data-onglet="machine"]').hidden)
      minuteur = setTimeout(chargerMachine, 30000);
  } catch (e) {
    $("runs").innerHTML = `<p class="msg ko">${esc(e.message)}</p>`;
  }
}
$("lancer").addEventListener("click", async e => {
  e.target.disabled = true;
  try {
    await sb.from("demandes").insert({ cree_le: maintenant() }).then(verifier);
    message("machine-msg", "C'est noté ✓ La machine démarre dans les 15 minutes.", true);
    chargerMachine();
  } catch (err) {
    message("machine-msg", err.message, false);
  }
  e.target.disabled = false;
});
