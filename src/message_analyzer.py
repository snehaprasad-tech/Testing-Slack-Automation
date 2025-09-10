import re
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import nltk
from fuzzywuzzy import fuzz
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

@dataclass
class SlackMessage:
    id: str
    text: str
    user: str
    channel: str
    timestamp: datetime
    thread_ts: Optional[str] = None
    reactions: Optional[List[str]] = None
    category: Optional[str] = None
    priority_score: Optional[float] = None
    similar_tickets: Optional[List[str]] = None

@dataclass
class TicketSimilarity:
    ticket_id: str
    similarity_score: float
    category: str
    key_phrases: List[str]

class MessageAnalyzer:
    def __init__(self):
        self.categories = {
            'bug_report': {
                'keywords': ['bug', 'error', 'issue', 'problem', 'broken', 'not working', 'crash', 'fail'],
                'patterns': [r'error.*code', r'exception', r'stack trace', r'500.*error', r'404.*error'],
                'color': '#FF6B6B'  # Red
            },
            'feature_request': {
                'keywords': ['feature', 'enhancement', 'improve', 'add', 'new', 'request', 'would like', 'could we'],
                'patterns': [r'can.*we.*add', r'would.*be.*nice', r'feature.*request'],
                'color': '#4ECDC4'  # Teal
            },
            'question': {
                'keywords': ['how', 'what', 'where', 'when', 'why', 'help', 'question', '?'],
                'patterns': [r'\?$', r'how.*to', r'what.*is', r'can.*someone'],
                'color': '#45B7D1'  # Blue
            },
            'urgent': {
                'keywords': ['urgent', 'asap', 'emergency', 'critical', 'down', 'outage', 'production'],
                'patterns': [r'urgent.*help', r'production.*down', r'critical.*issue'],
                'color': '#FF4757'  # Bright Red
            },
            'deployment': {
                'keywords': ['deploy', 'release', 'push', 'merge', 'build', 'ci/cd', 'pipeline'],
                'patterns': [r'deploy.*to', r'release.*notes', r'build.*failed'],
                'color': '#FFA726'  # Orange
            },
            'access_request': {
                'keywords': ['access', 'permission', 'login', 'password', 'account', 'credential'],
                'patterns': [r'need.*access', r'can.*t.*login', r'permission.*denied'],
                'color': '#AB47BC'  # Purple
            },
            'general': {
                'keywords': ['update', 'info', 'fyi', 'notice', 'announcement'],
                'patterns': [r'fyi', r'heads.*up', r'just.*to.*let.*you.*know'],
                'color': '#66BB6A'  # Green
            }
        }
        
        # Initialize sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Storage for processed messages and tickets
        self.messages: List[SlackMessage] = []
        self.ticket_embeddings = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove URLs, mentions, and special characters
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'<@[A-Z0-9]+>', '', text)  # Remove user mentions
        text = re.sub(r'<#[A-Z0-9]+\|[^>]+>', '', text)  # Remove channel mentions
        text = re.sub(r':[a-zA-Z0-9_-]+:', '', text)  # Remove emojis
        text = re.sub(r'[^\w\s?!.]', ' ', text)  # Keep only alphanumeric, spaces, and basic punctuation
        text = ' '.join(text.split())  # Remove extra whitespace
        return text.lower()

    def categorize_message(self, text: str) -> Tuple[str, float]:
        """Categorize a message based on keywords and patterns"""
        preprocessed_text = self.preprocess_text(text)
        category_scores = {}
        
        for category, config in self.categories.items():
            score = 0
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in preprocessed_text:
                    score += 1
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, preprocessed_text):
                    score += 2  # Patterns have higher weight
            
            category_scores[category] = score
        
        # Find the category with highest score
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        
        # If no category matches well, assign to 'general'
        if best_score == 0:
            best_category = 'general'
            best_score = 0.1
        
        # Normalize score to 0-1 range
        normalized_score = min(best_score / 5.0, 1.0)
        
        return best_category, normalized_score

    def calculate_priority_score(self, message: SlackMessage) -> float:
        """Calculate priority score based on various factors"""
        score = 0.0
        text = self.preprocess_text(message.text)
        
        # Urgency keywords
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'production', 'down', 'outage']
        for keyword in urgent_keywords:
            if keyword in text:
                score += 0.3
        
        # Question marks indicate need for response
        score += text.count('?') * 0.1
        
        # Length factor (longer messages might be more detailed/important)
        if len(text) > 100:
            score += 0.2
        
        # Time factor (recent messages get slight priority boost)
        hours_old = (datetime.now() - message.timestamp).total_seconds() / 3600
        if hours_old < 1:
            score += 0.2
        elif hours_old < 24:
            score += 0.1
        
        # Reactions indicate importance
        if message.reactions and len(message.reactions) > 2:
            score += 0.2
        
        # Category-based scoring
        if message.category in ['urgent', 'bug_report']:
            score += 0.4
        elif message.category in ['feature_request', 'access_request']:
            score += 0.2
        
        return min(score, 1.0)

    def find_similar_tickets(self, message: SlackMessage, top_k: int = 5) -> List[TicketSimilarity]:
        """Find similar tickets using semantic similarity"""
        if not self.messages:
            return []
        
        message_text = self.preprocess_text(message.text)
        message_embedding = self.sentence_model.encode([message_text])
        
        similarities = []
        
        for existing_message in self.messages:
            if existing_message.id == message.id:
                continue
                
            existing_text = self.preprocess_text(existing_message.text)
            existing_embedding = self.sentence_model.encode([existing_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(message_embedding, existing_embedding)[0][0]
            
            # Also calculate fuzzy string similarity
            fuzzy_similarity = fuzz.ratio(message_text, existing_text) / 100.0
            
            # Combine both similarities
            combined_similarity = (similarity * 0.7) + (fuzzy_similarity * 0.3)
            
            if combined_similarity > 0.3:  # Threshold for similarity
                # Extract key phrases
                key_phrases = self._extract_key_phrases(existing_text)
                
                similarities.append(TicketSimilarity(
                    ticket_id=existing_message.id,
                    similarity_score=combined_similarity,
                    category=existing_message.category or 'general',
                    key_phrases=key_phrases
                ))
        
        # Sort by similarity score and return top k
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)
        return similarities[:top_k]

    def _extract_key_phrases(self, text: str, max_phrases: int = 3) -> List[str]:
        """Extract key phrases from text using simple n-gram analysis"""
        words = text.split()
        phrases = []
        
        # Extract 2-3 word phrases that might be meaningful
        for i in range(len(words) - 1):
            if len(words[i]) > 3 and len(words[i+1]) > 3:  # Skip short words
                phrase = f"{words[i]} {words[i+1]}"
                if len(phrase) > 6:  # Minimum phrase length
                    phrases.append(phrase)
        
        # Return most common phrases (simplified)
        return phrases[:max_phrases]

    def process_message(self, message_data: Dict) -> SlackMessage:
        """Process a single message and return analyzed SlackMessage object"""
        # Create SlackMessage object
        message = SlackMessage(
            id=message_data.get('id', str(hash(message_data.get('text', '')))),
            text=message_data.get('text', ''),
            user=message_data.get('user', 'unknown'),
            channel=message_data.get('channel', 'general'),
            timestamp=datetime.fromtimestamp(float(message_data.get('ts', datetime.now().timestamp()))),
            thread_ts=message_data.get('thread_ts'),
            reactions=message_data.get('reactions', [])
        )
        
        # Analyze message
        category, confidence = self.categorize_message(message.text)
        message.category = category
        
        # Calculate priority score
        message.priority_score = self.calculate_priority_score(message)
        
        # Find similar tickets
        message.similar_tickets = self.find_similar_tickets(message)
        
        # Store message for future similarity comparisons
        self.messages.append(message)
        
        self.logger.info(f"Processed message: {message.id} -> Category: {category}, Priority: {message.priority_score:.2f}")
        
        return message

    def batch_process_messages(self, messages_data: List[Dict]) -> List[SlackMessage]:
        """Process multiple messages in batch"""
        processed_messages = []
        
        for message_data in messages_data:
            try:
                processed_message = self.process_message(message_data)
                processed_messages.append(processed_message)
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                continue
        
        return processed_messages

    def get_category_stats(self) -> Dict:
        """Get statistics about message categories"""
        if not self.messages:
            return {}
        
        category_counts = {}
        for message in self.messages:
            category = message.category or 'general'
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_messages': len(self.messages),
            'categories': category_counts,
            'avg_priority': sum(msg.priority_score or 0 for msg in self.messages) / len(self.messages)
        }

    def export_data(self, format: str = 'json') -> str:
        """Export processed messages data"""
        if format == 'json':
            data = [asdict(message) for message in self.messages]
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            df = pd.DataFrame([asdict(message) for message in self.messages])
            return df.to_csv(index=False)
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'")