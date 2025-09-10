#!/usr/bin/env python3
"""
Simple demo of the Slack Message Analytics system
This demo works without external dependencies
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class SimpleMessageAnalyzer:
    """Simplified version of the message analyzer for demonstration"""
    
    def __init__(self):
        self.categories = {
            'bug_report': {
                'keywords': ['bug', 'error', 'issue', 'problem', 'broken', 'not working', 'crash', 'fail'],
                'color': '#FF6B6B'
            },
            'feature_request': {
                'keywords': ['feature', 'enhancement', 'improve', 'add', 'new', 'request', 'would like'],
                'color': '#4ECDC4'
            },
            'question': {
                'keywords': ['how', 'what', 'where', 'when', 'why', 'help', 'question', '?'],
                'color': '#45B7D1'
            },
            'urgent': {
                'keywords': ['urgent', 'asap', 'emergency', 'critical', 'down', 'outage', 'production'],
                'color': '#FF4757'
            },
            'general': {
                'keywords': ['update', 'info', 'fyi', 'notice'],
                'color': '#66BB6A'
            }
        }
    
    def categorize_message(self, text: str) -> Tuple[str, float]:
        """Simple categorization based on keywords"""
        text_lower = text.lower()
        category_scores = {}
        
        for category, config in self.categories.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in text_lower:
                    score += 1
            category_scores[category] = score
        
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        
        if best_score == 0:
            best_category = 'general'
            best_score = 0.1
        
        return best_category, min(best_score / 3.0, 1.0)
    
    def calculate_priority(self, text: str, category: str) -> float:
        """Simple priority calculation"""
        priority = 0.0
        text_lower = text.lower()
        
        # Urgent keywords
        urgent_words = ['urgent', 'asap', 'critical', 'production', 'down']
        for word in urgent_words:
            if word in text_lower:
                priority += 0.3
        
        # Question marks
        priority += text_lower.count('?') * 0.1
        
        # Category bonus
        if category == 'urgent':
            priority += 0.5
        elif category == 'bug_report':
            priority += 0.3
        
        return min(priority, 1.0)

def generate_sample_messages():
    """Generate sample messages for demonstration"""
    messages = [
        {
            "id": "1",
            "text": "Our production server is down! Users can't access the application. This is urgent!",
            "user": "john_doe",
            "channel": "alerts",
            "timestamp": datetime.now() - timedelta(hours=1)
        },
        {
            "id": "2", 
            "text": "Can someone help me understand how the authentication flow works?",
            "user": "jane_smith",
            "channel": "dev-help",
            "timestamp": datetime.now() - timedelta(hours=2)
        },
        {
            "id": "3",
            "text": "I found a bug in the user registration form. Getting 500 errors when submitting.",
            "user": "mike_wilson", 
            "channel": "bug-reports",
            "timestamp": datetime.now() - timedelta(hours=3)
        },
        {
            "id": "4",
            "text": "Feature request: Can we add a dark mode toggle to the settings?",
            "user": "sarah_johnson",
            "channel": "feature-requests", 
            "timestamp": datetime.now() - timedelta(hours=4)
        },
        {
            "id": "5",
            "text": "FYI: Scheduled maintenance this Sunday 2-4 AM. App will be unavailable.",
            "user": "admin",
            "channel": "announcements",
            "timestamp": datetime.now() - timedelta(hours=12)
        }
    ]
    return messages

def analyze_messages(messages: List[Dict]) -> List[Dict]:
    """Analyze messages and return results"""
    analyzer = SimpleMessageAnalyzer()
    results = []
    
    for msg in messages:
        category, confidence = analyzer.categorize_message(msg['text'])
        priority = analyzer.calculate_priority(msg['text'], category)
        
        result = {
            'id': msg['id'],
            'text': msg['text'],
            'user': msg['user'],
            'channel': msg['channel'],
            'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'category': category,
            'confidence': round(confidence, 2),
            'priority': round(priority, 2),
            'color': analyzer.categories[category]['color']
        }
        results.append(result)
    
    return results

def print_dashboard(results: List[Dict]):
    """Print a simple text-based dashboard"""
    print("\n" + "="*80)
    print("🚀 SLACK MESSAGE ANALYTICS DASHBOARD")
    print("="*80)
    
    # Statistics
    total_messages = len(results)
    high_priority = sum(1 for r in results if r['priority'] > 0.5)
    categories = {}
    for r in results:
        categories[r['category']] = categories.get(r['category'], 0) + 1
    
    print(f"\n📊 QUICK STATS:")
    print(f"   Total Messages: {total_messages}")
    print(f"   High Priority: {high_priority}")
    print(f"   Categories: {len(categories)}")
    
    print(f"\n📈 CATEGORY BREAKDOWN:")
    for category, count in categories.items():
        print(f"   {category.replace('_', ' ').title()}: {count}")
    
    print(f"\n📋 MESSAGE ANALYSIS:")
    print("-" * 80)
    
    # Sort by priority
    results.sort(key=lambda x: x['priority'], reverse=True)
    
    for result in results:
        priority_indicator = "🔥" if result['priority'] > 0.7 else "⚠️" if result['priority'] > 0.4 else "ℹ️"
        category_emoji = {
            'bug_report': '🐛',
            'feature_request': '✨', 
            'question': '❓',
            'urgent': '🚨',
            'general': '📢'
        }.get(result['category'], '📝')
        
        print(f"\n{priority_indicator} Message {result['id']} | Priority: {result['priority']:.2f}")
        print(f"{category_emoji} Category: {result['category'].replace('_', ' ').title()}")
        print(f"👤 User: @{result['user']} in #{result['channel']}")
        print(f"🕒 Time: {result['timestamp']}")
        print(f"💬 Text: {result['text']}")
        print(f"🎨 Color: {result['color']}")
        print("-" * 40)
    
    print("\n🤖 AUTOMATION SUGGESTIONS:")
    if categories.get('bug_report', 0) > 1:
        print("   • Set up automatic bug report triage")
    if categories.get('question', 0) > 1:
        print("   • Consider implementing a FAQ chatbot")
    if categories.get('urgent', 0) > 0:
        print("   • Create urgent issue escalation workflow")
    if high_priority > total_messages * 0.3:
        print("   • Review priority thresholds - many high priority items")
    
    print("\n" + "="*80)
    print("Dashboard Demo Complete! 🎉")
    print("="*80)

def main():
    """Main demo function"""
    print("Initializing Slack Message Analytics Demo...")
    
    # Generate sample data
    messages = generate_sample_messages()
    print(f"Generated {len(messages)} sample messages")
    
    # Analyze messages
    results = analyze_messages(messages)
    print("Analysis complete!")
    
    # Display dashboard
    print_dashboard(results)
    
    # Save results to JSON for inspection
    with open('/workspace/demo_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: /workspace/demo_results.json")
    
    print("\n🚀 To run the full interactive dashboard:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Run: python src/app.py")
    print("   3. Open: http://localhost:8050")

if __name__ == '__main__':
    main()