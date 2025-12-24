#!/usr/bin/env python3.11
"""
Historical Firearms Twitter Bot

Posts information about historical firearms once per hour with:
- Firearm name/model
- Historical description and significance
- AI-generated image of the firearm

Author: Firearm History Bot
"""

import time
import schedule
import logging
from datetime import datetime
from firearm_generator import FirearmGenerator
from twitter_poster import TwitterPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/firearm-bot/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FirearmBot:
    def __init__(self):
        """Initialize the bot"""
        logger.info("Initializing Firearm Bot...")
        self.generator = FirearmGenerator()
        self.poster = TwitterPoster()
        logger.info("Bot initialized successfully!")
    
    def post_firearm(self):
        """Generate and post a firearm"""
        try:
            logger.info("=" * 60)
            logger.info(f"Starting new post at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # Generate firearm information
            logger.info("Generating firearm information...")
            firearm_info = self.generator.generate_firearm_info()
            
            if not firearm_info:
                logger.error("Failed to generate firearm information")
                return False
            
            logger.info(f"Generated: {firearm_info['name']}")
            logger.info(f"Description: {firearm_info['description']}")
            
            # Search for firearm image
            logger.info("Searching for firearm image...")
            image_url = self.generator.search_firearm_image(firearm_info['name'])
            
            if not image_url:
                logger.error("Failed to generate firearm image")
                return False
            
            logger.info(f"Image generated: {image_url}")
            
            # Post to Twitter
            logger.info("Posting to Twitter...")
            tweet_id = self.poster.post_firearm(
                firearm_info['name'],
                firearm_info['description'],
                image_url
            )
            
            if tweet_id:
                logger.info(f"✓ Successfully posted! Tweet ID: {tweet_id}")
                logger.info(f"View at: https://twitter.com/i/web/status/{tweet_id}")
                return True
            else:
                logger.error("Failed to post to Twitter")
                return False
                
        except Exception as e:
            logger.error(f"Error in post_firearm: {e}", exc_info=True)
            return False
    
    def run(self):
        """Run the bot with hourly scheduling"""
        logger.info("Starting Firearm Bot...")
        logger.info("Bot will post once per hour, every hour")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        # Post immediately on startup
        logger.info("Posting initial firearm...")
        self.post_firearm()
        
        # Schedule hourly posts
        schedule.every().hour.do(self.post_firearm)
        
        # Keep the bot running
        logger.info("\nBot is now running. Waiting for next scheduled post...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)

def main():
    """Main entry point"""
    bot = FirearmBot()
    bot.run()

if __name__ == "__main__":
    main()
