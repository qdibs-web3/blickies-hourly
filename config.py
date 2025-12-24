import os

# Twitter API Credentials
# When running on GitHub Actions, these will be loaded from GitHub Secrets
# When running locally, replace the empty strings with your actual API keys
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET', '')
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN', '')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '')

# OpenAI API Credentials
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Instructions:
# 1. For GitHub Actions: Add all keys as GitHub Secrets (see GITHUB_SETUP.md)
# 2. For local testing: Replace empty strings above with your actual API keys
#    Example: TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY', 'your_actual_key_here')
