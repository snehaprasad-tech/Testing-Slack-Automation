#!/usr/bin/env python3
"""
Local-only Slack Message Analyzer
No external dependencies required - uses only Python standard library
"""

import json
import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter
import hashlib

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
    similar_tickets: Optional[List[Dict]] = None

class LocalMessageAnalyzer:
    """Local-only message analyzer using built-in Python libraries"""
    
    def __init__(self):
        self.categories = {
            'bug_report': {
                'keywords': ['bug', 'error', 'issue', 'problem', 'broken', 'not working', 'crash', 'fail', 'exception', '500', '404'],
                'patterns': [r'error.*code', r'exception', r'stack trace', r'500.*error', r'404.*error', r'not.*work'],
                'color': '#FF6B6B',  # Red
                'priority_boost': 0.3
            },
            'feature_request': {
                'keywords': ['feature', 'enhancement', 'improve', 'add', 'new', 'request', 'would like', 'could we', 'suggestion'],
                'patterns': [r'can.*we.*add', r'would.*be.*nice', r'feature.*request', r'enhancement'],
                'color': '#4ECDC4',  # Teal
                'priority_boost': 0.2
            },
            'question': {
                'keywords': ['how', 'what', 'where', 'when', 'why', 'help', 'question', 'explain', 'understand'],
                'patterns': [r'\?$', r'how.*to', r'what.*is', r'can.*someone', r'help.*me'],
                'color': '#45B7D1',  # Blue
                'priority_boost': 0.1
            },
            'urgent': {
                'keywords': ['urgent', 'asap', 'emergency', 'critical', 'down', 'outage', 'production', 'immediately'],
                'patterns': [r'urgent.*help', r'production.*down', r'critical.*issue', r'emergency'],
                'color': '#FF4757',  # Bright Red
                'priority_boost': 0.8
            },
            'deployment': {
                'keywords': ['deploy', 'release', 'push', 'merge', 'build', 'ci/cd', 'pipeline', 'staging'],
                'patterns': [r'deploy.*to', r'release.*notes', r'build.*failed', r'pipeline'],
                'color': '#FFA726',  # Orange
                'priority_boost': 0.3
            },
            'access_request': {
                'keywords': ['access', 'permission', 'login', 'password', 'account', 'credential', 'auth'],
                'patterns': [r'need.*access', r'can.*t.*login', r'permission.*denied', r'access.*to'],
                'color': '#AB47BC',  # Purple
                'priority_boost': 0.4
            },
            'general': {
                'keywords': ['update', 'info', 'fyi', 'notice', 'announcement', 'heads up'],
                'patterns': [r'fyi', r'heads.*up', r'just.*to.*let.*you.*know', r'update'],
                'color': '#66BB6A',  # Green
                'priority_boost': 0.0
            }
        }
        
        self.messages = []
        self.word_frequency = Counter()

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        # Remove user mentions
        text = re.sub(r'<@[A-Z0-9]+>', '', text)
        # Remove channel mentions  
        text = re.sub(r'<#[A-Z0-9]+\|[^>]+>', '', text)
        # Remove emojis
        text = re.sub(r':[a-zA-Z0-9_-]+:', '', text)
        # Clean special characters but keep basic punctuation
        text = re.sub(r'[^\w\s?!.]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.lower()

    def categorize_message(self, text: str) -> Tuple[str, float]:
        """Categorize message using keyword and pattern matching"""
        preprocessed_text = self.preprocess_text(text)
        category_scores = {}
        
        for category, config in self.categories.items():
            score = 0
            
            # Check keywords (case insensitive)
            for keyword in config['keywords']:
                if keyword.lower() in preprocessed_text:
                    score += 1
            
            # Check patterns (higher weight)
            for pattern in config['patterns']:
                if re.search(pattern, preprocessed_text, re.IGNORECASE):
                    score += 2
            
            category_scores[category] = score
        
        # Find best category
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        
        # Default to general if no matches
        if best_score == 0:
            best_category = 'general'
            best_score = 0.1
        
        # Normalize confidence score
        confidence = min(best_score / 5.0, 1.0)
        
        return best_category, confidence

    def calculate_priority_score(self, message: SlackMessage) -> float:
        """Calculate priority score based on various factors"""
        score = 0.0
        text = self.preprocess_text(message.text)
        
        # Category-based priority boost
        category_boost = self.categories.get(message.category, {}).get('priority_boost', 0.0)
        score += category_boost
        
        # Urgency keywords (additional boost)
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'production', 'down', 'outage', 'immediately']
        for keyword in urgent_keywords:
            if keyword in text:
                score += 0.2
                break  # Don't double count
        
        # Question marks indicate need for response
        question_count = text.count('?')
        score += min(question_count * 0.1, 0.3)  # Cap at 0.3
        
        # Exclamation marks indicate urgency
        exclamation_count = text.count('!')
        score += min(exclamation_count * 0.05, 0.2)  # Cap at 0.2
        
        # Length factor (longer messages might be more detailed)
        if len(text) > 100:
            score += 0.1
        elif len(text) > 200:
            score += 0.2
        
        # Time factor (recent messages get slight boost)
        if message.timestamp:
            hours_old = (datetime.now() - message.timestamp).total_seconds() / 3600
            if hours_old < 1:
                score += 0.15
            elif hours_old < 6:
                score += 0.1
            elif hours_old < 24:
                score += 0.05
        
        # Reactions indicate importance
        if message.reactions and len(message.reactions) > 1:
            score += min(len(message.reactions) * 0.05, 0.2)
        
        return min(score, 1.0)

    def simple_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation using word overlap"""
        words1 = set(self.preprocess_text(text1).split())
        words2 = set(self.preprocess_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union

    def find_similar_tickets(self, message: SlackMessage, top_k: int = 5) -> List[Dict]:
        """Find similar tickets using simple text similarity"""
        if not self.messages or len(self.messages) <= 1:
            return []
        
        similarities = []
        
        for existing_message in self.messages:
            if existing_message.id == message.id:
                continue
            
            # Calculate similarity
            similarity_score = self.simple_similarity(message.text, existing_message.text)
            
            if similarity_score > 0.2:  # Minimum threshold
                # Extract common words as "key phrases"
                words1 = set(self.preprocess_text(message.text).split())
                words2 = set(self.preprocess_text(existing_message.text).split())
                common_words = list(words1.intersection(words2))[:3]
                
                similarities.append({
                    'ticket_id': existing_message.id,
                    'similarity_score': round(similarity_score, 3),
                    'category': existing_message.category or 'general',
                    'key_phrases': common_words,
                    'text_preview': existing_message.text[:100] + "..." if len(existing_message.text) > 100 else existing_message.text
                })
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:top_k]

    def process_message(self, message_data: Dict) -> SlackMessage:
        """Process a single message"""
        # Create message object
        timestamp = message_data.get('ts')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromtimestamp(float(timestamp))
            except:
                timestamp = datetime.now()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now()
        
        message = SlackMessage(
            id=message_data.get('id', str(hash(message_data.get('text', '')))),
            text=message_data.get('text', ''),
            user=message_data.get('user', 'unknown'),
            channel=message_data.get('channel', 'general'),
            timestamp=timestamp,
            thread_ts=message_data.get('thread_ts'),
            reactions=message_data.get('reactions', [])
        )
        
        # Analyze message
        category, confidence = self.categorize_message(message.text)
        message.category = category
        
        # Calculate priority
        message.priority_score = self.calculate_priority_score(message)
        
        # Find similar tickets
        message.similar_tickets = self.find_similar_tickets(message)
        
        # Store for future comparisons
        self.messages.append(message)
        
        # Update word frequency for analytics
        words = self.preprocess_text(message.text).split()
        self.word_frequency.update(words)
        
        return message

    def batch_process_messages(self, messages_data: List[Dict]) -> List[SlackMessage]:
        """Process multiple messages"""
        processed_messages = []
        
        for message_data in messages_data:
            try:
                processed_message = self.process_message(message_data)
                processed_messages.append(processed_message)
            except Exception as e:
                print(f"Warning: Error processing message: {e}")
                continue
        
        return processed_messages

    def get_analytics_data(self) -> Dict:
        """Get analytics data for dashboard"""
        if not self.messages:
            return {}
        
        # Category distribution
        category_counts = Counter(msg.category for msg in self.messages)
        
        # Priority distribution
        high_priority = sum(1 for msg in self.messages if msg.priority_score > 0.7)
        medium_priority = sum(1 for msg in self.messages if 0.3 < msg.priority_score <= 0.7)
        low_priority = sum(1 for msg in self.messages if msg.priority_score <= 0.3)
        
        # Time analysis
        recent_messages = sum(1 for msg in self.messages 
                            if (datetime.now() - msg.timestamp).total_seconds() < 86400)  # Last 24 hours
        
        # User analysis
        user_counts = Counter(msg.user for msg in self.messages)
        
        # Channel analysis
        channel_counts = Counter(msg.channel for msg in self.messages)
        
        return {
            'total_messages': len(self.messages),
            'categories': dict(category_counts),
            'priority_distribution': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            },
            'recent_messages': recent_messages,
            'top_users': dict(user_counts.most_common(5)),
            'top_channels': dict(channel_counts.most_common(5)),
            'avg_priority': sum(msg.priority_score for msg in self.messages) / len(self.messages),
            'top_words': dict(self.word_frequency.most_common(10))
        }

    def generate_automation_suggestions(self) -> List[Dict]:
        """Generate automation suggestions based on analysis"""
        suggestions = []
        
        if not self.messages:
            return suggestions
        
        analytics = self.get_analytics_data()
        categories = analytics.get('categories', {})
        
        # Access request automation
        if categories.get('access_request', 0) >= 2:
            suggestions.append({
                'title': 'Self-Service Access Portal',
                'description': f'Found {categories["access_request"]} access requests. Implement a self-service portal to reduce manual work.',
                'priority': 'High',
                'impact': 'Reduces response time by 80%',
                'effort': 'Medium',
                'category': 'access_request'
            })
        
        # FAQ bot for questions
        if categories.get('question', 0) >= 3:
            suggestions.append({
                'title': 'Automated FAQ Bot',
                'description': f'Found {categories["question"]} questions. A chatbot could handle common queries automatically.',
                'priority': 'Medium',
                'impact': 'Reduces support load by 60%',
                'effort': 'High',
                'category': 'question'
            })
        
        # Bug triage automation
        if categories.get('bug_report', 0) >= 2:
            suggestions.append({
                'title': 'Automated Bug Triage',
                'description': f'Found {categories["bug_report"]} bug reports. Implement automatic priority assignment and routing.',
                'priority': 'High',
                'impact': 'Improves response time by 50%',
                'effort': 'Medium',
                'category': 'bug_report'
            })
        
        # Deployment notifications
        if categories.get('deployment', 0) >= 1:
            suggestions.append({
                'title': 'Deployment Status Automation',
                'description': 'Automate deployment notifications and status updates to reduce manual communication.',
                'priority': 'Medium',
                'impact': 'Improves team awareness',
                'effort': 'Low',
                'category': 'deployment'
            })
        
        # Urgent escalation
        urgent_count = sum(1 for msg in self.messages if msg.priority_score > 0.8)
        if urgent_count > 0:
            suggestions.append({
                'title': 'Urgent Issue Escalation',
                'description': f'Found {urgent_count} urgent issues. Set up automatic escalation workflows.',
                'priority': 'Critical',
                'impact': 'Prevents service downtime',
                'effort': 'Low',
                'category': 'urgent'
            })
        
        return suggestions

    def export_data(self, format_type: str = 'json') -> str:
        """Export processed data"""
        data = []
        for message in self.messages:
            msg_dict = asdict(message)
            # Convert datetime to string for JSON serialization
            if isinstance(msg_dict['timestamp'], datetime):
                msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
            data.append(msg_dict)
        
        if format_type == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            # Simple CSV format
            if not data:
                return ""
            
            headers = ['id', 'text', 'user', 'channel', 'timestamp', 'category', 'priority_score']
            csv_lines = [','.join(headers)]
            
            for item in data:
                row = []
                for header in headers:
                    value = str(item.get(header, ''))
                    # Escape commas in text
                    if ',' in value:
                        value = f'"{value}"'
                    row.append(value)
                csv_lines.append(','.join(row))
            
            return '\n'.join(csv_lines)

def generate_sample_data() -> List[Dict]:
    """Generate sample Slack messages for testing"""
    base_time = datetime.now()
    
    sample_messages = [
        {
            "id": "msg_001",
            "text": "URGENT: Production server is down! Users can't login. Need immediate help!",
            "user": "john_doe",
            "channel": "alerts",
            "ts": (base_time - timedelta(hours=1)).timestamp(),
            "reactions": ["fire", "eyes", "sos"]
        },
        {
            "id": "msg_002", 
            "text": "Can someone help me understand how the OAuth authentication flow works? I'm getting confused with the redirect URLs.",
            "user": "jane_smith",
            "channel": "dev-help",
            "ts": (base_time - timedelta(hours=2)).timestamp(),
            "reactions": ["question"]
        },
        {
            "id": "msg_003",
            "text": "Found a critical bug in the user registration form. When users enter special characters, the form crashes with a 500 error. Stack trace attached.",
            "user": "mike_wilson",
            "channel": "bug-reports", 
            "ts": (base_time - timedelta(hours=3)).timestamp(),
            "reactions": ["bug", "thumbsup"]
        },
        {
            "id": "msg_004",
            "text": "Feature request: Can we add a dark mode toggle to the user settings page? Many users have been asking for this enhancement.",
            "user": "sarah_johnson",
            "channel": "feature-requests",
            "ts": (base_time - timedelta(hours=4)).timestamp(),
            "reactions": ["bulb", "thumbsup", "moon"]
        },
        {
            "id": "msg_005",
            "text": "The CI/CD pipeline failed again on the staging deployment. Looks like there's an issue with the Docker build process. Can someone investigate?",
            "user": "alex_brown",
            "channel": "devops",
            "ts": (base_time - timedelta(hours=5)).timestamp(),
            "reactions": ["wrench"]
        },
        {
            "id": "msg_006",
            "text": "I need access to the production database for debugging. Can someone grant me read-only permissions? My username is alex.brown.",
            "user": "alex_brown",
            "channel": "access-requests",
            "ts": (base_time - timedelta(hours=6)).timestamp(),
            "reactions": ["lock"]
        },
        {
            "id": "msg_007",
            "text": "FYI: Scheduled maintenance window this Sunday 2-4 AM EST. The main application will be temporarily unavailable. Please plan accordingly.",
            "user": "admin",
            "channel": "announcements",
            "ts": (base_time - timedelta(hours=12)).timestamp(),
            "reactions": ["loudspeaker", "thumbsup"]
        },
        {
            "id": "msg_008",
            "text": "Another authentication issue here. Users are getting randomly logged out after 10 minutes. This might be related to the session timeout configuration we changed last week.",
            "user": "tom_anderson",
            "channel": "bug-reports",
            "ts": (base_time - timedelta(hours=8)).timestamp(),
            "reactions": ["lock", "bug"]
        },
        {
            "id": "msg_009",
            "text": "How do we handle GDPR data export requests? Do we have a standard process for this? Customer is asking for all their data.",
            "user": "lisa_martinez",
            "channel": "compliance",
            "ts": (base_time - timedelta(hours=10)).timestamp(),
            "reactions": ["scales", "question"]
        },
        {
            "id": "msg_010",
            "text": "New API endpoint is ready for testing! Can someone from QA please review the documentation and run the test cases? Link in thread.",
            "user": "david_lee",
            "channel": "api-development",
            "ts": (base_time - timedelta(hours=14)).timestamp(),
            "reactions": ["checkmark", "clipboard"]
        }
    ]
    
    return sample_messages

if __name__ == '__main__':
    # Simple CLI test
    print("🚀 Local Slack Message Analyzer")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = LocalMessageAnalyzer()
    
    # Generate and process sample data
    sample_data = generate_sample_data()
    processed_messages = analyzer.batch_process_messages(sample_data)
    
    print(f"✅ Processed {len(processed_messages)} messages")
    
    # Show analytics
    analytics = analyzer.get_analytics_data()
    print(f"\n📊 Analytics:")
    print(f"   Categories: {analytics['categories']}")
    print(f"   Priority Distribution: {analytics['priority_distribution']}")
    print(f"   Average Priority: {analytics['avg_priority']:.2f}")
    
    # Show automation suggestions
    suggestions = analyzer.generate_automation_suggestions()
    print(f"\n🤖 Automation Suggestions ({len(suggestions)}):")
    for suggestion in suggestions:
        print(f"   • {suggestion['title']} ({suggestion['priority']} priority)")
    
    print(f"\n💾 Data exported to local_analysis_results.json")
    with open('local_analysis_results.json', 'w') as f:
        f.write(analyzer.export_data('json'))