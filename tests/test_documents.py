"""Lecture des fichiers et conversion en blocs de contenu."""

import base64

import pytest

from docscan.documents import ErreurDocument, bloc_document, fichiers_du_dossier


def test_image_devient_un_bloc_image(tmp_path):
    fichier = tmp_path / "scan.png"
    fichier.write_bytes(b"\x89PNG\r\n\x1a\n fausse image")
    bloc = bloc_document(fichier)
    assert bloc["type"] == "image"
    assert bloc["source"]["media_type"] == "image/png"
    assert base64.standard_b64decode(bloc["source"]["data"]).startswith(b"\x89PNG")


def test_pdf_devient_un_bloc_document(tmp_path):
    fichier = tmp_path / "facture.pdf"
    fichier.write_bytes(b"%PDF-1.4 faux pdf")
    bloc = bloc_document(fichier)
    assert bloc["type"] == "document"
    assert bloc["source"]["media_type"] == "application/pdf"


def test_texte_est_envoye_tel_quel(tmp_path):
    fichier = tmp_path / "note.txt"
    fichier.write_text("Facture n°42", encoding="utf-8")
    bloc = bloc_document(fichier)
    assert bloc["source"]["type"] == "text"
    assert "42" in bloc["source"]["data"]


def test_format_non_supporte(tmp_path):
    fichier = tmp_path / "archive.zip"
    fichier.write_bytes(b"PK\x03\x04")
    with pytest.raises(ErreurDocument, match="Format non pris en charge"):
        bloc_document(fichier)


def test_fichier_absent(tmp_path):
    with pytest.raises(ErreurDocument, match="introuvable"):
        bloc_document(tmp_path / "rien.png")


def test_fichier_vide(tmp_path):
    fichier = tmp_path / "vide.png"
    fichier.write_bytes(b"")
    with pytest.raises(ErreurDocument, match="vide"):
        bloc_document(fichier)


def test_fichier_trop_gros(tmp_path, monkeypatch):
    monkeypatch.setattr("docscan.documents.TAILLE_MAX_OCTETS", 10)
    fichier = tmp_path / "gros.png"
    fichier.write_bytes(b"x" * 100)
    with pytest.raises(ErreurDocument, match="trop volumineux"):
        bloc_document(fichier)


def test_parcours_de_dossier(tmp_path):
    (tmp_path / "b.pdf").write_bytes(b"%PDF")
    (tmp_path / "a.png").write_bytes(b"\x89PNG")
    (tmp_path / "notes.zip").write_bytes(b"PK")
    assert [f.name for f in fichiers_du_dossier(tmp_path)] == ["a.png", "b.pdf"]
