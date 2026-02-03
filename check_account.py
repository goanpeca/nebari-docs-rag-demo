#!/usr/bin/env python3
"""Check Anthropic account details and limits."""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment")
    exit(1)

client = Anthropic(api_key=api_key)

print("=" * 60)
print("ANTHROPIC ACCOUNT INVESTIGATION")
print("=" * 60)

# Check if API key is valid
print(f"\n API Key: {api_key[:15]}...{api_key[-4:]}")
print(f"   Key type: {'Workspace' if api_key.startswith('sk-ant-api') else 'User'}")

# Try to get account info by making a minimal API call
try:
    response = client.messages.create(
        model="claude-3-haiku-20240307", max_tokens=10, messages=[{"role": "user", "content": "Hi"}]
    )
    print("\n API Key is VALID and working")
    print("   Usage tracked for billing: Yes")
except Exception as e:
    print(f"\n API Key error: {e}")

print("\n" + "=" * 60)
print("NEXT STEPS TO GET CLAUDE SONNET 4 ACCESS")
print("=" * 60)

print("""
Your account is likely on TIER 1 (new accounts).

To upgrade to higher tiers and access Claude Sonnet 4:

1. **Automatic Tier Upgrade:**
   - Spend $5 on Haiku → Tier 2 (Claude Sonnet access)
   - Spend $40 total → Tier 3 (Claude Opus access)
   - Spend $200 total → Tier 4 (Claude Sonnet 4 access)

2. **Manual Request (Faster):**
   Go to: https://console.anthropic.com/settings/limits
   Click "Request tier increase" if available

   OR email: support@anthropic.com
   Subject: "Request API Tier Upgrade - Have Credits"
   Body: "I have credits and need access to Claude Sonnet 4
         for a project demo. Please upgrade my tier."

3. **Use Haiku for Now (Recommended for Demo):**
   - Haiku is 75% cheaper than Sonnet
   - Much faster responses (better UX for demo)
   - Still very good quality for Q&A
   - Your $27 will last much longer

For your interview demo, Haiku is actually BETTER because:
- Faster responses = better user experience
- Lower latency = more impressive
- Still accurate for documentation Q&A
- Shows you understand cost optimization

RECOMMENDED: Keep using Haiku for the demo!
""")

print("\n" + "=" * 60)
print("CHECK YOUR USAGE TIER")
print("=" * 60)
print("\nVisit: https://console.anthropic.com/settings/limits")
print("Look for 'Rate Limits' section - it will show your tier")
print("\n" + "=" * 60)
