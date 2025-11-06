"""
Villager Portrait Scraper

Downloads villager portraits from Stardew Valley Wiki.
"""

import requests
from pathlib import Path
from villager_database import get_all_villagers
import time

# Base URL for Stardew Valley Wiki
WIKI_BASE = "https://stardewvalleywiki.com"

# Portrait URL mapping (MediaWiki format)
PORTRAIT_URLS = {
    "Abigail": "/mediawiki/images/8/88/Abigail.png",
    "Alex": "/mediawiki/images/0/04/Alex.png",
    "Caroline": "/mediawiki/images/8/87/Caroline.png",
    "Clint": "/mediawiki/images/3/31/Clint.png",
    "Demetrius": "/mediawiki/images/f/f9/Demetrius.png",
    "Dwarf": "/mediawiki/images/e/ed/Dwarf.png",
    "Elliott": "/mediawiki/images/b/bd/Elliott.png",
    "Emily": "/mediawiki/images/2/28/Emily.png",
    "Evelyn": "/mediawiki/images/8/8e/Evelyn.png",
    "George": "/mediawiki/images/7/78/George.png",
    "Gus": "/mediawiki/images/5/52/Gus.png",
    "Haley": "/mediawiki/images/1/1b/Haley.png",
    "Harvey": "/mediawiki/images/9/95/Harvey.png",
    "Jas": "/mediawiki/images/5/55/Jas.png",
    "Jodi": "/mediawiki/images/4/41/Jodi.png",
    "Kent": "/mediawiki/images/9/99/Kent.png",
    "Krobus": "/mediawiki/images/7/71/Krobus.png",
    "Leah": "/mediawiki/images/e/e6/Leah.png",
    "Lewis": "/mediawiki/images/2/2b/Lewis.png",
    "Linus": "/mediawiki/images/3/31/Linus.png",
    "Marnie": "/mediawiki/images/5/52/Marnie.png",
    "Maru": "/mediawiki/images/f/f8/Maru.png",
    "Pam": "/mediawiki/images/d/da/Pam.png",
    "Penny": "/mediawiki/images/a/ab/Penny.png",
    "Pierre": "/mediawiki/images/7/7e/Pierre.png",
    "Robin": "/mediawiki/images/1/1b/Robin.png",
    "Sam": "/mediawiki/images/9/94/Sam.png",
    "Sebastian": "/mediawiki/images/a/a8/Sebastian.png",
    "Shane": "/mediawiki/images/8/8b/Shane.png",
    "Vincent": "/mediawiki/images/f/f1/Vincent.png",
    "Willy": "/mediawiki/images/8/82/Willy.png",
    "Wizard": "/mediawiki/images/c/c7/Wizard.png",
}


def download_portraits(output_dir: Path = None):
    """
    Download all villager portraits from the wiki.

    Args:
        output_dir: Directory to save portraits (defaults to dashboard/portraits)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "dashboard" / "portraits"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading portraits to: {output_dir}")
    print(f"Total villagers: {len(PORTRAIT_URLS)}")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for villager, url_path in PORTRAIT_URLS.items():
        full_url = WIKI_BASE + url_path
        output_file = output_dir / f"{villager}.png"

        # Skip if already downloaded
        if output_file.exists():
            print(f"[OK] {villager:15} - Already exists")
            success_count += 1
            continue

        try:
            # Download image
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()

            # Save to file
            with open(output_file, 'wb') as f:
                f.write(response.content)

            print(f"[OK] {villager:15} - Downloaded ({len(response.content)} bytes)")
            success_count += 1

            # Be nice to the server
            time.sleep(0.5)

        except requests.RequestException as e:
            print(f"[FAIL] {villager:15} - Failed: {e}")
            failed_count += 1

    print("=" * 60)
    print(f"Download complete!")
    print(f"Success: {success_count}/{len(PORTRAIT_URLS)}")
    print(f"Failed: {failed_count}/{len(PORTRAIT_URLS)}")

    return success_count, failed_count


if __name__ == "__main__":
    download_portraits()
