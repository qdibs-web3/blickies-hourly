import tweepy
import requests
from io import BytesIO
from PIL import Image
import os

try:
    from config import (
        TWITTER_API_KEY, 
        TWITTER_API_SECRET, 
        TWITTER_BEARER_TOKEN,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )
    HAS_ACCESS_TOKENS = True
except ImportError:
    from config import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_BEARER_TOKEN
    HAS_ACCESS_TOKENS = False
    TWITTER_ACCESS_TOKEN = None
    TWITTER_ACCESS_TOKEN_SECRET = None

class TwitterPoster:
    def __init__(self):
        """Initialize Twitter API client"""
        
        if not HAS_ACCESS_TOKENS:
            print("WARNING: Access tokens not found in config.py")
            print("Run 'python3.11 setup_auth.py' to set up authentication")
            print("Bot will run in limited mode (text-only tweets)")
        
        # Set up API v2 client for posting tweets
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        # Set up API v1.1 for media upload (if we have access tokens)
        if HAS_ACCESS_TOKENS and TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET:
            auth = tweepy.OAuth1UserHandler(
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_TOKEN_SECRET
            )
            self.api_v1 = tweepy.API(auth)
        else:
            self.api_v1 = None
        
    def download_image(self, image_url, save_path=None):
        """Download image from URL and optionally save to disk"""
        try:
            print(f"Downloading image from: {image_url}")
            headers = {'User-Agent': 'FirearmBot/1.0 (Educational Twitter Bot)'}
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Load image with PIL to ensure it's valid
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to file if path provided
            if save_path:
                img.save(save_path, format='JPEG', quality=95)
                print(f"Image saved to: {save_path}")
                return save_path
            
            # Otherwise return as bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            return img_bytes
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def post_firearm(self, firearm_name, description, image_url):
        """Post a firearm to Twitter with image"""
        
        try:
            # Create the tweet text
            tweet_text = f"{firearm_name}\n\n{description}\n\n#Firearms #History #Guns #MilitaryHistory"
            
            # Ensure tweet is within character limit (280 characters)
            if len(tweet_text) > 280:
                # Truncate description if needed
                max_desc_length = 280 - len(firearm_name) - len("\n\n\n\n#Firearms #History #Guns #MilitaryHistory") - 3
                description = description[:max_desc_length] + "..."
                tweet_text = f"{firearm_name}\n\n{description}\n\n#Firearms #History #Guns #MilitaryHistory"
            
            print(f"\nTweet text ({len(tweet_text)} chars):\n{tweet_text}\n")
            
            media_id = None
            
            # Try to upload media if we have API v1.1 access
            if self.api_v1 and image_url:
                try:
                    # Download image to temporary file
                    temp_image_path = "/tmp/firearm_temp.jpg"
                    image_path = self.download_image(image_url, save_path=temp_image_path)
                    
                    if image_path:
                        print("Uploading media to Twitter...")
                        media = self.api_v1.media_upload(filename=image_path)
                        media_id = media.media_id
                        print(f"Media uploaded successfully! Media ID: {media_id}")
                        
                        # Clean up temp file
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
                    
                except Exception as e:
                    print(f"Error uploading media: {e}")
                    print("Posting text-only tweet instead...")
            
            # Post tweet
            if media_id:
                response = self.client.create_tweet(text=tweet_text, media_ids=[media_id])
                print(f"✓ Tweet with image posted successfully! Tweet ID: {response.data['id']}")
            else:
                response = self.client.create_tweet(text=tweet_text)
                print(f"✓ Text-only tweet posted successfully! Tweet ID: {response.data['id']}")
            
            return response.data['id']
            
        except tweepy.TweepyException as e:
            print(f"✗ Error posting to Twitter: {e}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return None

if __name__ == "__main__":
    # Test the poster
    poster = TwitterPoster()
    
    # Test with sample data
    test_name = "M1 Garand"
    test_desc = "The M1 Garand was the first standard-issue semi-automatic rifle for the US military. It gave American soldiers a significant firepower advantage in WWII."
    test_image = "https://upload.wikimedia.org/wikipedia/commons/0/0e/M1_Garand_rifle_-_USA_-_30-06_-_Arm%C3%A9museum.jpg"
    
    print("Testing Twitter poster...")
    poster.post_firearm(test_name, test_desc, test_image)