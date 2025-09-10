#!/usr/bin/env python3
"""
Simple Local Dashboard - No complex dependencies
Creates a standalone HTML file that can be opened in any browser
"""

import json
import os
import webbrowser
from local_analyzer import LocalMessageAnalyzer, generate_sample_data

def create_simple_dashboard():
    """Create a simple, standalone HTML dashboard"""
    
    # Initialize and process data
    analyzer = LocalMessageAnalyzer()
    sample_data = generate_sample_data()
    processed_messages = analyzer.batch_process_messages(sample_data)
    
    analytics = analyzer.get_analytics_data()
    suggestions = analyzer.generate_automation_suggestions()
    
    # Sort messages by priority
    processed_messages.sort(key=lambda x: x.priority_score, reverse=True)
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
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
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
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
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #F39C12;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #A0AEC0;
            font-size: 1.1em;
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
        
        .section-header h2 {{
            font-size: 1.5em;
            color: #F39C12;
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        .message-card {{
            background: rgba(255, 255, 255, 0.08);
            margin-bottom: 20px;
            border-radius: 12px;
            overflow: hidden;
            border-left: 5px solid;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .message-card:hover {{
            transform: translateX(8px);
            background: rgba(255, 255, 255, 0.12);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }}
        
        .message-header {{
            padding: 18px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .message-content {{
            padding: 18px;
        }}
        
        .message-text {{
            font-size: 1.1em;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .message-meta {{
            font-size: 0.9em;
            color: #A0AEC0;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .category-badge {{
            color: white;
        }}
        
        .priority-badge {{
            background: #34495E;
            color: #FFFFFF;
        }}
        
        .user-info {{
            color: #A0AEC0;
            font-size: 0.9em;
        }}
        
        .similar-section {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .similar-ticket {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 3px solid #3498DB;
        }}
        
        .similar-ticket-header {{
            font-weight: bold;
            color: #3498DB;
            margin-bottom: 5px;
        }}
        
        .similar-ticket-preview {{
            font-size: 0.9em;
            color: #A0AEC0;
            font-style: italic;
        }}
        
        .suggestion-card {{
            background: rgba(255, 255, 255, 0.08);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 5px solid #F39C12;
            transition: transform 0.3s ease;
        }}
        
        .suggestion-card:hover {{
            transform: translateY(-3px);
        }}
        
        .suggestion-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 12px;
            color: #F39C12;
        }}
        
        .suggestion-description {{
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        
        .suggestion-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.9em;
        }}
        
        .priority-critical {{ border-left-color: #FF4757; }}
        .priority-high {{ border-left-color: #FFA726; }}
        .priority-medium {{ border-left-color: #45B7D1; }}
        .priority-low {{ border-left-color: #66BB6A; }}
        
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
            margin-right: 12px;
        }}
        
        .legend-label {{
            font-weight: 500;
        }}
        
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #A0AEC0;
            font-style: italic;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .message-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
            
            .suggestion-meta {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
        
        .emoji {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">🚀</span>Slack Message Analytics</h1>
            <p>Local Dashboard - Real-time Analysis of {analytics.get('total_messages', 0)} Messages</p>
            <p style="margin-top: 10px; font-size: 0.9em; color: #A0AEC0;">
                Generated on {analytics.get('timestamp', 'N/A')} • No deployment required
            </p>
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
                <h2><span class="emoji">🎨</span>Category Legend</h2>
            </div>
            <div class="section-content">
                <div class="legend">
                    {generate_legend_items(analyzer.categories)}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2><span class="emoji">📋</span>Message Analysis ({len(processed_messages)} messages)</h2>
            </div>
            <div class="section-content">
                {generate_message_cards_html(processed_messages, analyzer.categories)}
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2><span class="emoji">🤖</span>Automation Suggestions</h2>
            </div>
            <div class="section-content">
                {generate_suggestions_html(suggestions)}
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2><span class="emoji">📊</span>Detailed Analytics</h2>
            </div>
            <div class="section-content">
                {generate_analytics_html(analytics)}
            </div>
        </div>
    </div>
    
    <script>
        // Simple interactivity
        document.querySelectorAll('.message-card').forEach(card => {{
            card.addEventListener('click', function() {{
                this.style.transform = this.style.transform === 'scale(1.02)' ? 'scale(1)' : 'scale(1.02)';
            }});
        }});
        
        // Show load time
        window.addEventListener('load', function() {{
            console.log('Dashboard loaded successfully!');
        }});
    </script>
</body>
</html>"""
    
    return html_content

def generate_legend_items(categories):
    """Generate legend items HTML"""
    items = []
    for cat_name, cat_info in categories.items():
        emoji_map = {
            'bug_report': '🐛',
            'feature_request': '✨',
            'question': '❓',
            'urgent': '🚨',
            'deployment': '🚀',
            'access_request': '🔐',
            'general': '📢'
        }
        emoji = emoji_map.get(cat_name, '📝')
        
        item_html = f'''
            <div class="legend-item">
                <div class="legend-color" style="background-color: {cat_info['color']}"></div>
                <div class="legend-label">{emoji} {cat_name.replace('_', ' ').title()}</div>
            </div>
        '''
        items.append(item_html)
    
    return ''.join(items)

def generate_message_cards_html(messages, categories):
    """Generate message cards HTML"""
    if not messages:
        return '<div class="no-data">No messages to display</div>'
    
    cards = []
    for msg in messages:
        # Get category info
        cat_info = categories.get(msg.category, {})
        color = cat_info.get('color', '#666666')
        
        # Priority class
        priority_class = 'priority-high' if msg.priority_score > 0.7 else \
                        'priority-medium' if msg.priority_score > 0.3 else 'priority-low'
        
        # Similar tickets section
        similar_html = ''
        if msg.similar_tickets:
            similar_items = []
            for ticket in msg.similar_tickets:
                similar_item = f'''
                    <div class="similar-ticket">
                        <div class="similar-ticket-header">
                            Ticket {ticket['ticket_id']} ({ticket['similarity_score']*100:.1f}% similar)
                        </div>
                        <div class="similar-ticket-preview">{ticket['text_preview']}</div>
                    </div>
                '''
                similar_items.append(similar_item)
            
            similar_html = f'''
                <div class="similar-section">
                    <strong>🔗 Similar Tickets ({len(msg.similar_tickets)}):</strong>
                    {''.join(similar_items)}
                </div>
            '''
        
        # Emoji for category
        emoji_map = {
            'bug_report': '🐛',
            'feature_request': '✨',
            'question': '❓',
            'urgent': '🚨',
            'deployment': '🚀',
            'access_request': '🔐',
            'general': '📢'
        }
        emoji = emoji_map.get(msg.category, '📝')
        
        card_html = f'''
            <div class="message-card {priority_class}" style="border-left-color: {color}">
                <div class="message-header">
                    <div>
                        <span class="badge category-badge" style="background-color: {color}">
                            {emoji} {msg.category.replace('_', ' ').upper()}
                        </span>
                        <span class="badge priority-badge">Priority: {msg.priority_score:.2f}</span>
                    </div>
                    <div class="user-info">
                        👤 @{msg.user} in #{msg.channel}
                    </div>
                </div>
                <div class="message-content">
                    <div class="message-text">{msg.text}</div>
                    <div class="message-meta">
                        <span>📅 {msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
                        {f'<span>🔗 {len(msg.similar_tickets)} similar tickets</span>' if msg.similar_tickets else ''}
                    </div>
                    {similar_html}
                </div>
            </div>
        '''
        cards.append(card_html)
    
    return ''.join(cards)

def generate_suggestions_html(suggestions):
    """Generate automation suggestions HTML"""
    if not suggestions:
        return '<div class="no-data">No automation suggestions available yet.<br>Process more messages to get personalized recommendations!</div>'
    
    cards = []
    for suggestion in suggestions:
        priority_class = f"priority-{suggestion['priority'].lower()}"
        
        # Priority emoji
        priority_emoji = {
            'Critical': '🔥',
            'High': '⚠️',
            'Medium': 'ℹ️',
            'Low': '💡'
        }.get(suggestion['priority'], '💡')
        
        card_html = f'''
            <div class="suggestion-card {priority_class}">
                <div class="suggestion-title">
                    {priority_emoji} {suggestion['title']}
                </div>
                <div class="suggestion-description">
                    {suggestion['description']}
                </div>
                <div class="suggestion-meta">
                    <span><strong>Priority:</strong> {suggestion['priority']}</span>
                    <span><strong>Impact:</strong> {suggestion['impact']}</span>
                    <span><strong>Effort:</strong> {suggestion['effort']}</span>
                </div>
            </div>
        '''
        cards.append(card_html)
    
    return ''.join(cards)

def generate_analytics_html(analytics):
    """Generate detailed analytics HTML"""
    categories = analytics.get('categories', {})
    priority_dist = analytics.get('priority_distribution', {})
    
    analytics_html = f'''
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px;">
                <h3 style="color: #F39C12; margin-bottom: 15px;">📊 Category Breakdown</h3>
                {generate_category_list(categories)}
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px;">
                <h3 style="color: #F39C12; margin-bottom: 15px;">⚡ Priority Distribution</h3>
                <div style="margin-bottom: 10px;">🔥 High Priority: {priority_dist.get('high', 0)} messages</div>
                <div style="margin-bottom: 10px;">⚠️ Medium Priority: {priority_dist.get('medium', 0)} messages</div>
                <div style="margin-bottom: 10px;">ℹ️ Low Priority: {priority_dist.get('low', 0)} messages</div>
            </div>
        </div>
    '''
    
    return analytics_html

def generate_category_list(categories):
    """Generate category list HTML"""
    if not categories:
        return '<div style="color: #A0AEC0;">No category data available</div>'
    
    items = []
    for category, count in categories.items():
        emoji_map = {
            'bug_report': '🐛',
            'feature_request': '✨',
            'question': '❓',
            'urgent': '🚨',
            'deployment': '🚀',
            'access_request': '🔐',
            'general': '📢'
        }
        emoji = emoji_map.get(category, '📝')
        
        item_html = f'<div style="margin-bottom: 8px;">{emoji} {category.replace("_", " ").title()}: {count} messages</div>'
        items.append(item_html)
    
    return ''.join(items)

def main():
    """Main function to create and open the dashboard"""
    print("🚀 Creating Simple Local Dashboard...")
    print("=" * 50)
    
    try:
        html_content = create_simple_dashboard()
        
        # Save to file
        html_file = 'slack_analytics_dashboard.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard created: {html_file}")
        print(f"📁 File size: {os.path.getsize(html_file) / 1024:.1f} KB")
        
        # Try to open in browser
        try:
            file_path = os.path.abspath(html_file)
            webbrowser.open(f'file://{file_path}')
            print(f"🌐 Dashboard opened in your default browser")
        except Exception as e:
            print(f"⚠️ Could not auto-open browser: {e}")
            print(f"🌐 Please manually open: {os.path.abspath(html_file)}")
        
        print(f"\n🎯 Dashboard Features:")
        print(f"   • ✅ Works completely offline")
        print(f"   • ✅ No installation or dependencies required")
        print(f"   • ✅ Responsive design with dark theme")
        print(f"   • ✅ Message categorization and priority scoring")
        print(f"   • ✅ Similar ticket matching")
        print(f"   • ✅ Automation suggestions")
        print(f"   • ✅ Detailed analytics and insights")
        
        return html_file
        
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return None

if __name__ == '__main__':
    main()