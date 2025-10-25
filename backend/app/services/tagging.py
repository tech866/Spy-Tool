"""
AI tagging service with heuristics and optional LLM
"""
import re
import structlog
from typing import Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from ..core.config import settings

logger = structlog.get_logger()

# Allow-listed tags
ALLOWED_TAGS = [
    "VSL",
    "UGC",
    "Talking-Head",
    "Lead Generation",
    "Bizop",
    "Ecom",
    "SaaS",
    "Coaching",
    "Publishing",
    "Mentorship",
    "Webinar",
    "Case Study"
]


class TaggingService:
    """
    AI tagging service combining heuristic rules with optional LLM
    """

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None

        if settings.AI_TAGGING_ENABLED:
            if settings.OPENAI_API_KEY:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            elif settings.ANTHROPIC_API_KEY:
                self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def suggest_tags(
        self,
        title: Optional[str],
        description: Optional[str],
        platform: str
    ) -> list[str]:
        """
        Suggest tags for an ad using heuristics and optional LLM

        Args:
            title: Ad title
            description: Ad description
            platform: Platform name (meta, tiktok, youtube)

        Returns:
            List of suggested tag names
        """
        # Combine text
        text = f"{title or ''} {description or ''}".lower()

        # Start with heuristic tags
        heuristic_tags = self._heuristic_tags(text)

        # If LLM is enabled, get additional suggestions
        if settings.AI_TAGGING_ENABLED and (self.openai_client or self.anthropic_client):
            try:
                llm_tags = await self._llm_tags(title, description, platform)
                # Combine and deduplicate
                all_tags = list(set(heuristic_tags + llm_tags))
                logger.info("tags_suggested", heuristic=heuristic_tags, llm=llm_tags, final=all_tags)
                return all_tags
            except Exception as e:
                logger.error("llm_tagging_failed", error=str(e))
                # Fall back to heuristics only
                return heuristic_tags

        return heuristic_tags

    def _heuristic_tags(self, text: str) -> list[str]:
        """
        Apply heuristic rules to suggest tags

        Args:
            text: Combined title + description in lowercase

        Returns:
            List of tag names
        """
        tags = []

        # VSL patterns
        if re.search(r'(video sales|vsl|webinar|watch.*video|free training)', text):
            tags.append("VSL")

        # UGC patterns
        if re.search(r'(ugc|user generated|real people|testimonial|review)', text):
            tags.append("UGC")

        # Talking-Head patterns
        if re.search(r'(talking head|direct to camera|speaking|message from)', text):
            tags.append("Talking-Head")

        # Lead Generation patterns
        if re.search(r'(lead|funnel|demo|free consultation|book a call|schedule|signup|register)', text):
            tags.append("Lead Generation")

        # Bizop patterns
        if re.search(r'(business opportunity|make money|side hustle|financial freedom|income)', text):
            tags.append("Bizop")

        # Ecom patterns
        if re.search(r'(shopify|ecommerce|e-commerce|store|dropship|product|shop now|buy now)', text):
            tags.append("Ecom")

        # SaaS patterns
        if re.search(r'(saas|software|platform|tool|app|automation|subscription)', text):
            tags.append("SaaS")

        # Coaching patterns
        if re.search(r'(coach|coaching|mentor|training|course|program|mastermind)', text):
            tags.append("Coaching")

        # Publishing patterns
        if re.search(r'(book|ebook|guide|publish|author|kindle)', text):
            tags.append("Publishing")

        # Mentorship patterns
        if re.search(r'(mentorship|mentor|1-on-1|one on one|guidance)', text):
            tags.append("Mentorship")

        # Webinar patterns
        if re.search(r'(webinar|live training|masterclass|workshop|seminar)', text):
            tags.append("Webinar")

        # Case Study patterns
        if re.search(r'(case study|success story|how.*made|how.*built|results)', text):
            tags.append("Case Study")

        return tags

    async def _llm_tags(
        self,
        title: Optional[str],
        description: Optional[str],
        platform: str
    ) -> list[str]:
        """
        Use LLM to suggest additional tags

        Args:
            title: Ad title
            description: Ad description
            platform: Platform name

        Returns:
            List of tag names with confidence >= 0.5
        """
        prompt = f"""Analyze this ad and suggest relevant tags from the following allow-list:
{', '.join(ALLOWED_TAGS)}

Platform: {platform}
Title: {title or 'N/A'}
Description: {description or 'N/A'}

Return only the most relevant tags (2-3 maximum) as a comma-separated list.
Only use tags from the allow-list above."""

        if self.openai_client:
            response = await self.openai_client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing advertising content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            result = response.choices[0].message.content.strip()
        elif self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model=settings.AI_MODEL,
                max_tokens=50,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            result = response.content[0].text.strip()
        else:
            return []

        # Parse comma-separated tags
        suggested = [tag.strip() for tag in result.split(',')]

        # Filter to only allowed tags
        valid_tags = [tag for tag in suggested if tag in ALLOWED_TAGS]

        return valid_tags
