"""
Professionalism & Vulgarity Moderation Bot
Soft moderation for community chats - nudges, not bans
"""

from typing import Tuple, List
import re


class ProfessionalismBot:
    """
    Lightweight moderation for community chats
    
    Philosophy:
    - Soft nudges, not punitive action
    - Educational, not authoritarian
    - Preserve student voice while maintaining respect
    """
    
    def __init__(self):
        # Profanity and vulgarity
        self.vulgarity_list = [
            'fuck', 'fucking', 'shit', 'damn', 'bitch', 'asshole', 'bastard',
            'crap', 'piss', 'dick', 'cock', 'pussy','nigga'
        ]
        
        # Personal attacks and harassment
        self.attack_patterns = [
            'you\'re stupid', 'you\'re an idiot', 'you\'re dumb',
            'shut up', 'nobody cares', 'kill yourself',
            'you suck', 'loser', 'pathetic'
        ]
        
        # Discriminatory language
        self.discriminatory_patterns = [
            # Slurs (partial list for demo - expand for production)
            'retard', 'retarded', 'autistic' # when used pejoratively
        ]
        
        # Crisis/self-harm language (for flagging, not blocking)
        self.crisis_keywords = [
            'want to die', 'kill myself', 'suicide', 'end it all',
            'self harm', 'hurt myself', 'no point living'
        ]
    
        # Pronouns/markers used to detect targeted insults
        self.second_person_markers = [r"you", r"you're", r"youre", r"u"]

    def check_message(self, message: str) -> Tuple[bool, str]:
        """
        Check message for inappropriate content
        
        Returns:
            (is_appropriate, processed_message)
            - is_appropriate: False if message should be blocked/moderated
            - processed_message: Original or modified message
        """
        message_lower = message.lower()
        
        # Check for crisis keywords (flag but don't block)
        crisis_detected = self._contains_crisis_language(message_lower)
        if crisis_detected:
            # Don't block, but flag for counselor attention
            # This is handled at a higher level
            pass
        
        # Check for discriminatory language (block)
        if self._contains_discriminatory_language(message_lower):
            return False, "Message contained discriminatory language"
        
        # Check for personal attacks (block)
        if self._contains_personal_attack(message_lower):
            return False, "Message contained personal attack or harassment"
        
        # Check for excessive vulgarity (soft filter)
        vulgarity_count = self._count_vulgarity(message_lower)
        if vulgarity_count > 2:
            # Excessive profanity
            return False, "Message contained excessive profanity"
        elif vulgarity_count > 0:
            # Light profanity - allow but could add warning
            # For now, we allow it
            pass
        
        # Message is appropriate
        return True, message
    
    def _contains_crisis_language(self, message_lower: str) -> bool:
        """Check for crisis/self-harm keywords"""
        return any(keyword in message_lower for keyword in self.crisis_keywords)
    
    def _contains_discriminatory_language(self, message_lower: str) -> bool:
        """Check for discriminatory language"""
        # Simple substring matching (expand with regex for production)
        for pattern in self.discriminatory_patterns:
            if pattern in message_lower:
                # Additional context check could go here
                # For demo, simple matching
                return True
        return False
    
    def _contains_personal_attack(self, message_lower: str) -> bool:
        """Check for personal attacks or harassment"""
        # Direct pattern matches (explicit phrases)
        for pattern in self.attack_patterns:
            if pattern in message_lower:
                return True

        # Targeted insults using vulgar words (e.g., "you are a bastard")
        # If a vulgarity appears close to a second-person marker, treat as attack
            for vulgar in self.vulgarity_list:
                # Simple, robust patterns: up to ~5 words between pronoun and insult
                pronouns = r"(?:you|you're|youre|u)"
                pattern1 = r"\b" + pronouns + r"\b(?:\s+\w+){0,5}\s+\b" + re.escape(vulgar) + r"\b"
                pattern2 = r"\b" + re.escape(vulgar) + r"\b(?:\s+\w+){0,5}\s+\b" + pronouns + r"\b"
                if re.search(pattern1, message_lower) or re.search(pattern2, message_lower):
                    return True

        return False
    
    def _count_vulgarity(self, message_lower: str) -> int:
        """Count instances of vulgar language"""
        count = 0
        for word in self.vulgarity_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.findall(pattern, message_lower)
            count += len(matches)
        return count
    
    def generate_warning_message(self, message: str) -> str:
        """
        Generate a gentle warning message for user
        Educational tone, not punitive
        """
        message_lower = message.lower()
        
        if self._contains_personal_attack(message_lower):
            return ("Your message appears to contain a personal attack. "
                   "This community is for peer support. Please rephrase respectfully.")
        
        if self._contains_discriminatory_language(message_lower):
            return ("Your message contained language that may be hurtful to others. "
                   "Please use inclusive and respectful language.")
        
        vulgarity_count = self._count_vulgarity(message_lower)
        if vulgarity_count > 2:
            return ("Your message contained excessive profanity. "
                   "Please rephrase to maintain a supportive environment.")
        
        return "Please rephrase your message to maintain a respectful tone."


# Global moderation bot instance
professionalism_bot = ProfessionalismBot()


def check_message(message: str) -> Tuple[bool, str]:
    """
    Convenience function for message checking
    Returns (is_appropriate, processed_message)
    """
    return professionalism_bot.check_message(message)


def generate_warning(message: str) -> str:
    """Generate warning message for inappropriate content"""
    return professionalism_bot.generate_warning_message(message)