import re
from typing import List, Dict, Tuple
from .domain_keywords import DOMAIN_KEYWORDS
from ..models import Exam, Domain


class DomainSuggester:
    """
    Suggests appropriate domains for questions based on content analysis.
    """
    
    # Weight multipliers for different keyword categories
    WEIGHT_MULTIPLIERS = {
        'high_weight': 3.0,
        'medium_weight': 2.0,
        'low_weight': 1.0
    }
    
    def __init__(self):
        self.keyword_cache = {}
    
    def suggest_domains(self, question_text: str, exam_name: str, top_n: int = 3) -> List[Dict]:
        """
        Analyze question text and suggest appropriate domains.
        
        Args:
            question_text: The question text to analyze
            exam_name: The exam identifier (e.g., 'google_cloud_developer')
            top_n: Number of top suggestions to return
            
        Returns:
            List of domain suggestions with scores and confidence levels
        """
        if not question_text or not exam_name:
            return []
        
        # Get exam's domains and keywords
        exam_keywords = DOMAIN_KEYWORDS.get(exam_name, {})
        if not exam_keywords:
            return []
        
        # Analyze text and score domains
        domain_scores = self._analyze_question_text(question_text, exam_keywords)
        
        # Sort by score and get top suggestions
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Convert to suggestion format
        suggestions = []
        max_score = sorted_domains[0][1] if sorted_domains else 0
        
        for domain_name, score in sorted_domains[:top_n]:
            if score > 0:  # Only include domains with positive scores
                confidence = self._calculate_confidence(score, max_score)
                suggestions.append({
                    'domain_name': domain_name,
                    'score': round(score, 2),
                    'confidence': round(confidence, 1),
                    'confidence_level': self._get_confidence_level(confidence)
                })
        
        return suggestions
    
    def _analyze_question_text(self, text: str, exam_keywords: Dict) -> Dict[str, float]:
        """
        Analyze question text and calculate scores for each domain.
        """
        # Normalize text for analysis
        normalized_text = self._normalize_text(text)
        
        domain_scores = {}
        
        for domain_name, keyword_categories in exam_keywords.items():
            total_score = 0.0
            
            for category, keywords in keyword_categories.items():
                if category in self.WEIGHT_MULTIPLIERS:
                    category_score = self._score_keywords(normalized_text, keywords)
                    weighted_score = category_score * self.WEIGHT_MULTIPLIERS[category]
                    total_score += weighted_score
            
            domain_scores[domain_name] = total_score
        
        return domain_scores
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for keyword matching.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and common punctuation
        text = re.sub(r'[^\w\s\-\./]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _score_keywords(self, text: str, keywords: List[str]) -> float:
        """
        Score how well keywords match in the text.
        """
        score = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Exact phrase match (higher score)
            if keyword_lower in text:
                # Count occurrences
                occurrences = text.count(keyword_lower)
                
                # Bonus for exact phrase match
                phrase_bonus = 1.5 if ' ' in keyword_lower else 1.0
                
                # Score based on keyword length (longer keywords are more specific)
                length_bonus = len(keyword_lower.split()) * 0.3
                
                score += (occurrences * phrase_bonus * (1 + length_bonus))
            
            # Partial word matches (lower score)
            else:
                words = keyword_lower.split()
                if len(words) > 1:
                    # Check if most words from the keyword appear in text
                    matching_words = sum(1 for word in words if word in text)
                    if matching_words >= len(words) * 0.6:  # 60% of words match
                        score += matching_words * 0.3
        
        return score
    
    def _calculate_confidence(self, score: float, max_score: float) -> float:
        """
        Calculate confidence percentage based on score relative to max score.
        """
        if max_score == 0:
            return 0.0
        
        # Base confidence on relative score
        relative_score = (score / max_score) * 100
        
        # Apply confidence curve (sigmoid-like)
        if relative_score >= 80:
            confidence = 85 + (relative_score - 80) * 0.5  # 85-95%
        elif relative_score >= 60:
            confidence = 70 + (relative_score - 60) * 0.75   # 70-85%
        elif relative_score >= 40:
            confidence = 50 + (relative_score - 40) * 1.0   # 50-70%
        elif relative_score >= 20:
            confidence = 30 + (relative_score - 20) * 1.0   # 30-50%
        else:
            confidence = relative_score * 1.5               # 0-30%
        
        return min(95.0, max(5.0, confidence))  # Cap between 5-95%
    
    def _get_confidence_level(self, confidence: float) -> str:
        """
        Convert confidence percentage to human-readable level.
        """
        if confidence >= 75:
            return 'High'
        elif confidence >= 55:
            return 'Medium'
        elif confidence >= 35:
            return 'Low'
        else:
            return 'Very Low'
    
    def get_domain_suggestions_for_exam(self, question_text: str, exam_id: int, top_n: int = 3) -> List[Dict]:
        """
        Get domain suggestions for a specific exam by ID.
        """
        try:
            exam = Exam.objects.get(id=exam_id, is_active=True)
            suggestions = self.suggest_domains(question_text, exam.name, top_n)
            
            # Enrich with actual domain objects
            for suggestion in suggestions:
                try:
                    domain = Domain.objects.get(
                        exam=exam,
                        name=suggestion['domain_name'],
                        is_active=True
                    )
                    suggestion['domain_id'] = domain.id
                    suggestion['domain_object'] = domain
                except Domain.DoesNotExist:
                    suggestion['domain_id'] = None
                    suggestion['domain_object'] = None
            
            return suggestions
            
        except Exam.DoesNotExist:
            return []

    def get_best_domain_for_question(self, question_text: str, exam_id: int, min_confidence: float = 40.0) -> Dict:
        """
        Get the best domain suggestion for a question.
        Returns None if no domain meets the minimum confidence threshold.
        
        Args:
            question_text: The question text to analyze
            exam_id: The exam ID
            min_confidence: Minimum confidence required (default 40%)
            
        Returns:
            Dict with domain info or None if no confident match
        """
        suggestions = self.get_domain_suggestions_for_exam(question_text, exam_id, top_n=1)

        if suggestions and len(suggestions) > 0:
            best_suggestion = suggestions[0]
            if best_suggestion['confidence'] >= min_confidence and best_suggestion.get('domain_id'):
                return best_suggestion
        
        return None


# Convenience function for easy use
def suggest_domains_for_question(question_text: str, exam_name: str, top_n: int = 3) -> List[Dict]:
    """
    Convenience function to get domain suggestions.
    
    Example usage:
    suggestions = suggest_domains_for_question(
        "You are developing a microservices application...",
        "google_cloud_developer"
    )
    """
    suggester = DomainSuggester()
    return suggester.suggest_domains(question_text, exam_name, top_n)


def get_auto_domain_for_question(question_text: str, exam_id: int) -> Dict:
    """
    Get automatically selected domain for a question.
    
    Example usage:
    domain_info = get_auto_domain_for_question(
        "You are developing a microservices application...",
        1  # exam ID
    )
    """
    suggester = DomainSuggester()
    return suggester.get_best_domain_for_question(question_text, exam_id)