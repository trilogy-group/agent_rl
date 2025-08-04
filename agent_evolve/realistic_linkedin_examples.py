#!/usr/bin/env python3
"""
Examples of realistic LinkedIn posts for training data generation
"""

realistic_linkedin_posts = [
    {
        "category": "Product Launch",
        "content": """🚀 Exciting news! After 18 months of development, we're officially launching our new AI-powered analytics platform at TechFlow Solutions.

The journey hasn't been easy. Our team of 12 engineers worked tirelessly, conducting over 200 user interviews and processing 50TB of data to understand what businesses really need from their analytics tools.

Key highlights of our platform:
✅ 300% faster data processing than industry standards
✅ Real-time insights across 15+ data sources
✅ Intuitive drag-and-drop dashboard builder
✅ Enterprise-grade security with SOC 2 compliance

Special thanks to our beta customers who provided invaluable feedback: @Microsoft @Salesforce @HubSpot - your insights shaped every feature.

We're offering early access to the first 100 companies who sign up this month. Interested in revolutionizing your data strategy?

👇 Drop a comment or DM me directly
🔗 Learn more: techflow.com/analytics-platform

#Analytics #AI #ProductLaunch #DataScience #TechInnovation #Startup #B2B #SaaS""",
        "description": "Comprehensive product launch with story, metrics, social proof, and clear CTA"
    },
    
    {
        "category": "Personal Achievement", 
        "content": """🎯 One year ago today, I made the scary decision to leave my corporate job at Goldman Sachs to start my own fintech consultancy.

The stats:
📈 Year 1 revenue: $350K
👥 Team grown from 1 to 5 people
🏢 Worked with 23 companies across 8 countries
📚 Published 12 industry reports that were cited 200+ times

But behind these numbers is a story of:
• 60-hour weeks for the first 6 months
• Countless rejections and "nos"
• Imposter syndrome that kept me up at night
• Amazing mentors who believed in me when I didn't believe in myself

To everyone considering the entrepreneurial leap: it's terrifying, exhausting, and absolutely worth it. The freedom to choose your clients, solve problems you're passionate about, and build something from scratch is unmatched.

Huge gratitude to my clients who took a chance on a new consultancy, my family who supported late-night calls across time zones, and my network who referred business when I had zero track record.

What's next? We're launching our first fintech accelerator program in Q2 2024. More details coming soon!

To anyone thinking about making a big career change: your future self is counting on your current courage. 💪

#Entrepreneurship #Fintech #CareerChange #Consulting #StartupLife #Finance #Success""",
        "description": "Personal journey with specific metrics, vulnerability, and inspirational messaging"
    },

    {
        "category": "Industry Insights",
        "content": """🤖 Just finished analyzing 2,000+ job postings from the past 6 months. The AI job market is shifting in ways that might surprise you.

Here's what the data reveals:

📊 SURPRISING TRENDS:
• "Prompt Engineering" jobs increased 1,200% since January
• AI Ethics roles grew 340% (finally!)  
• Traditional "AI Researcher" positions dropped 15%
• Hybrid roles (AI + Domain Expertise) up 280%

💰 SALARY INSIGHTS:
• Average AI salary: $142K (up 18% from last year)
• Prompt Engineers: $95K - $160K range
• AI Product Managers: $135K - $200K
• ML Engineers still commanding highest premiums: $150K - $250K

🎯 SKILLS IN DEMAND:
1. LangChain & vector databases (mentioned in 67% of posts)
2. Fine-tuning & model optimization (52%)
3. AI safety & alignment (43% - huge jump!)
4. Multimodal AI applications (38%)
5. Edge AI deployment (31%)

🔮 MY PREDICTION:
The next wave isn't about building better models - it's about building better AI products. Companies need people who understand both technology AND business problems.

If you're pivoting into AI:
→ Focus on applied skills, not just theory
→ Build a portfolio of real projects
→ Learn one domain deeply (healthcare, finance, etc.)
→ Understand the ethical implications

The AI gold rush is real, but like any gold rush, the people selling shovels (tools, education, integration) often do better than the miners.

What trends are you seeing in your network? Drop your observations below! 👇

Full analysis with charts and methodology: linkedin.com/pulse/ai-jobs-2024

#AI #Jobs #CareerAdvice #MachineLearning #TechTrends #DataScience #FutureOfWork""",
        "description": "Data-driven industry analysis with specific metrics, predictions, and engagement"
    }
]

print("=== REALISTIC LINKEDIN POST EXAMPLES ===")
for i, post in enumerate(realistic_linkedin_posts, 1):
    print(f"\n{i}. {post['category']} ({len(post['content'])} characters)")
    print(f"Description: {post['description']}")
    print(f"Word count: {len(post['content'].split())} words")
    print("---")

print("\n=== KEY CHARACTERISTICS OF REALISTIC POSTS ===")
print("✅ 200-400 words (much longer than current training data)")
print("✅ Multiple paragraphs with clear structure")  
print("✅ Specific metrics, numbers, and data points")
print("✅ Personal stories and vulnerability")
print("✅ Professional emojis and formatting")
print("✅ Multiple relevant hashtags")
print("✅ Clear calls-to-action")
print("✅ Industry-specific terminology")
print("✅ Social proof and credibility markers")