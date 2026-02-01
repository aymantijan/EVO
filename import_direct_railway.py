"""
Import ultra-rapide vers Railway Postgres via COPY
Compatible colonnes NOT NULL (created_at / updated_at)
"""

import csv
import os
import psycopg2
from urllib.parse import urlparse
from io import StringIO
from datetime import datetime, UTC

def get_railway_db_url():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   ⚡ IMPORT RAPIDE VIA COPY (POSTGRES)                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("railway.app → Projet → Postgres → Variables / Connect")
    print("Copiez DATABASE_URL")
    print()
    return input("Collez DATABASE_URL ici : ").strip()


def import_with_copy(csv_file, db_url):
    result = urlparse(db_url)

    print("\n🔌 Connexion à Railway Postgres...")
    conn = psycopg2.connect(
        host=result.hostname,
        port=result.port,
        database=result.path.lstrip("/"),
        user=result.username,
        password=result.password,
    )
    cursor = conn.cursor()
    print("✅ Connecté")

    print("\n📦 Préparation des données pour COPY...")

    buffer = StringIO()
    writer = csv.writer(buffer, delimiter="\t", quoting=csv.QUOTE_MINIMAL)

    now = datetime.now(UTC)
    total = 0

    with open(csv_file, "r", encoding="latin-1", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            titre = row.get("titre", "").strip()
            if not titre:
                continue

            writer.writerow([
                titre,
                row.get("auteur", "").strip(),
                row.get("type", "").strip(),
                row.get("domaine", "").strip(),
                row.get("description", "").strip(),
                int(row.get("niveau") or 1),
                row.get("url", "").strip(),
                row.get("image", "").strip(),
                str(row.get("is_active", "true")).lower() in ("true", "1", "yes", "oui"),
                now,   # created_at
                now,   # updated_at
            ])
            total += 1

    buffer.seek(0)

    print(f"🚀 Envoi de {total:,} lignes vers PostgreSQL...")

    try:
        cursor.copy_from(
            buffer,
            "gamification_resource",
            sep="\t",
            columns=(
                "titre",
                "auteur",
                "type",
                "domaine",
                "description",
                "niveau",
                "url",
                "image",
                "is_active",
                "created_at",
                "updated_at",
            ),
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"❌ COPY échoué : {e}")

    cursor.execute("SELECT COUNT(*) FROM gamification_resource")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("✅ IMPORT TERMINÉ AVEC SUCCÈS")
    print("=" * 60)
    print(f"📥 Importées : {total:,}")
    print(f"📚 Total DB  : {count:,}")
    print("=" * 60)


if __name__ == "__main__":
    csv_file = "all_resources.csv"

    if not os.path.exists(csv_file):
        print(f"❌ Fichier {csv_file} introuvable")
        exit(1)

    try:
        import psycopg2  # noqa
    except ImportError:
        print("❌ psycopg2 manquant → pip install psycopg2-binary")
        exit(1)

    db_url = get_railway_db_url()

    print("\n⚠️  Import massif (~106 000 lignes)")
    confirm = input("Tapez 'OUI' pour confirmer : ")

    if confirm != "OUI":
        print("❌ Import annulé")
        exit(0)

    import_with_copy(csv_file, db_url)
