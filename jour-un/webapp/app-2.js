/* ---------- Prospects ---------- */
function numero(t) {
  const c = String(t || "").replace(/[^\d+]/g, "");
  if (/^0\d{9}$/.test(c)) return "+" + ((R.meta && R.meta.indicatif) || "41") + c.slice(1);
  return c.startsWith("00") ? "+" + c.slice(2) : c;
}
function remplir(modele, p) {
  const moi = (R.data && R.data.moi) || {};
  const v = { nom: p.nom, lien: p.kit_url || "", moi: moi.nom || "", tel: moi.telephone || "", ville: p.ville || "", metier: (metiers()[p.metier] || p.metier || "").toLowerCase() };
  return String(modele || "").replace(/\{(\w+)\}/g, (m, k) => k in v ? v[k] : m);
}
async function enregistrerSuivi(id, champs) {
  const ligne = { prospect_id: id, statut: statut(id), stop: false, ...(suivi[id] || {}), ...champs, maj: maintenant() };
  suivi[id] = ligne;
  dessiner(false);
  const { error } = await sb.from("suivi").upsert(ligne);
  if (error) alert("Le statut n'a pas pu être enregistré : " + error.message);
}
function filtres() {
  const q = $("q").value.trim().toLowerCase(), fm = $("fm").value, fs = $("fs").value;
  const fn = $("fn").checked, ft = $("ft").checked, ref = (R.meta && R.meta.genere_le) || maintenant();
  return prospects.filter(p => !(suivi[p.id] && suivi[p.id].stop) &&
    (!q || `${p.nom} ${p.ville} ${p.adresse}`.toLowerCase().includes(q)) &&
    (!fm || p.metier === fm) &&
    (fs === "" || (fs === "actifs" ? !FINIS.includes(statut(p.id)) : statut(p.id) === fs)) &&
    (!fn || jours(p.premiere_detection, ref) <= 7) &&
    (!ft || p.telephone));
}
function carte(p) {
  const tel = numero(p.telephone), s = statut(p.id), pays = R.data.pays || "CH";
  const mobile = (MOBILE[pays] || MOBILE.CH).test(tel), suisse = pays === "CH", accord = suisse ? " (après accord)" : "";
  const nouveau = jours(p.premiere_detection, (R.meta && R.meta.genere_le) || maintenant()) <= 7;
  const msg = R.data.messages || {};
  const a = [];
  if (p.kit_url) a.push(`<a class="prim" target="_blank" href="${esc(p.kit_url)}">Voir son kit</a>`);
  if (suisse) a.push(`<a target="_blank" href="https://search.ch/tel/?was=${enc(p.nom)}&wo=${enc(p.ville || "")}">Annuaire</a>`);
  a.push(`<a target="_blank" href="https://www.google.com/search?q=${enc(p.nom + " " + (p.ville || ""))}">Google</a>`);
  if (tel) a.push(`<a data-c href="tel:${esc(tel)}">Appeler</a>`);
  if (tel && p.kit_url) a.push(`<a data-c href="sms:${esc(tel)}?&body=${enc(remplir(msg.sms, p))}">SMS${accord}</a>`);
  if (mobile && p.kit_url) a.push(`<a data-c target="_blank" href="https://wa.me/${tel.slice(1)}?text=${enc(remplir(msg.sms, p))}">WhatsApp${accord}</a>`);
  if (p.email && p.kit_url) a.push(`<a data-c href="mailto:${esc(p.email)}?subject=${enc(remplir(msg.email_objet, p))}&body=${enc(remplir(msg.email, p))}">Email${accord}</a>`);
  a.push(`<button class="stop" data-stop>Stop</button>`);
  const tags = [...(nouveau ? ['<span class="tag new">Nouveau</span>'] : []), ...(p.raisons || []).map(r => `<span class="tag">${esc(r)}</span>`)];
  return `<div class="p ${FINIS.includes(s) ? "fait" : ""}" data-id="${esc(p.id)}">
    <div class="ligne"><div><div class="nom">${esc(p.nom)}</div>
      <div class="muted">${esc(metiers()[p.metier] || p.metier)} · ${esc(p.adresse || p.ville)}${p.telephone ? " · " + esc(p.telephone) : ""}</div>
      ${p.activite ? `<div class="muted" style="font-size:13px;margin-top:4px">${esc(p.activite.slice(0, 180))}${p.activite.length > 180 ? "…" : ""}</div>` : ""}</div>
      <select class="statut">${STATUTS.map(x => `<option ${x === s ? "selected" : ""}>${x}</option>`).join("")}</select></div>
    <div class="tags">${tags.join("")}</div>
    <div class="actions">${a.join("")}</div></div>`;
}
function dessiner(reset = true) {
  if (reset) limite = 40;
  const liste = filtres();
  $("liste").innerHTML = liste.slice(0, limite).map(carte).join("") || '<div class="vide">Aucun prospect pour ces filtres.</div>';
  $("plus").hidden = liste.length <= limite;
  const compte = s => prospects.filter(p => statut(p.id) === s).length;
  const ref = (R.meta && R.meta.genere_le) || maintenant();
  $("stats").innerHTML = [["Nouveaux (7 j)", prospects.filter(p => jours(p.premiere_detection, ref) <= 7).length],
    ["À contacter", compte("À contacter")], ["Kits envoyés", compte("Kit envoyé") + compte("Relancé")],
    ["Intéressés", compte("Intéressé")], ["Clients", compte("Client")]]
    .map(([l, n]) => `<div class="stat"><b>${n}</b><span class="muted">${l}</span></div>`).join("");
}
$("liste").addEventListener("change", e => {
  if (e.target.matches("select.statut")) enregistrerSuivi(e.target.closest(".p").dataset.id, { statut: e.target.value });
});
$("liste").addEventListener("click", e => {
  const a = e.target.closest("a[data-c]");
  if (a) { const id = a.closest(".p").dataset.id; if (statut(id) === "À contacter") setTimeout(() => enregistrerSuivi(id, { statut: "Kit envoyé" }), 300); }
  const b = e.target.closest("button[data-stop]");
  if (b) {
    const p = prospects.find(x => x.id === b.closest(".p").dataset.id);
    if (confirm(`Retirer définitivement « ${p.nom} » ? Il ne sera plus jamais contacté et son kit sera supprimé au prochain passage de la machine.`))
      enregistrerSuivi(p.id, { statut: "Pas intéressé", stop: true });
  }
});
for (const id of ["q", "fm", "fs", "fn", "ft"]) $(id).addEventListener("input", () => dessiner());
$("plus").addEventListener("click", () => { limite += 40; dessiner(false); });
$("export").addEventListener("click", () => {
  const lignes = [["nom", "metier", "ville", "telephone", "email", "statut", "kit"]];
  for (const p of prospects) lignes.push([p.nom, metiers()[p.metier] || p.metier, p.ville, p.telephone, p.email, statut(p.id), p.kit_url]);
  const csv = lignes.map(l => l.map(v => `"${String(v ?? "").replace(/"/g, '""')}"`).join(";")).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob(["\uFEFF" + csv], { type: "text/csv" }));
  a.download = `jour-un-${maintenant().slice(0, 10)}.csv`;
  a.click();
});
for (const s of STATUTS) $("fs").insertAdjacentHTML("beforeend", `<option>${s}</option>`);

