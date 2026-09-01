"""Interface web locale : glisser-déposer un document, relire, corriger, exporter.

Lancement :  python -m docscan web
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from docscan import config
from docscan.documents import EXTENSIONS_SUPPORTEES, ErreurDocument
from docscan.extraction import ErreurExtraction, extraire
from docscan.modeles import ErreurModele, charger_modele, lister_modeles

app = FastAPI(title="docscan", docs_url=None, redoc_url=None)


@app.get("/", response_class=HTMLResponse)
def page_accueil() -> str:
    return PAGE


@app.get("/api/modeles")
def api_modeles() -> JSONResponse:
    modeles = []
    for nom, chemin in sorted(lister_modeles().items()):
        try:
            modele = charger_modele(chemin)
        except ErreurModele:
            continue
        modeles.append(
            {
                "nom": nom,
                "description": modele.description,
                "champs": [
                    {"nom": c.nom, "libelle": c.libelle, "type": c.type, "choix": c.choix}
                    for c in modele.champs
                ],
            }
        )
    return JSONResponse({"modeles": modeles, "extensions": EXTENSIONS_SUPPORTEES})


@app.post("/api/scan")
async def api_scan(
    fichier: UploadFile = File(...),
    modele: str = Form(...),
    effort: str = Form(config.EFFORT),
) -> JSONResponse:
    try:
        gabarit = charger_modele(modele)
    except ErreurModele as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    suffixe = Path(fichier.filename or "document").suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffixe, delete=False) as tmp:
        tmp.write(await fichier.read())
        chemin_tmp = Path(tmp.name)

    try:
        resultat = extraire(chemin_tmp, gabarit, effort=effort)
    except (ErreurDocument, ErreurExtraction) as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    finally:
        chemin_tmp.unlink(missing_ok=True)

    donnees = resultat.to_dict()
    donnees["document"] = fichier.filename
    donnees["libelles"] = {c.nom: c.libelle for c in gabarit.champs}
    donnees["types"] = {c.nom: c.type for c in gabarit.champs}
    return JSONResponse(donnees)


PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>docscan — remplissage automatique de champs</title>
<style>
  :root {
    color-scheme: light dark;
    --fond: #f6f6f4; --carte: #fff; --texte: #1a1a18; --discret: #6b6b66;
    --bord: #e2e2dd; --accent: #b8562f; --ok: #2f7a4d; --alerte: #b07d15;
  }
  @media (prefers-color-scheme: dark) {
    :root { --fond:#16161a; --carte:#1e1e23; --texte:#ececea; --discret:#9a9a94;
            --bord:#33333a; --accent:#e08a5f; --ok:#68c08d; --alerte:#e0b44a; }
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--fond); color:var(--texte);
         font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 900px; margin: 0 auto; padding: 32px 20px 64px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  p.sous { color: var(--discret); margin: 0 0 28px; }
  .carte { background:var(--carte); border:1px solid var(--bord); border-radius:10px;
           padding:20px; margin-bottom:18px; }
  label { display:block; font-weight:600; margin-bottom:6px; font-size:13px; }
  select, input[type=text] { width:100%; padding:9px 10px; border:1px solid var(--bord);
           border-radius:7px; background:var(--fond); color:var(--texte); font:inherit; }
  #zone { border:2px dashed var(--bord); border-radius:10px; padding:34px; text-align:center;
          color:var(--discret); cursor:pointer; transition:.15s; margin-top:16px; }
  #zone.survol { border-color:var(--accent); color:var(--accent); }
  button { background:var(--accent); color:#fff; border:0; border-radius:7px;
           padding:9px 16px; font:inherit; font-weight:600; cursor:pointer; }
  button.secondaire { background:transparent; color:var(--accent);
                      border:1px solid var(--accent); }
  button:disabled { opacity:.5; cursor:not-allowed; }
  table { width:100%; border-collapse:collapse; }
  th, td { text-align:left; padding:8px 6px; border-bottom:1px solid var(--bord);
           vertical-align:top; }
  th { font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--discret); }
  td.champ { width:34%; font-weight:600; }
  td.note { width:80px; text-align:right; font-variant-numeric:tabular-nums; font-size:13px; }
  .vide { color:var(--discret); font-style:italic; }
  .haute { color:var(--ok); } .basse { color:var(--alerte); }
  .barre { display:flex; gap:10px; align-items:center; margin-top:16px; flex-wrap:wrap; }
  .msg { padding:11px 14px; border-radius:8px; margin-top:14px; }
  .msg.err { background:rgba(184,86,47,.12); color:var(--accent); }
  .msg.info { background:rgba(176,125,21,.14); color:var(--alerte); }
  pre { overflow-x:auto; background:var(--fond); padding:12px; border-radius:8px;
        border:1px solid var(--bord); font-size:12px; }
  .patiente::after { content:"…"; animation:points 1.2s steps(4,end) infinite; }
  @keyframes points { 0%{content:""} 25%{content:"."} 50%{content:".."} 75%{content:"..."} }
</style>
</head>
<body>
<main>
  <h1>docscan</h1>
  <p class="sous">Déposez un document scanné : l'IA lit son contenu et remplit vos champs.</p>

  <div class="carte">
    <label for="modele">Modèle de champs</label>
    <select id="modele"></select>
    <p id="apercu" class="sous" style="margin:8px 0 0;font-size:13px"></p>
    <div id="zone">
      <strong>Cliquez ou déposez un fichier ici</strong><br>
      <span id="formats"></span>
    </div>
    <input type="file" id="fichier" hidden>
    <div id="etat"></div>
  </div>

  <div class="carte" id="resultats" hidden>
    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px">
      <strong id="nom-doc"></strong>
      <span class="sous" id="type-doc" style="font-size:13px"></span>
    </div>
    <div id="remarques"></div>
    <table>
      <thead><tr><th>Champ</th><th>Valeur détectée (modifiable)</th><th class="note">Confiance</th></tr></thead>
      <tbody id="lignes"></tbody>
    </table>
    <div class="barre">
      <button id="copier" class="secondaire">Copier le JSON</button>
      <button id="telecharger-json" class="secondaire">Télécharger .json</button>
      <button id="telecharger-csv" class="secondaire">Télécharger .csv</button>
    </div>
  </div>
</main>

<script>
const $ = (id) => document.getElementById(id);
let modeles = [], resultat = null;

async function init() {
  const rep = await fetch('/api/modeles').then(r => r.json());
  modeles = rep.modeles;
  $('formats').textContent = 'Formats : ' + rep.extensions.join(', ');
  $('modele').innerHTML = modeles
    .map(m => `<option value="${m.nom}">${m.nom} — ${m.description || ''}</option>`)
    .join('');
  majApercu();
}

function majApercu() {
  const m = modeles.find(m => m.nom === $('modele').value);
  $('apercu').textContent = m ? `${m.champs.length} champs : ` +
    m.champs.map(c => c.nom).join(', ') : '';
}

function message(texte, type) {
  $('etat').innerHTML = texte ? `<div class="msg ${type}">${texte}</div>` : '';
}

async function envoyer(fichier) {
  if (!fichier) return;
  $('resultats').hidden = true;
  message(`<span class="patiente">Lecture de ${fichier.name} en cours</span>`, 'info');

  const corps = new FormData();
  corps.append('fichier', fichier);
  corps.append('modele', $('modele').value);
  try {
    const rep = await fetch('/api/scan', { method: 'POST', body: corps });
    const donnees = await rep.json();
    if (!rep.ok) { message(donnees.detail || 'Échec de la lecture.', 'err'); return; }
    resultat = donnees;
    afficher(donnees);
    message('', '');
  } catch (e) {
    message('Erreur réseau : ' + e.message, 'err');
  }
}

function afficher(d) {
  $('nom-doc').textContent = d.document;
  $('type-doc').textContent = d.type_document ? 'reconnu : ' + d.type_document : '';
  $('remarques').innerHTML = d.remarques
    ? `<div class="msg info">${d.remarques}</div>` : '';

  $('lignes').innerHTML = Object.entries(d.champs).map(([nom, valeur]) => {
    const note = d.confiance?.[nom];
    const vide = valeur === null || valeur === '' ||
                 (Array.isArray(valeur) && valeur.length === 0);
    const texte = vide ? '' : (typeof valeur === 'object'
      ? JSON.stringify(valeur) : String(valeur));
    const classeNote = note >= 0.8 ? 'haute' : 'basse';
    return `<tr>
      <td class="champ">${d.libelles?.[nom] || nom}<br>
        <span class="sous" style="font-weight:400;font-size:12px">${nom}</span></td>
      <td><input type="text" data-champ="${nom}" value="${texte.replace(/"/g, '&quot;')}"
            placeholder="${vide ? 'non trouvé — à saisir' : ''}"></td>
      <td class="note ${vide ? '' : classeNote}">${
        note === undefined || note === null ? '' : Math.round(note * 100) + '%'}</td>
    </tr>`;
  }).join('');
  $('resultats').hidden = false;
}

function valeursCorrigees() {
  const sortie = {};
  document.querySelectorAll('#lignes input[data-champ]').forEach(i => {
    sortie[i.dataset.champ] = i.value === '' ? null : i.value;
  });
  return sortie;
}

function telecharger(nom, contenu, type) {
  const url = URL.createObjectURL(new Blob([contenu], { type }));
  const a = Object.assign(document.createElement('a'), { href: url, download: nom });
  a.click();
  URL.revokeObjectURL(url);
}

$('modele').addEventListener('change', majApercu);
$('zone').addEventListener('click', () => $('fichier').click());
$('fichier').addEventListener('change', e => envoyer(e.target.files[0]));
['dragenter', 'dragover'].forEach(ev => $('zone').addEventListener(ev, e => {
  e.preventDefault(); $('zone').classList.add('survol');
}));
['dragleave', 'drop'].forEach(ev => $('zone').addEventListener(ev, e => {
  e.preventDefault(); $('zone').classList.remove('survol');
}));
$('zone').addEventListener('drop', e => envoyer(e.dataTransfer.files[0]));

$('copier').addEventListener('click', async () => {
  await navigator.clipboard.writeText(JSON.stringify(valeursCorrigees(), null, 2));
  $('copier').textContent = 'Copié !';
  setTimeout(() => ($('copier').textContent = 'Copier le JSON'), 1500);
});
$('telecharger-json').addEventListener('click', () => telecharger(
  'docscan.json', JSON.stringify(valeursCorrigees(), null, 2), 'application/json'));
$('telecharger-csv').addEventListener('click', () => {
  const v = valeursCorrigees();
  const echappe = (x) => `"${String(x ?? '').replace(/"/g, '""')}"`;
  const csv = Object.keys(v).map(echappe).join(';') + '\\n' +
              Object.values(v).map(echappe).join(';');
  telecharger('docscan.csv', csv, 'text/csv');
});

init();
</script>
</body>
</html>
"""
