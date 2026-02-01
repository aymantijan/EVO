"""
Suppression des doublons dans gamification_resource
Garde une seule ligne par titre (la plus ancienne)
Compatible Railway Postgres
"""

import psycopg2
from urllib.parse import urlparse


def get_railway_db_url():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🧹 SUPPRESSION DES DOUBLONS (POSTGRES)                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("railway.app → Projet → Postgres → Variables / Connect")
    print("Copiez DATABASE_URL")
    print()
    return input("Collez DATABASE_URL ici : ").strip()


def remove_duplicates(db_url):
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

    # 1️⃣ Compter les doublons avant
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT titre
            FROM gamification_resource
            GROUP BY titre
            HAVING COUNT(*) > 1
        ) t;
    """)
    duplicates_before = cursor.fetchone()[0]

    print(f"\n📊 Titres dupliqués détectés : {duplicates_before}")

    if duplicates_before == 0:
        print("✅ Aucun doublon à supprimer")
        cursor.close()
        conn.close()
        return

    confirm = input("\n⚠️  Supprimer les doublons et garder 1 ligne par titre ? (OUI) : ")
    if confirm != "OUI":
        print("❌ Opération annulée")
        cursor.close()
        conn.close()
        return

    print("\n🧹 Suppression des doublons en cours...")

    # 2️⃣ Suppression (on garde l'id le plus petit)
    cursor.execute("""
        DELETE FROM gamification_resource a
        USING gamification_resource b
        WHERE a.titre = b.titre
          AND a.id > b.id;
    """)

    deleted = cursor.rowcount
    conn.commit()

    # 3️⃣ Vérification finale
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT titre
            FROM gamification_resource
            GROUP BY titre
            HAVING COUNT(*) > 1
        ) t;
    """)
    duplicates_after = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM gamification_resource;")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("✅ DÉDOUBLONNAGE TERMINÉ")
    print("=" * 60)
    print(f"🗑️  Lignes supprimées : {deleted:,}")
    print(f"📚 Total restant      : {total:,}")
    print(f"🔁 Doublons restants  : {duplicates_after}")
    print("=" * 60)


if __name__ == "__main__":
    db_url = get_railway_db_url()
    remove_duplicates(db_url)
