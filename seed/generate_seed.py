"""
Generate seed data for demo purposes
"""
import json
import random
from datetime import datetime, timedelta

# Sample creator names (popular marketing/business influencers)
CREATOR_NAMES = [
    "Alex Hormozi", "Adrian Morrison", "Dan Lok", "Iman Gadzhi",
    "Grant Cardone", "Tai Lopez", "Gary Vaynerchuk", "Russell Brunson",
    "Frank Kern", "Ryan Deiss", "Neil Patel", "Amy Porterfield",
    "Pat Flynn", "John Lee Dumas", "Lewis Howes", "Jasmine Star",
    "Marie Forleo", "Ramit Sethi", "Tim Ferriss", "Tony Robbins",
    # Add more names to reach 300
    "Rachel Hollis", "Brendon Burchard", "Dean Graziosi", "Jeff Walker",
    "Darren Hardy", "Brian Tracy", "Zig Ziglar", "Jim Rohn",
    "Eric Worre", "Ray Higdon", "Rob Fore", "Julie Solomon",
    "Jenna Kutcher", "Glennon Doyle", "Mel Robbins", "Gabby Bernstein",
]

# Extend to 300 creators
for i in range(len(CREATOR_NAMES), 300):
    CREATOR_NAMES.append(f"Creator {i+1}")

# Sample ad titles and descriptions
AD_TEMPLATES = {
    "VSL": {
        "titles": [
            "How I Built a $10M Business in 12 Months",
            "The Secret Formula to Scaling Your Business",
            "Watch This Free Training to Transform Your Life",
            "Discover the #1 Mistake Holding You Back",
            "The Proven System to Generate Passive Income",
        ],
        "descriptions": [
            "Join this free webinar to learn the exact strategy I used to scale from $0 to $10M. Limited spots available!",
            "In this video sales letter, I reveal the framework that helped thousands achieve financial freedom.",
            "Watch this 60-minute training and learn how to build a sustainable online business from scratch.",
        ],
        "tags": ["VSL", "Lead Generation", "Webinar"]
    },
    "Ecom": {
        "titles": [
            "Build Your Dream Store in 30 Minutes",
            "Shopify Success: From Zero to $100K/Month",
            "Dropshipping Made Easy - Start Today",
            "The Complete E-commerce Blueprint",
            "Amazon FBA Secrets Revealed",
        ],
        "descriptions": [
            "Learn how to create a profitable Shopify store with our proven system. No experience needed!",
            "Discover the exact products and strategies that generated $2M in revenue last year.",
            "Get started with dropshipping today with our step-by-step guide and supplier list.",
        ],
        "tags": ["Ecom", "Lead Generation", "Case Study"]
    },
    "Coaching": {
        "titles": [
            "Transform Your Life with 1-on-1 Coaching",
            "Breakthrough Your Limits - Free Consultation",
            "The Coaching Program That Changed Everything",
            "Unlock Your Full Potential Today",
            "Join Our Elite Mastermind Group",
        ],
        "descriptions": [
            "Work directly with me to achieve your goals. Book your free discovery call now.",
            "Limited spots available for my 90-day transformation program. Apply today!",
            "Join hundreds of successful students in our exclusive coaching community.",
        ],
        "tags": ["Coaching", "Mentorship", "Lead Generation"]
    },
    "SaaS": {
        "titles": [
            "The All-in-One Marketing Platform",
            "Automate Your Business with AI",
            "CRM That Actually Works - Try Free",
            "Scale Your Agency with Our Software",
            "The Tool That 10,000+ Businesses Use",
        ],
        "descriptions": [
            "Start your 14-day free trial and see why we're the #1 choice for entrepreneurs.",
            "Our platform helps you save 20+ hours per week on repetitive tasks. Get started today!",
            "Join thousands of businesses that switched to our all-in-one solution.",
        ],
        "tags": ["SaaS", "Lead Generation"]
    },
    "UGC": {
        "titles": [
            "Real Results from Real People",
            "See What Our Customers Are Saying",
            "This Changed My Life - Customer Story",
            "From Struggling to Thriving in 90 Days",
            "My Honest Review After 6 Months",
        ],
        "descriptions": [
            "Watch Sarah share how she went from $5K/month to $50K/month using our system.",
            "Real testimonial from a real customer. No actors, no scripts.",
            "John quit his 9-5 after just 3 months. Here's his story.",
        ],
        "tags": ["UGC", "Case Study", "Talking-Head"]
    },
}

PLATFORMS = ["meta", "tiktok", "youtube"]


def generate_creators():
    """Generate creator data"""
    creators = []

    for i, name in enumerate(CREATOR_NAMES):
        creators.append({
            "name": name,
            "source_handle": name.lower().replace(" ", "_"),
            "avatar_url": f"https://i.pravatar.cc/150?u={i}",
            "bio": f"Entrepreneur, business coach, and marketing expert helping you scale your business."
        })

    return creators


def generate_ads(creators):
    """Generate ad data"""
    ads = []

    # Generate 20-30 ads per creator (aiming for 6000+ ads)
    for creator in creators:
        num_ads = random.randint(15, 25)

        for _ in range(num_ads):
            # Choose random category
            category = random.choice(list(AD_TEMPLATES.keys()))
            template = AD_TEMPLATES[category]

            # Random platform
            platform = random.choice(PLATFORMS)

            # Random dates (last 6 months)
            days_ago = random.randint(1, 180)
            started_at = (datetime.utcnow() - timedelta(days=days_ago)).isoformat() + "Z"

            # Build ad
            ad = {
                "creator_name": creator["name"],
                "platform": platform,
                "title": random.choice(template["titles"]),
                "description": random.choice(template["descriptions"]),
                "started_at": started_at,
                "duration_seconds": random.randint(30, 600) if random.random() > 0.3 else None,
                "engagement_count": random.randint(100, 50000),
                "external_url": f"https://{platform}.com/ads/{random.randint(100000, 999999)}",
                "funnel_url": f"https://example.com/funnel-{random.randint(1, 100)}",
                "thumb_url": f"https://picsum.photos/400/300?random={random.randint(1, 10000)}",
                "is_active": random.random() > 0.3,  # 70% active
                "tags": template["tags"]
            }

            ads.append(ad)

    return ads


def main():
    """Generate and save seed data"""
    print("Generating creators...")
    creators = generate_creators()
    print(f"Generated {len(creators)} creators")

    print("Generating ads...")
    ads = generate_ads(creators)
    print(f"Generated {len(ads)} ads")

    # Save to JSON
    seed_data = {
        "creators": creators,
        "ads": ads
    }

    with open("seed/seed_data.json", "w") as f:
        json.dump(seed_data, f, indent=2)

    print(f"Seed data saved to seed/seed_data.json")
    print(f"Total: {len(creators)} creators, {len(ads)} ads")


if __name__ == "__main__":
    main()
