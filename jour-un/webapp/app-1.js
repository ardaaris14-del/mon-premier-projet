const SUPABASE_URL = "https://pnngtkpweyjohbjkremi.supabase.co";
const SUPABASE_CLE = "sb_publishable_NVPaDufXCrYPtGgt-Sp3ag_aO42ulmM";
const sb = supabase.createClient(SUPABASE_URL, SUPABASE_CLE);

const STATUTS = ["À contacter", "Kit envoyé", "Relancé", "Intéressé", "Client", "Pas intéressé"];
const FINIS = ["Client", "Pas intéressé"];
const CANTONS = { JU: "Jura", NE: "Neuchâtel", VD: "Vaud", GE: "Genève", FR: "Fribourg", VS: "Valais", BE: "Berne" };
const METIERS_PAR_DEFAUT = {"plombier":"Plombier chauffagiste","electricien":"Électricien","peintre":"Peintre en bâtiment","menuisier":"Menuisier","couvreur":"Couvreur","coiffeur":"Salon de coiffure","estheticienne":"Institut de beauté","garage":"Garage automobile","macon":"Maçonnerie et construction","carreleur":"Carreleur","paysagiste":"Paysagiste","nettoyage":"Entreprise de nettoyage","restaurant":"Restaurant","transport":"Transport et déménagement","informatique":"Services informatiques","fitness":"Coach sportif","photographe":"Photographe","generique":"Entreprise"};
const MOBILE = { CH: /^\+417[5-9]\d{7}$/, FR: /^\+33[67]\d{8}$/ };

const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const enc = encodeURIComponent;
const jours = (a, b) => (new Date(b) - new Date(a)) / 864e5;
const maintenant = () => new Date().toISOString();
const message = (id, texte, ok) => { const el = $(id); el.textContent = texte; el.className = "msg " + (ok ? "ok" : "ko"); };
const stock = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
const verifier = ({ data, error }) => { if (error) throw new Error(error.message); return data; };

let R = { data: {}, meta: {} }, prospects = [], suivi = {}, limite = 40;
const metiers = () => (R.meta && R.meta.metiers) || METIERS_PAR_DEFAUT;
const statut = id => (suivi[id] && suivi[id].statut) || "À contacter";

/* ---------- Connexion ---------- */
async function afficher(session) {
  $("connexion").hidden = !!session;
  $("app").hidden = !session;
  if (!session) return;
  $("compte-email").textContent = "Connecté avec " + session.user.email;
  try { await charger(); } catch (e) { $("maj").textContent = "Erreur de chargement : " + e.message; }
}
$("connexion").addEventListener("submit", async e => {
  e.preventDefault();
  const { error } = await sb.auth.signInWithPassword({ email: $("email").value.trim(), password: $("mdp").value });
  if (error) message("connexion-msg", error.message.includes("Invalid") ? "Email ou mot de passe incorrect." : error.message, false);
});
$("creer").addEventListener("click", async () => {
  const email = $("email").value.trim(), password = $("mdp").value;
  if (!email || password.length < 8) return message("connexion-msg", "Entre ton email et un mot de passe d'au moins 8 caractères, puis clique à nouveau.", false);
  const { error } = await sb.auth.signUp({ email, password });
  if (error && !/confirm|email/i.test(error.message)) return message("connexion-msg", error.message.includes("Inscription") || error.message.includes("Database") ? "Cet email n'est pas autorisé." : error.message, false);
  const r = await sb.auth.signInWithPassword({ email, password });
  if (r.error) message("connexion-msg", "Compte créé. Si la connexion ne marche pas encore, réessaie dans une minute. (" + r.error.message + ")", false);
});
$("deconnexion").addEventListener("click", () => sb.auth.signOut());

/* ---------- Données ---------- */
async function charger() {
  const [reglages, liste, suivis] = await Promise.all([
    sb.from("reglages").select("data, meta").eq("id", 1).maybeSingle().then(verifier),
    sb.from("prospects").select("*").order("score", { ascending: false }).limit(2000).then(verifier),
    sb.from("suivi").select("*").then(verifier),
  ]);
  R = reglages || { data: {}, meta: {} };
  prospects = liste;
  suivi = Object.fromEntries(suivis.map(s => [s.prospect_id, s]));
  const genere = R.meta && R.meta.genere_le;
  $("maj").textContent = genere
    ? `Mis à jour le ${new Date(genere).toLocaleString("fr-CH", { dateStyle: "short", timeStyle: "short" })} · ${prospects.length} nouvelles entreprises avec leur kit prêt`
    : "La machine n'a pas encore rempli la base : lance-la depuis l'onglet Machine.";
  $("fm").innerHTML = '<option value="">Tous les métiers</option>' + [...new Set(prospects.map(p => p.metier))]
    .map(m => `<option value="${esc(m)}">${esc(metiers()[m] || m)}</option>`).join("");
  $("client-metier").innerHTML = Object.entries(metiers()).map(([k, n]) => `<option value="${k}">${esc(n)}</option>`).join("");
  if (R.meta && R.meta.url_kits) $("lien-public").href = R.meta.url_kits;
  dessiner();
  montrer(stock.get("ju-onglet") || "prospects");
}

/* ---------- Onglets ---------- */
function montrer(nom) {
  document.querySelectorAll("[data-onglet]").forEach(s => { s.hidden = s.dataset.onglet !== nom; });
  document.querySelectorAll("nav.onglets button").forEach(b => b.classList.toggle("actif", b.dataset.vers === nom));
  stock.set("ju-onglet", nom);
  if (nom === "clients") chargerClients();
  if (nom === "reglages") remplirReglages();
  if (nom === "machine") chargerMachine();
}
document.querySelectorAll("nav.onglets button").forEach(b => b.addEventListener("click", () => montrer(b.dataset.vers)));

