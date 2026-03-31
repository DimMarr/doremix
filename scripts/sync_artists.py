import asyncio
import os
import sys

# Add src/back to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "back"))

from database import AsyncSessionLocal
from models.artist import Artist
from models.track import Track
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from utils.youtube_utils import get_youtube_channel_avatar

# Configuration officielle pour les artistes majeurs (pour éviter les doublons via les chaînes non-officielles)
KNOWN_CHANNELS = {
    "Eminem": "https://www.youtube.com/@Eminem",
    "Queen": "https://www.youtube.com/@queenofficial",
    "GIMS": "https://www.youtube.com/@gims",
    "Hans Zimmer": "https://www.youtube.com/@HansZimmer",
    "Daft Punk": "https://www.youtube.com/@daftpunk",
    "Taylor Swift": "https://www.youtube.com/@TaylorSwift",
    "Metallica": "https://www.youtube.com/@metallica",
    "Mozart": "https://www.youtube.com/@KlassicP",  # Chaîne classique référence
    "Imagine Dragons": "https://www.youtube.com/@ImagineDragons",
    "Sia": "https://www.youtube.com/@sia",
    "Stromae": "https://www.youtube.com/@StromaeOfficial",
}


async def sync_artists():
    print("--- Démarrage de la synchronisation des artistes ---")
    async with AsyncSessionLocal() as db:
        # 1. Suppression des artistes sans morceaux (comme l'artiste fictif 'Adele')
        # On récupère tous les artistes avec leur compte de tracks
        result = await db.execute(select(Artist).options(selectinload(Artist.tracks)))
        artists = result.scalars().all()

        for artist in artists:
            if len(artist.tracks) == 0:
                print(f"🗑️ Suppression de l'artiste sans morceaux : {artist.name}")
                await db.delete(artist)

        await db.commit()
        print("✅ Nettoyage terminé.")

        # 2. Mise à jour des images
        # On recharge les artistes restants
        result = await db.execute(select(Artist).options(selectinload(Artist.tracks)))
        artists = result.scalars().all()

        for artist in artists:
            # On force la mise à jour si l'image est manquante ou si c'est un artiste connu
            needs_update = artist.imageUrl is None or artist.name in KNOWN_CHANNELS

            if needs_update:
                channel_url = KNOWN_CHANNELS.get(artist.name)

                # Si pas dans la liste connue, on essaie de déduire via le premier track
                if not channel_url and artist.tracks:
                    # Ici on suppose que le premier track est représentatif de l'artiste
                    # Dans une vraie prod, on pourrait faire plus complexe, mais c'est une bonne base.
                    print(
                        f"🔍 Recherche de chaîne pour {artist.name} via ses morceaux..."
                    )
                    # Note: Dans ce projet, le channel_url est idéalement stocké ou extrait via le repository
                    # On va tenter une extraction simple si possible
                    pass

                if channel_url:
                    print(f"📸 Récupération de l'avatar pour {artist.name}...")
                    try:
                        new_image = get_youtube_channel_avatar(channel_url)
                        if new_image and new_image != artist.imageUrl:
                            artist.imageUrl = new_image
                            print(f"✨ Image mise à jour pour {artist.name}")
                    except Exception as e:
                        print(f"❌ Erreur pour {artist.name}: {e}")
                else:
                    print(
                        f"⚠️ Aucune chaîne trouvée pour {artist.name}, image conservée."
                    )

        await db.commit()
        print("--- Synchronisation terminée avec succès ---")


if __name__ == "__main__":
    asyncio.run(sync_artists())
