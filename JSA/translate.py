import gzip
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Configuration
FILES_DIR = Path("files")
KANJIDIC_URL = "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"
LOCAL_XML_GZ = FILES_DIR / "kanjidic2.xml.gz"

def ensure_dictionary() -> Path:
    """Download the compressed KANJIDIC2 file if it doesn't exist."""
    FILES_DIR.mkdir(exist_ok=True)
    if not LOCAL_XML_GZ.exists():
        print(f"Downloading KANJIDIC2 dictionary from {KANJIDIC_URL}...")
        # Add a common User-Agent header to protect against potential server-side blocks
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(KANJIDIC_URL, LOCAL_XML_GZ)
        print("Download complete.")
    return LOCAL_XML_GZ

def load_kanji_dictionary(dict_path: Path) -> dict[str, list[str]]:
    print("Parsing KANJIDIC2 XML data...")
    kanji_map = {}
    
    with gzip.open(dict_path, 'rb') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('character'):
                kanji_char = None
                for child in elem:
                    if child.tag.endswith('literal'):
                        kanji_char = child.text
                        break
                        
                if kanji_char:
                    meanings = []
                    for child in elem.iter():
                        # FIX: KANJIDIC2 uses <meaning>, not <gloss>
                        if child.tag.endswith('meaning'):
                            # English definitions are characterized by having NO 'm_lang' attribute
                            if 'm_lang' not in child.attrib and child.text:
                                meanings.append(child.text)
                    if meanings:
                        kanji_map[kanji_char] = meanings
                        
                elem.clear()
                
    print(f"Dictionary ready with {len(kanji_map)} indexed characters.")
    return kanji_map

def sample_cached_rikishi(limit: int = 15) -> list[dict]:
    """Pull unique Japanese/English shikona pairs from Stage 1/2 cache files."""
    cache_files_ja = sorted(FILES_DIR.glob("banzuke_ja_division_*_page_*.json"))
    if not cache_files_ja:
        raise FileNotFoundError("No cached JSA files found in 'files/'. Please run Stage 1/2 first.")
        
    sampled_pairs = []
    
    ja_path = cache_files_ja[0]
    en_path = Path(str(ja_path).replace("banzuke_ja_", "banzuke_en_"))
    
    if not en_path.exists():
        raise FileNotFoundError(f"Could not find matching English banzuke file at {en_path}")

    with open(ja_path, 'r', encoding='utf-8') as f_ja, open(en_path, 'r', encoding='utf-8') as f_en:
        data_ja = json.load(f_ja)
        data_en = json.load(f_en)
        
        rows_ja = data_ja.get("BanzukeTable", [])
        rows_en = data_en.get("BanzukeTable", [])
        
        for row_ja, row_en in zip(rows_ja, rows_en):
            if row_ja.get("banzuke_id") != 0 and row_ja.get("shikona"):
                sampled_pairs.append({
                    "name_ja": row_ja["shikona"],
                    "name_en": row_en.get("shikona", "Unknown")
                })
                if len(sampled_pairs) >= limit:
                    break
                    
    return sampled_pairs

def main():
    # 1. Coordinate and parse dictionary source
    dict_file = ensure_dictionary()
    kanji_lookup = load_kanji_dictionary(dict_file)
    
    # 2. Gather sample data from cache files
    rikishi_samples = sample_cached_rikishi()
    
    # 3. Process and print validation report
    print("\n" + "="*60)
    print(" STAGE 3 PIPELINE REPORT: ATOMIC KANJI TRANSLATION TEST")
    print("="*60)
    
    for rikishi in rikishi_samples:
        # Split the full string into Ring Name and Real Name using the full-width space
        parts = rikishi['name_ja'].split(' ')
        ring_name_ja = parts[0]
        given_name_ja = parts[1] if len(parts) > 1 else ""
        
        print(f"\nWrestler: {rikishi['name_en']}")
        print(f"  -> Ring Name: {ring_name_ja}")
        if given_name_ja:
            print(f"  -> Real Given Name: {given_name_ja}")
        print("-" * 40)
        
        # Focus the atomic dictionary lookup purely on the Ring Name component
        for char in ring_name_ja:
            if char in ["ノ", "乃", "の"]: 
                print(f"  [{char}] -> (Grammatical connector)")
                continue
                
            meanings = kanji_lookup.get(char)
            if meanings:
                display_meanings = ", ".join(meanings[:3])
                print(f"  [{char}] -> {display_meanings}")

if __name__ == "__main__":
    main()
