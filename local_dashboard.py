#!/usr/bin/env python3
"""
Local Slack Analytics Dashboard
Simple web interface using only Python standard library + minimal dependencies
"""

import json
import os
import webbrowser
from datetime import datetime
from typing import List, Dict
import threading
import time

# Try to import Flask, fallback to simple HTTP server if not available
try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    import http.server
    import socketserver
    from urllib.parse import parse_qs, urlparse

from local_analyzer import LocalMessageAnalyzer, generate_sample_data

class LocalDashboard:
    def __init__(self):
        self.analyzer = LocalMessageAnalyzer()
        self.processed_messages = []
        self.port = 8080
        
    def process_sample_data(self):
        """Load and process sample data"""
        sample_data = generate_sample_data()
        self.processed_messages = self.analyzer.batch_process_messages(sample_data)
        print(f"✅ Processed {len(self.processed_messages)} sample messages")
    
    def get_dashboard_data(self):
        """Get all data needed for dashboard"""
        analytics = self.analyzer.get_analytics_data()
        suggestions = self.analyzer.generate_automation_suggestions()
        
        # Prepare messages for display
        messages_data = []
        for msg in sorted(self.processed_messages, key=lambda x: x.priority_score, reverse=True):
            msg_data = {
                'id': msg.id,
                'text': msg.text,
                'user': msg.user,
                'channel': msg.channel,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'category': msg.category,
                'priority_score': round(msg.priority_score, 2),
                'color': self.analyzer.categories[msg.category]['color'],
                'similar_count': len(msg.similar_tickets) if msg.similar_tickets else 0,
                'similar_tickets': msg.similar_tickets or []
            }
            messages_data.append(msg_data)
        
        return {
            'analytics': analytics,
            'messages': messages_data,
            'suggestions': suggestions,
            'categories': self.analyzer.categories
        }

