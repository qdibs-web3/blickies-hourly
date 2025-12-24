import json
import random
import requests
from openai import OpenAI
from config import OPENAI_API_KEY

class FirearmGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url='https://api.openai.com/v1')
        
        # User agent for Wikipedia requests
        self.headers = {
            'User-Agent': 'FirearmBot/1.0 (Educational Twitter Bot)'
        }
        
        # Historical periods with appropriate firearm types
        self.period_types = {
            "Early Firearms Era (1400-1600)": ["hand cannon", "matchlock musket", "arquebus"],
            "Flintlock Era (1600-1840)": ["flintlock pistol", "flintlock musket", "blunderbuss"],
            "Percussion Era (1840-1870)": ["percussion rifle", "percussion pistol", "muzzle-loading rifle"],
            "American Civil War Era (1860s)": ["rifle musket", "revolver", "carbine", "rifle"],
            "Wild West Era (1870-1900)": ["revolver", "lever-action rifle", "single-action pistol", "shotgun"],
            "World War I (1914-1918)": ["bolt-action rifle", "semi-automatic pistol", "machine gun", "submachine gun"],
            "Interwar Period (1920-1939)": ["semi-automatic pistol", "submachine gun", "bolt-action rifle", "automatic rifle"],
            "World War II (1939-1945)": ["semi-automatic rifle", "submachine gun", "machine gun", "pistol", "bolt-action rifle"],
            "Cold War Era (1950-1990)": ["assault rifle", "battle rifle", "submachine gun", "pistol", "sniper rifle"],
            "Modern Era (1990-present)": ["assault rifle", "carbine", "pistol", "sniper rifle", "submachine gun"]
        }
    
    def generate_firearm_info(self):
        """Generate information about a historical firearm using OpenAI"""
        
        # Randomly select period and appropriate firearm type
        period = random.choice(list(self.period_types.keys()))
        firearm_type = random.choice(self.period_types[period])
        
        prompt = f"""Generate information about a specific, real historical {firearm_type} from the {period}.

IMPORTANT: Choose a REAL, historically documented firearm that actually existed during this period. Use the actual manufacturer name and model number.

Please provide:
1. The exact name/model of the firearm (e.g., "Colt Single Action Army", "M1 Garand", "Lee-Enfield No. 4 Mk I")
2. A brief 2-3 sentence description explaining why it was made, its historical significance, and its key features

Format your response as JSON with these exact keys:
{{
    "name": "exact firearm name with manufacturer and model",
    "description": "2-3 sentence description of why it was made and its significance"
}}

Examples of good responses:
- "Colt M1911" not just "pistol"
- "Winchester Model 1873" not just "lever-action rifle"
- "Mauser Gewehr 98" not just "bolt-action rifle"

Make sure the firearm is real, historically accurate, and actually existed during the specified period."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a firearms historian with expertise in historical weapons from all eras. You ONLY provide information about REAL, historically documented firearms with actual manufacturer names and model numbers. Never make up fictional firearms or suggest firearms that didn't exist in a given period."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            # Sometimes the model wraps JSON in markdown code blocks
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            firearm_data = json.loads(content)
            
            # Validate that we got actual data
            if not firearm_data.get('name') or firearm_data['name'].lower().startswith('none'):
                print("Got invalid firearm, retrying...")
                return self.generate_firearm_info()  # Retry
            
            return firearm_data
            
        except Exception as e:
            print(f"Error generating firearm info: {e}")
            return None
    
    def search_firearm_image(self, firearm_name):
        """Search for a real image of the firearm using Wikipedia"""
        
        print(f"Searching for images of: {firearm_name}")
        
        # Try direct Wikipedia page lookup
        image_url = self.get_wikipedia_image(firearm_name)
        if image_url:
            return image_url
        
        # Try searching Wikipedia
        image_url = self.search_wikipedia_pages(firearm_name)
        if image_url:
            return image_url
        
        # Try Wikimedia Commons
        image_url = self.search_wikimedia_commons(firearm_name)
        if image_url:
            return image_url
        
        print("⚠ Could not find image from Wikipedia/Wikimedia")
        print("  The bot will post text-only")
        return None
    
    def get_wikipedia_image(self, title):
        """Get image from a Wikipedia page by title"""
        try:
            wiki_api_url = "https://en.wikipedia.org/w/api.php"
            
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'pageimages',
                'format': 'json',
                'pithumbsize': 1024
            }
            
            response = requests.get(wiki_api_url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if page_id != '-1' and 'thumbnail' in page_data:
                    image_url = page_data['thumbnail']['source']
                    print(f"  ✓ Found Wikipedia image for: {page_data.get('title', title)}")
                    return image_url
            
            return None
            
        except Exception as e:
            print(f"  Error getting Wikipedia image: {e}")
            return None
    
    def search_wikipedia_pages(self, search_term):
        """Search Wikipedia and get image from first result"""
        try:
            wiki_api_url = "https://en.wikipedia.org/w/api.php"
            
            # Search for pages
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': search_term,
                'format': 'json',
                'srlimit': 3
            }
            
            response = requests.get(wiki_api_url, params=search_params, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            
            if not search_results:
                return None
            
            # Try each search result
            for result in search_results:
                page_title = result['title']
                print(f"  Trying: {page_title}")
                
                image_url = self.get_wikipedia_image(page_title)
                if image_url:
                    return image_url
            
            return None
            
        except Exception as e:
            print(f"  Error searching Wikipedia: {e}")
            return None
    
    def search_wikimedia_commons(self, firearm_name):
        """Search Wikimedia Commons for firearm images"""
        try:
            commons_api_url = "https://commons.wikimedia.org/w/api.php"
            
            # Search for images
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': firearm_name,
                'srnamespace': 6,  # File namespace
                'format': 'json',
                'srlimit': 5
            }
            
            response = requests.get(commons_api_url, params=search_params, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            
            if not search_results:
                return None
            
            # Try each result
            for result in search_results:
                file_title = result['title']
                
                # Get image URL
                image_params = {
                    'action': 'query',
                    'titles': file_title,
                    'prop': 'imageinfo',
                    'iiprop': 'url',
                    'format': 'json'
                }
                
                response = requests.get(commons_api_url, params=image_params, headers=self.headers, timeout=15)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                
                for page_id, page_data in pages.items():
                    if 'imageinfo' in page_data and page_data['imageinfo']:
                        image_url = page_data['imageinfo'][0]['url']
                        print(f"  ✓ Found Wikimedia Commons image")
                        return image_url
            
            return None
            
        except Exception as e:
            print(f"  Error searching Wikimedia Commons: {e}")
            return None

if __name__ == "__main__":
    # Test the generator
    generator = FirearmGenerator()
    
    print("Testing firearm generation with real images...\n")
    print("=" * 60)
    
    # Test a few times
    for i in range(3):
        print(f"\nTest {i+1}:")
        print("-" * 60)
        
        firearm_info = generator.generate_firearm_info()
        
        if firearm_info:
            print(f"Name: {firearm_info['name']}")
            print(f"Description: {firearm_info['description'][:100]}...")
            print()
            
            image_url = generator.search_firearm_image(firearm_info['name'])
            
            if image_url:
                print(f"✓ Image: {image_url[:80]}...")
            else:
                print("✗ No image found")
        else:
            print("✗ Failed to generate firearm info")
        
        print()
