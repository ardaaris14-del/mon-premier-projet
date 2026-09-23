/* ---------- Ventes ---------- */
const OFFRES = { "kit+suivi": "Kit + suivi", kit: "Kit seul", mois: "Mensualité" };
const offre = () => (R.data && R.data.offre) || {};
const argent = n => `${offre().devise || "CHF"} ${Number(n || 0).toLocaleString("fr-CH", { maximumFractionDigits: 2 })}`;
const somme = l => l.reduce((t, v) => t + Number(v.montant || 0), 0);
const pluriel = (n, mot) => `${n} ${mot}${n > 1 ? "s" : ""}`;

async function chargerVentes() {
  try {
    const [ventes, clients] = await Promise.all([
      sb.from("ventes").select("*").order("cree_le", { ascending: false }).limit(2000).then(verifier),
      sb.from("clients").select("id, formule, suivi").then(verifier),
    ]);
    const avec = ventes.filter(v => v.offre === "kit+suivi"), sans = ventes.filter(v => v.offre === "kit");
    const mois = maintenant().slice(0, 7), duMois = ventes.filter(v => String(v.cree_le || "").slice(0, 7) === mois);
    const abonnes = clients.filter(c => c.formule !== "kit" && c.suivi).length;
    $("ventes-stats").innerHTML = [
      [avec.length, "Kit + suivi", argent(somme(avec))],
      [sans.length, "Kit seul", argent(somme(sans))],
      [abonnes, "Abonnements actifs", `${argent(abonnes * Number(offre().prix_mois || 0))} / mois`],
      [argent(somme(duMois)), "Encaissé ce mois", pluriel(duMois.length, "paiement")],
      [argent(somme(ventes)), "Total encaissé", pluriel(ventes.length, "paiement")],
    ].map(([n, l, d]) => `<div class="stat"><b>${n}</b><span class="muted">${l}<br>${d}</span></div>`).join("");

    const total = avec.length + sans.length, part = total ? Math.round(avec.length / total * 100) : 0;
    $("ventes-part").innerHTML = total
      ? `<div class="barre">${avec.length ? `<span class="avec" style="width:${part}%">${part} % avec suivi</span>` : ""}${
          sans.length ? `<span class="sans" style="width:${100 - part}%">${100 - part} % sans</span>` : ""}</div>
        <p class="muted">${pluriel(avec.length, "client")} avec suivi, ${pluriel(sans.length, "client")} kit seul.
        Chaque client avec suivi te rapporte ${argent(offre().prix_mois)} de plus chaque mois.</p>`
      : '<p class="muted">Pas encore de vente. La répartition apparaîtra dès le premier paiement.</p>';

    $("ventes-liens").innerHTML = [["Kit + suivi", offre().lien_paiement], ["Kit seul", offre().lien_paiement_kit]]
      .map(([nom, lien]) => `<div class="lien-pay"><b>${nom}</b>${lien
        ? `<code>${esc(lien)}</code><button data-copie-lien="${esc(lien)}">Copier</button><a class="tag" target="_blank" href="${esc(lien)}">Ouvrir</a>`
        : '<span class="muted">Pas de lien : ajoute-le dans Réglages.</span>'}</div>`).join("");

    $("ventes-liste").innerHTML = ventes.slice(0, 50).map(v => `<div class="run"><div><b>${esc(v.entreprise || "—")}</b>
      <span class="tag${v.offre === "kit+suivi" ? " new" : ""}">${OFFRES[v.offre] || esc(v.offre)}</span>
      <div class="muted">${new Date(v.cree_le).toLocaleDateString("fr-CH")} · ${v.source === "stripe" ? "Stripe" : "Ajoutée à la main"}</div></div>
      <div class="actions" style="margin:0"><b>${argent(v.montant)}</b>${v.source === "manuel" ? `<button data-supprimer="${esc(v.id)}">Supprimer</button>` : ""}</div></div>`).join("")
      || '<p class="muted">Aucune vente pour l\'instant.</p>';
    if (!$("vente-ajout").montant.value) $("vente-ajout").offre.dispatchEvent(new Event("change"));
  } catch (e) {
    $("ventes-liste").innerHTML = `<p class="msg ko">${esc(e.message)}</p>`;
  }
}
$("vente-ajout").addEventListener("submit", async e => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  const bouton = e.target.querySelector("button");
  bouton.disabled = true;
  try {
    await sb.from("ventes").insert({ entreprise: f.entreprise.trim(), offre: f.offre, montant: Number(f.montant),
      devise: offre().devise || "CHF", source: "manuel" }).then(verifier);
    e.target.reset();
    message("ventes-msg", "Vente ajoutée ✓", true);
    chargerVentes();
  } catch (err) {
    message("ventes-msg", err.message, false);
  }
  bouton.disabled = false;
});
$("vente-ajout").offre.addEventListener("change", e => {
  const o = offre(), prix = { "kit+suivi": Number(o.prix_kit || 0) + Number(o.prix_mois || 0), kit: o.prix_kit, mois: o.prix_mois }[e.target.value];
  if (prix) $("vente-ajout").montant.value = prix;
});
$("ventes-liste").addEventListener("click", async e => {
  const b = e.target.closest("[data-supprimer]");
  if (!b || !confirm("Supprimer cette vente ?")) return;
  try { await sb.from("ventes").delete().eq("id", b.dataset.supprimer).then(verifier); chargerVentes(); }
  catch (err) { message("ventes-msg", err.message, false); }
});
$("ventes-liens").addEventListener("click", async e => {
  const b = e.target.closest("[data-copie-lien]");
  if (!b) return;
  try { await navigator.clipboard.writeText(b.dataset.copieLien); b.textContent = "Copié !"; } catch (err) {}
});

sb.auth.onAuthStateChange((evenement, session) => { if (evenement !== "TOKEN_REFRESHED") afficher(session); });
