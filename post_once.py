#!/usr/bin/env python3
"""
Single Post Script for GitHub Actions

This script posts one firearm to Twitter and then exits.
Designed to be run by GitHub Actions on a schedule.
"""

import os
import sys
import logging
from datetime import datetime
from firearm_generator import FirearmGenerator
from twitter_poster import TwitterPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('post.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def post_firearm():
    """Generate and post a single firearm"""
    try:
        logger.info("=" * 60)
        logger.info(f"Starting post at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info("=" * 60)
        
        # Initialize components
        logger.info("Initializing bot components...")
        generator = FirearmGenerator()
        poster = TwitterPoster()
        
        # Generate firearm information
        logger.info("Generating firearm information...")
        firearm_info = generator.generate_firearm_info()
        
        if not firearm_info:
            logger.error("Failed to generate firearm information")
            return False
        
        logger.info(f"Generated: {firearm_info['name']}")
        logger.info(f"Description: {firearm_info['description'][:100]}...")
        
        # Search for firearm image
        logger.info("Searching for firearm image...")
        image_url = generator.search_firearm_image(firearm_info['name'])
        
        if not image_url:
            logger.warning("No image found, will post text-only")
        else:
            logger.info(f"Image found: {image_url[:80]}...")
        
        # Post to Twitter
        logger.info("Posting to Twitter...")
        tweet_id = poster.post_firearm(
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

def main():
    """Main entry point"""
    logger.info("Historical Firearms Bot - Single Post Mode")
    logger.info("Running on GitHub Actions")
    logger.info("")
    
    success = post_firearm()
    
    if success:
        logger.info("\n✓ Post completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n✗ Post failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
