"""
Suppression TOTALE des ressources dans gamification_resource
Attention : opération IRRÉVERSIBLE
"""

import psycopg2
from urllib.parse import urlparse


def get_railway_db_url():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🧨 SUPPRESSION TOTALE DES RESSOURCES                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("railway.app → Projet → Postgres → Variables / Connect")
    print("Copiez DATABASE_URL")
    print()
    return input("Collez DATABASE_URL ici : ").strip()


def delete_all_resources(db_url):
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

    # Vérifier combien de lignes existent
    cursor.execute("SELECT COUNT(*) FROM gamification_resource;")
    total = cursor.fetchone()[0]

    print(f"\n📊 Ressources actuelles dans la base : {total:,}")

    if total == 0:
        print("✅ La table est déjà vide")
        cursor.close()
        conn.close()
        return

    print("\n⚠️  ATTENTION : cette action va SUPPRIMER TOUTES les ressources")
    confirm = input("Tapez 'SUPPRIMER' pour confirmer : ")

    if confirm != "SUPPRIMER":
        print("❌ Opération annulée")
        cursor.close()
        conn.close()
        return

    print("\n🧨 Suppression en cours...")

    # Suppression totale
    cursor.execute("""
        TRUNCATE TABLE gamification_resource
        RESTART IDENTITY
        CASCADE;
    """)

    conn.commit()

    print("✅ Toutes les ressources ont été supprimées")
    print("🔁 Les IDs ont été réinitialisés")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    db_url = get_railway_db_url()
    delete_all_resources(db_url)
