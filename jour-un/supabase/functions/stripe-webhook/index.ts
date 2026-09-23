// Reçoit les paiements Stripe : enregistre chaque vente, crée le client et passe le prospect en « Client ».
import { createClient } from "npm:@supabase/supabase-js@2.117.1";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false },
});
const texte = new TextEncoder();
const TOLERANCE = 300;
let cles: { secret: string; liens: string[] } | null = null;

// Le secret de signature et les liens de paiement web-design.ch (les autres ventes du compte Stripe sont ignorées).
async function lireCles() {
  if (!cles) {
    const { data, error } = await sb.from("cles").select("nom, valeur").in("nom", ["stripe_webhook", "stripe_liens"]);
    if (error) throw error;
    const v = Object.fromEntries(data.map((c) => [c.nom, c.valeur]));
    cles = { secret: v.stripe_webhook ?? "", liens: String(v.stripe_liens ?? "").split(",").filter(Boolean) };
  }
  return cles;
}

async function signatureValide(corps: string, entete: string, cle: string) {
  let t = 0;
  const signatures: string[] = [];
  for (const morceau of entete.split(",")) {
    const [k, v] = morceau.split("=", 2);
    if (k === "t") t = Number(v);
    if (k === "v1" && v) signatures.push(v);
  }
  if (!t || !signatures.length || Math.abs(Date.now() / 1000 - t) > TOLERANCE) return false;
  const k = await crypto.subtle.importKey("raw", texte.encode(cle), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const brut = new Uint8Array(await crypto.subtle.sign("HMAC", k, texte.encode(`${t}.${corps}`)));
  const attendu = Array.from(brut, (o) => o.toString(16).padStart(2, "0")).join("");
  return signatures.some((s) => s.length === attendu.length && [...s].reduce((d, c, i) => d | (c.charCodeAt(0) ^ attendu.charCodeAt(i)), 0) === 0);
}

const chiffres = (s?: string | null) => String(s ?? "").replace(/\D/g, "").slice(-9);
const simple = (s?: string | null) =>
  String(s ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
    .replace(/\b(sarl|sa|gmbh|ag|sagl|snc|sas|sasu|eurl)\b/g, "").replace(/[^a-z0-9]+/g, " ").trim();

async function trouverProspect(nom: string, tel: string | null) {
  const { data, error } = await sb.from("prospects").select("id, nom, metier, ville, telephone").limit(5000);
  if (error) throw error;
  const t = chiffres(tel), n = simple(nom);
  return (t.length === 9 && data.find((p) => chiffres(p.telephone) === t)) || (n && data.find((p) => simple(p.nom) === n)) || null;
}

// Enregistre la vente une seule fois, même si Stripe envoie l'événement plusieurs fois.
async function enregistrerVente(vente: Record<string, unknown>) {
  const { error } = await sb.from("ventes").insert({ ...vente, source: "stripe" });
  if (error?.code === "23505") return false;
  if (error) throw error;
  return true;
}

async function paiementCheckout(s: any, liens: string[]) {
  if (s.payment_status !== "paid" || !liens.includes(s.payment_link)) return;
  const offre = s.mode === "subscription" ? "kit+suivi" : "kit";
  const champ = (s.custom_fields ?? []).find((c: any) => c.key === "entreprise");
  const entreprise = (champ?.text?.value || s.customer_details?.name || "Client").trim();
  const tel = s.customer_details?.phone ?? null, email = s.customer_details?.email ?? null;
  const nouvelle = await enregistrerVente({
    id: s.id, offre, montant: (s.amount_total ?? 0) / 100, devise: String(s.currency ?? "chf").toUpperCase(),
    entreprise, email, telephone: tel,
  });
  if (!nouvelle) return;
  const prospect = await trouverProspect(entreprise, tel);
  const { data: client, error } = await sb.from("clients").insert({
    nom: prospect?.nom ?? entreprise,
    metier: prospect?.metier ?? "generique",
    ville: prospect?.ville ?? "",
    telephone: tel ?? prospect?.telephone ?? null,
    email,
    formule: offre,
    suivi: offre === "kit+suivi",
    prospect_id: prospect?.id ?? null,
    stripe_client: typeof s.customer === "string" ? s.customer : null,
    stripe_abonnement: typeof s.subscription === "string" ? s.subscription : null,
  }).select("id").single();
  if (error) throw error;
  const lien = await sb.from("ventes").update({ client_id: client.id }).eq("id", s.id);
  if (lien.error) throw lien.error;
  if (prospect) {
    const suivi = await sb.from("suivi").upsert({ prospect_id: prospect.id, statut: "Client", stop: false, maj: new Date().toISOString() });
    if (suivi.error) throw suivi.error;
  }
}

async function factureMensuelle(f: any) {
  if (f.billing_reason !== "subscription_cycle" || !f.amount_paid) return;
  const abonnement = f.subscription ?? f.parent?.subscription_details?.subscription ?? null;
  const { data: client } = await sb.from("clients").select("id, nom").eq("stripe_abonnement", abonnement).maybeSingle();
  if (!client) return;
  await enregistrerVente({
    id: f.id, offre: "mois", montant: f.amount_paid / 100, devise: String(f.currency ?? "chf").toUpperCase(),
    entreprise: client.nom, email: f.customer_email ?? null, client_id: client.id,
  });
}

async function finAbonnement(a: any) {
  const { error } = await sb.from("clients").update({ suivi: false }).eq("stripe_abonnement", a.id);
  if (error) throw error;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Méthode non autorisée", { status: 405 });
  const corps = await req.text();
  try {
    const { secret, liens } = await lireCles();
    if (!secret || !(await signatureValide(corps, req.headers.get("stripe-signature") ?? "", secret))) {
      return new Response("Signature invalide", { status: 400 });
    }
    const evenement = JSON.parse(corps);
    const objet = evenement.data?.object ?? {};
    if (evenement.type === "checkout.session.completed" || evenement.type === "checkout.session.async_payment_succeeded") await paiementCheckout(objet, liens);
    if (evenement.type === "invoice.paid") await factureMensuelle(objet);
    if (evenement.type === "customer.subscription.deleted") await finAbonnement(objet);
    return Response.json({ recu: true });
  } catch (err) {
    console.error(err);
    return new Response("Erreur", { status: 500 });
  }
});