def create_html_dashboard(dashboard_data):
    """Create HTML dashboard content"""
    analytics = dashboard_data['analytics']
    messages = dashboard_data['messages']
    suggestions = dashboard_data['suggestions']
    categories = dashboard_data['categories']
    
    # Create category chart data
    category_data = analytics.get('categories', {})
    category_labels = list(category_data.keys())
    category_values = list(category_data.values())
    category_colors = [categories.get(cat, {}).get('color', '#666666') for cat in category_labels]
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slack Message Analytics - Local Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1A1A1A 0%, #2D3748 100%);
            color: #FFFFFF;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #F39C12, #E74C3C);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #F39C12;
        }}
        
        .stat-label {{
            color: #A0AEC0;
            margin-top: 5px;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.05);
            margin-bottom: 30px;
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .section-header {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        .message-card {{
            background: rgba(255, 255, 255, 0.08);
            margin-bottom: 15px;
            border-radius: 10px;
            overflow: hidden;
            border-left: 4px solid;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .message-card:hover {{
            transform: translateX(5px);
            background: rgba(255, 255, 255, 0.12);
        }}
        
        .message-header {{
            padding: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .message-content {{
            padding: 15px;
        }}
        
        .priority-high {{ border-left-color: #FF4757; }}
        .priority-medium {{ border-left-color: #FFA726; }}
        .priority-low {{ border-left-color: #66BB6A; }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 8px;
        }}
        
        .category-badge {{
            color: white;
        }}
        
        .priority-badge {{
            background: #34495E;
            color: #FFFFFF;
        }}
        
        .suggestion-card {{
            background: rgba(255, 255, 255, 0.08);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #F39C12;
        }}
        
        .suggestion-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #F39C12;
        }}
        
        .suggestion-meta {{
            font-size: 0.9em;
            color: #A0AEC0;
            margin-top: 10px;
        }}
        
        .filter-buttons {{
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .filter-btn {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .filter-btn:hover, .filter-btn.active {{
            background: #F39C12;
            border-color: #F39C12;
        }}
        
        .category-legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 10px;
        }}
        
        .similar-tickets {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .similar-ticket {{
            background: rgba(255, 255, 255, 0.05);
            padding: 8px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Slack Message Analytics</h1>
            <p>Local Dashboard - Analyzing {analytics.get('total_messages', 0)} messages</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{analytics.get('total_messages', 0)}</div>
                <div class="stat-label">Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analytics.get('priority_distribution', {}).get('high', 0)}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(analytics.get('categories', {}))}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analytics.get('avg_priority', 0):.2f}</div>
                <div class="stat-label">Avg Priority</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>📊 Category Legend</h2>
            </div>
            <div class="section-content">
                <div class="category-legend">
                    {' '.join([f'<div class="legend-item"><div class="legend-color" style="background-color: {cat_info["color"]}"></div><span>{cat_name.replace("_", " ").title()}</span></div>' for cat_name, cat_info in categories.items()])}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>📋 Messages Analysis</h2>
            </div>
            <div class="section-content">
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterMessages('all')">All Messages</button>
                    <button class="filter-btn" onclick="filterMessages('high')">High Priority</button>
                    <button class="filter-btn" onclick="filterMessages('urgent')">Urgent</button>
                    <button class="filter-btn" onclick="filterMessages('questions')">Questions</button>
                </div>
                
                <div id="messages-container">
                    {generate_message_cards(messages)}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>🤖 Automation Suggestions</h2>
            </div>
            <div class="section-content">
                {generate_suggestion_cards(suggestions)}
            </div>
        </div>
    </div>
    
    <script>
        let allMessages = {json.dumps(messages)};
        
        function filterMessages(filter) {{
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            let filteredMessages = allMessages;
            
            switch(filter) {{
                case 'high':
                    filteredMessages = allMessages.filter(msg => msg.priority_score > 0.7);
                    break;
                case 'urgent':
                    filteredMessages = allMessages.filter(msg => msg.category === 'urgent');
                    break;
                case 'questions':
                    filteredMessages = allMessages.filter(msg => msg.category === 'question');
                    break;
            }}
            
            updateMessageCards(filteredMessages);
        }}
        
        function updateMessageCards(messages) {{
            const container = document.getElementById('messages-container');
            container.innerHTML = messages.map(msg => createMessageCard(msg)).join('');
        }}
        
        function createMessageCard(msg) {{
            const priorityClass = msg.priority_score > 0.7 ? 'priority-high' : 
                                msg.priority_score > 0.3 ? 'priority-medium' : 'priority-low';
            
            const similarTicketsHtml = msg.similar_tickets.length > 0 ? `
                <div class="similar-tickets">
                    <strong>Similar Tickets (${msg.similar_tickets.length}):</strong>
                    ${{msg.similar_tickets.map(ticket => `
                        <div class="similar-ticket">
                            Ticket ${{ticket.ticket_id}} (${{(ticket.similarity_score * 100).toFixed(1)}}% similar)
                            <br><small>${{ticket.text_preview}}</small>
                        </div>
                    `).join('')}}
                </div>
            ` : '';
            
            return `
                <div class="message-card ${priorityClass}">
                    <div class="message-header">
                        <span class="badge category-badge" style="background-color: ${msg.color}">
                            ${msg.category.replace('_', ' ').toUpperCase()}
                        </span>
                        <span class="badge priority-badge">Priority: ${msg.priority_score}</span>
                        <span style="float: right; color: #A0AEC0; font-size: 0.9em;">
                            @${msg.user} in #${msg.channel}
                        </span>
                    </div>
                    <div class="message-content">
                        <p>${msg.text}</p>
                        <div style="margin-top: 10px; font-size: 0.9em; color: #A0AEC0;">
                            <span>📅 ${msg.timestamp}</span>
                            ${msg.similar_count > 0 ? `<span style="margin-left: 20px;">🔗 ${msg.similar_count} similar</span>` : ''}
                        </div>
                        ${similarTicketsHtml}
                    </div>
                </div>
            `;
        }}
        
        // Auto-refresh every 30 seconds (if running with Flask)
        if (window.location.protocol.includes('http')) {{
            setInterval(() => {{
                // Could implement auto-refresh here
            }}, 30000);
        }}
    </script>
</body>
</html>
"""
    
    return html_template

def generate_message_cards(messages):
    """Generate HTML for message cards"""
    cards_html = []
    
    for msg in messages:
        priority_class = 'priority-high' if msg['priority_score'] > 0.7 else \
                        'priority-medium' if msg['priority_score'] > 0.3 else 'priority-low'
        
        similar_html = ''
        if msg['similar_tickets']:
            similar_html = f"""
                <div class="similar-tickets">
                    <strong>Similar Tickets ({len(msg['similar_tickets'])}):</strong>
                    {''.join([f'<div class="similar-ticket">Ticket {t["ticket_id"]} ({t["similarity_score"]*100:.1f}% similar)<br><small>{t["text_preview"]}</small></div>' for t in msg['similar_tickets']])}
                </div>
            """
        
        card_html = f"""
            <div class="message-card {priority_class}" data-category="{msg['category']}" data-priority="{msg['priority_score']}">
                <div class="message-header">
                    <span class="badge category-badge" style="background-color: {msg['color']}">
                        {msg['category'].replace('_', ' ').upper()}
                    </span>
                    <span class="badge priority-badge">Priority: {msg['priority_score']}</span>
                    <span style="float: right; color: #A0AEC0; font-size: 0.9em;">
                        @{msg['user']} in #{msg['channel']}
                    </span>
                </div>
                <div class="message-content">
                    <p>{msg['text']}</p>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #A0AEC0;">
                        <span>📅 {msg['timestamp']}</span>
                        {f'<span style="margin-left: 20px;">🔗 {msg["similar_count"]} similar</span>' if msg['similar_count'] > 0 else ''}
                    </div>
                    {similar_html}
                </div>
            </div>
        """
        cards_html.append(card_html)
    
    return '\n'.join(cards_html)

def generate_suggestion_cards(suggestions):
    """Generate HTML for suggestion cards"""
    if not suggestions:
        return '<p style="text-align: center; color: #A0AEC0;">No automation suggestions available yet. Process more messages to get insights!</p>'
    
    cards_html = []
    for suggestion in suggestions:
        priority_color = '#FF4757' if suggestion['priority'] == 'Critical' else \
                        '#FFA726' if suggestion['priority'] == 'High' else \
                        '#45B7D1' if suggestion['priority'] == 'Medium' else '#66BB6A'
        
        card_html = f"""
            <div class="suggestion-card">
                <div class="suggestion-title">{suggestion['title']}</div>
                <p>{suggestion['description']}</p>
                <div class="suggestion-meta">
                    <span class="badge" style="background-color: {priority_color};">{suggestion['priority']} Priority</span>
                    <span style="margin-left: 15px;">💪 {suggestion['impact']}</span>
                    <span style="margin-left: 15px;">⏱️ {suggestion['effort']} Effort</span>
                </div>
            </div>
        """
        cards_html.append(card_html)
    
    return '\n'.join(cards_html)

def run_flask_dashboard():
    """Run dashboard using Flask if available"""
    app = Flask(__name__)
    dashboard = LocalDashboard()
    dashboard.process_sample_data()
    
    @app.route('/')
    def index():
        dashboard_data = dashboard.get_dashboard_data()
        html_content = create_html_dashboard(dashboard_data)
        return html_content
    
    @app.route('/api/data')
    def api_data():
        return jsonify(dashboard.get_dashboard_data())
    
    print(f"🚀 Starting Flask dashboard on http://localhost:{dashboard.port}")
    app.run(host='0.0.0.0', port=dashboard.port, debug=False)

def create_static_html():
    """Create a static HTML file that can be opened in browser"""
    dashboard = LocalDashboard()
    dashboard.process_sample_data()
    
    dashboard_data = dashboard.get_dashboard_data()
    html_content = create_html_dashboard(dashboard_data)
    
    html_file = 'slack_dashboard.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Created static HTML dashboard: {html_file}")
    return html_file

def main():
    """Main function to run the local dashboard"""
    print("🚀 Slack Message Analytics - Local Dashboard")
    print("=" * 50)
    
    # Try Flask first, fallback to static HTML
    if FLASK_AVAILABLE:
        print("📊 Flask is available - starting interactive dashboard...")
        try:
            run_flask_dashboard()
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"❌ Error running Flask dashboard: {e}")
            print("📄 Falling back to static HTML...")
            html_file = create_static_html()
            webbrowser.open(f'file://{os.path.abspath(html_file)}')
    else:
        print("📄 Flask not available - creating static HTML dashboard...")
        html_file = create_static_html()
        
        # Try to open in browser
        try:
            webbrowser.open(f'file://{os.path.abspath(html_file)}')
            print(f"🌐 Dashboard opened in your default browser")
        except:
            print(f"🌐 Please open this file in your browser: {os.path.abspath(html_file)}")
        
        print("\n📋 Dashboard Features:")
        print("   • Message categorization and priority scoring")
        print("   • Interactive filtering (All, High Priority, Urgent, Questions)")
        print("   • Similar ticket matching")
        print("   • Automation suggestions")
        print("   • Responsive design with dark theme")

if __name__ == '__main__':
    main()