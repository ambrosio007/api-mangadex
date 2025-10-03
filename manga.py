from flask import Flask, jsonify, request, render_template
import requests
import os

app = Flask(__name__)

BASE_URL = "https://api.mangadex.org"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome = request.form.get("nome_manga")
        incluir = request.form.getlist("incluir")  # nomes das tags
        excluir = request.form.getlist("excluir")

        mangas = buscar_mangas(nome, incluir, excluir)

        return render_template("buscar.html", mangas=mangas)

    return render_template("buscar.html")

import requests

def buscar_mangas(title, included_tag_names, excluded_tag_names):
    # 1. Pegar todas as tags do MangaDex
    tags_resp = requests.get(f"{BASE_URL}/manga/tag").json()

    # 2. Mapear nomes → IDs
    included_tag_ids = [
        tag["id"]
        for tag in tags_resp["data"]
        if tag["attributes"]["name"]["en"].lower()
        in [t.lower() for t in included_tag_names]
    ]

    excluded_tag_ids = [
        tag["id"]
        for tag in tags_resp["data"]
        if tag["attributes"]["name"]["en"].lower()
        in [t.lower() for t in excluded_tag_names]
    ]

    # 3. Montar requisição para a API de mangas (já incluindo cover_art)
    params = {"title": title, "limit": 10, "includes[]": "cover_art"}
    for tag_id in included_tag_ids:
        params.setdefault("includedTags[]", []).append(tag_id)
    for tag_id in excluded_tag_ids:
        params.setdefault("excludedTags[]", []).append(tag_id)

    # 4. Chamar a API do MangaDex
    r = requests.get(f"{BASE_URL}/manga", params=params)
    data = r.json()

    mangas = []
    for manga in data.get("data", []):
        attrs = manga["attributes"]

        cover_file = None
        for rel in manga.get("relationships", []):
            if rel["type"] == "cover_art":
                cover_file = rel["attributes"]["fileName"]
                break

        capa_url = "/static/img/placeholder.jpg"  # Default

        if cover_file:
            # Tentar miniatura 256px (geralmente pública)
            thumb_url = f"https://uploads.mangadex.org/covers/{manga['id']}/{cover_file}.256.jpg"
            try:
                head = requests.head(thumb_url)
                if head.status_code == 200 and 'image' in head.headers.get('Content-Type', ''):
                    capa_url = thumb_url
                else:
                    # fallback para a capa original
                    original_url = f"https://uploads.mangadex.org/covers/{manga['id']}/{cover_file}"
                    head2 = requests.head(original_url)
                    if head2.status_code == 200 and 'image' in head2.headers.get('Content-Type', ''):
                        capa_url = original_url
            except:
                # Qualquer erro, mantém placeholder
                pass

        mangas.append({
            "id": manga["id"],
            "title": attrs["title"].get("en") or list(attrs["title"].values())[0],
            "status": attrs.get("status"),
            "cover": capa_url
        })

    return mangas


if __name__ == "__main__":
    app.run(debug=True)