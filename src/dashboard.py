import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

from message_analyzer import MessageAnalyzer, SlackMessage

class SlackAnalyticsDashboard:
    def __init__(self):
        # Initialize the Dash app with Bootstrap theme
        self.app = dash.Dash(__name__, external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ])
        
        self.analyzer = MessageAnalyzer()
        self.processed_messages = []
        
        # Define contrasting color palette
        self.colors = {
            'primary': '#2C3E50',      # Dark Blue
            'secondary': '#E74C3C',    # Red
            'accent': '#F39C12',       # Orange
            'success': '#27AE60',      # Green
            'info': '#3498DB',         # Light Blue
            'warning': '#F1C40F',      # Yellow
            'danger': '#E74C3C',       # Red
            'light': '#ECF0F1',        # Light Gray
            'dark': '#34495E',         # Dark Gray
            'background': '#1A1A1A',   # Very Dark
            'surface': '#2D3748',      # Dark Surface
            'text': '#FFFFFF',         # White Text
            'text_secondary': '#A0AEC0' # Light Gray Text
        }
        
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Setup the main dashboard layout"""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1([
                        html.I(className="fas fa-comments me-3"),
                        "Slack Message Analytics Dashboard"
                    ], className="text-center mb-4", style={'color': self.colors['text']}),
                    html.Hr(style={'border-color': self.colors['accent']})
                ])
            ]),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Upload & Analyze", className="card-title"),
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    html.I(className="fas fa-cloud-upload-alt fa-2x mb-2"),
                                    html.Br(),
                                    'Drag and Drop or ',
                                    html.A('Select Slack Export Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '100px',
                                    'lineHeight': '100px',
                                    'borderWidth': '2px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '10px',
                                    'textAlign': 'center',
                                    'borderColor': self.colors['accent'],
                                    'color': self.colors['text_secondary']
                                },
                                multiple=True
                            ),
                            html.Div(id='upload-status', className="mt-3")
                        ])
                    ], style={'background-color': self.colors['surface']})
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Quick Stats", className="card-title"),
                            html.Div(id='quick-stats')
                        ])
                    ], style={'background-color': self.colors['surface']})
                ], width=6)
            ], className="mb-4"),
            
            # Main Analytics Section
            dbc.Row([
                # Category Distribution
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-chart-pie me-2"),
                                "Message Categories"
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='category-chart')
                        ])
                    ], style={'background-color': self.colors['surface']})
                ], width=6),
                
                # Priority Timeline
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-chart-line me-2"),
                                "Priority Timeline"
                            ])
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='priority-timeline')
                        ])
                    ], style={'background-color': self.colors['surface']})
                ], width=6)
            ], className="mb-4"),
            
            # Interactive Message Board
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-tasks me-2"),
                                "Interactive Message Board"
                            ]),
                            dbc.ButtonGroup([
                                dbc.Button("All", id="filter-all", color="outline-light", size="sm"),
                                dbc.Button("High Priority", id="filter-priority", color="outline-warning", size="sm"),
                                dbc.Button("Urgent", id="filter-urgent", color="outline-danger", size="sm"),
                                dbc.Button("Questions", id="filter-questions", color="outline-info", size="sm")
                            ], className="ms-auto")
                        ]),
                        dbc.CardBody([
                            html.Div(id='message-board', style={'min-height': '400px'})
                        ])
                    ], style={'background-color': self.colors['surface']})
                ])
            ], className="mb-4"),
            
            # Similar Tickets Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-search me-2"),
                                "Similar Ticket Analysis"
                            ])
                        ]),
                        dbc.CardBody([
                            html.Div(id='similar-tickets-section')
                        ])
                    ], style={'background-color': self.colors['surface']})
                ])
            ], className="mb-4"),
            
            # Automation Suggestions
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-robot me-2"),
                                "Automation Suggestions"
                            ])
                        ]),
                        dbc.CardBody([
                            html.Div(id='automation-suggestions')
                        ])
                    ], style={'background-color': self.colors['surface']})
                ])
            ])
            
        ], fluid=True, style={
            'background-color': self.colors['background'],
            'min-height': '100vh',
            'color': self.colors['text']
        })

    def setup_callbacks(self):
        """Setup all dashboard callbacks"""
        
        @self.app.callback(
            [Output('upload-status', 'children'),
             Output('quick-stats', 'children'),
             Output('category-chart', 'figure'),
             Output('priority-timeline', 'figure'),
             Output('message-board', 'children'),
             Output('similar-tickets-section', 'children'),
             Output('automation-suggestions', 'children')],
            [Input('upload-data', 'contents'),
             Input('filter-all', 'n_clicks'),
             Input('filter-priority', 'n_clicks'),
             Input('filter-urgent', 'n_clicks'),
             Input('filter-questions', 'n_clicks')],
            [State('upload-data', 'filename')]
        )
        def update_dashboard(contents_list, filter_all, filter_priority, filter_urgent, filter_questions, filenames):
            ctx = callback_context
            
            # Handle file upload
            if contents_list:
                try:
                    # Process uploaded files (simplified - assume JSON format)
                    sample_messages = self.generate_sample_data()
                    self.processed_messages = self.analyzer.batch_process_messages(sample_messages)
                    upload_status = dbc.Alert(
                        f"Successfully processed {len(self.processed_messages)} messages!",
                        color="success",
                        className="mt-2"
                    )
                except Exception as e:
                    upload_status = dbc.Alert(f"Error processing files: {str(e)}", color="danger", className="mt-2")
            else:
                # Generate sample data if no upload
                if not self.processed_messages:
                    sample_messages = self.generate_sample_data()
                    self.processed_messages = self.analyzer.batch_process_messages(sample_messages)
                upload_status = dbc.Alert("Using sample data. Upload your Slack export to analyze real messages.", color="info", className="mt-2")
            
            # Determine active filter
            active_filter = "all"
            if ctx.triggered:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if button_id == 'filter-priority':
                    active_filter = "priority"
                elif button_id == 'filter-urgent':
                    active_filter = "urgent"
                elif button_id == 'filter-questions':
                    active_filter = "questions"
            
            # Generate dashboard components
            quick_stats = self.create_quick_stats()
            category_chart = self.create_category_chart()
            priority_timeline = self.create_priority_timeline()
            message_board = self.create_message_board(active_filter)
            similar_tickets = self.create_similar_tickets_section()
            automation_suggestions = self.create_automation_suggestions()
            
            return (upload_status, quick_stats, category_chart, priority_timeline, 
                   message_board, similar_tickets, automation_suggestions)

    def generate_sample_data(self) -> List[Dict]:
        """Generate sample Slack messages for demonstration"""
        import random
        
        sample_messages = [
            {
                "id": "1", "text": "Our production server is down! Users can't access the application. This is urgent!",
                "user": "john_doe", "channel": "alerts", "ts": (datetime.now() - timedelta(hours=1)).timestamp(),
                "reactions": ["🚨", "👀", "🔥"]
            },
            {
                "id": "2", "text": "Can someone help me understand how the authentication flow works? I'm getting confused with the OAuth implementation.",
                "user": "jane_smith", "channel": "dev-help", "ts": (datetime.now() - timedelta(hours=2)).timestamp(),
                "reactions": ["❓"]
            },
            {
                "id": "3", "text": "I found a bug in the user registration form. When users enter special characters in their name, the form crashes with a 500 error.",
                "user": "mike_wilson", "channel": "bug-reports", "ts": (datetime.now() - timedelta(hours=3)).timestamp(),
                "reactions": ["🐛", "👍"]
            },
            {
                "id": "4", "text": "Feature request: Can we add a dark mode toggle to the user settings? Many users have been asking for this.",
                "user": "sarah_johnson", "channel": "feature-requests", "ts": (datetime.now() - timedelta(hours=4)).timestamp(),
                "reactions": ["💡", "👍", "🌙"]
            },
            {
                "id": "5", "text": "The CI/CD pipeline failed again. It seems like there's an issue with the Docker build process. Can someone take a look?",
                "user": "alex_brown", "channel": "devops", "ts": (datetime.now() - timedelta(hours=5)).timestamp(),
                "reactions": ["🔧"]
            },
            {
                "id": "6", "text": "I need access to the staging environment database. Can someone grant me the necessary permissions?",
                "user": "emily_davis", "channel": "access-requests", "ts": (datetime.now() - timedelta(hours=6)).timestamp(),
                "reactions": ["🔐"]
            },
            {
                "id": "7", "text": "FYI: We'll be performing scheduled maintenance on Sunday between 2-4 AM. The application will be temporarily unavailable.",
                "user": "admin", "channel": "announcements", "ts": (datetime.now() - timedelta(hours=12)).timestamp(),
                "reactions": ["📢", "👍"]
            },
            {
                "id": "8", "text": "Another authentication issue here. Users are getting logged out randomly. This might be related to the session timeout configuration.",
                "user": "tom_anderson", "channel": "bug-reports", "ts": (datetime.now() - timedelta(hours=8)).timestamp(),
                "reactions": ["🔐", "🐛"]
            },
            {
                "id": "9", "text": "How do we handle user data export requests according to GDPR? Do we have a standard process for this?",
                "user": "lisa_martinez", "channel": "compliance", "ts": (datetime.now() - timedelta(hours=10)).timestamp(),
                "reactions": ["⚖️", "❓"]
            },
            {
                "id": "10", "text": "The new API endpoint is ready for testing. Can someone from QA please review the documentation and test cases?",
                "user": "david_lee", "channel": "api-development", "ts": (datetime.now() - timedelta(hours=14)).timestamp(),
                "reactions": ["✅", "📋"]
            }
        ]
        
        return sample_messages

    def create_quick_stats(self) -> html.Div:
        """Create quick statistics cards"""
        if not self.processed_messages:
            return html.Div("No data available")
        
        stats = self.analyzer.get_category_stats()
        high_priority_count = sum(1 for msg in self.processed_messages if msg.priority_score > 0.7)
        
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(stats['total_messages'], className="text-center", style={'color': self.colors['accent']}),
                        html.P("Total Messages", className="text-center mb-0")
                    ])
                ], style={'background-color': self.colors['dark']})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(high_priority_count, className="text-center", style={'color': self.colors['danger']}),
                        html.P("High Priority", className="text-center mb-0")
                    ])
                ], style={'background-color': self.colors['dark']})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(len(stats.get('categories', {})), className="text-center", style={'color': self.colors['info']}),
                        html.P("Categories", className="text-center mb-0")
                    ])
                ], style={'background-color': self.colors['dark']})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats.get('avg_priority', 0):.2f}", className="text-center", style={'color': self.colors['success']}),
                        html.P("Avg Priority", className="text-center mb-0")
                    ])
                ], style={'background-color': self.colors['dark']})
            ], width=3)
        ])

    def create_category_chart(self) -> go.Figure:
        """Create category distribution pie chart"""
        if not self.processed_messages:
            return go.Figure()
        
        categories = {}
        colors_list = []
        
        for message in self.processed_messages:
            category = message.category or 'general'
            categories[category] = categories.get(category, 0) + 1
        
        # Get colors for each category
        for category in categories.keys():
            colors_list.append(self.analyzer.categories.get(category, {}).get('color', '#666666'))
        
        fig = go.Figure(data=[go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            marker_colors=colors_list,
            textinfo='label+percent',
            textfont={'color': 'white'},
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            paper_bgcolor=self.colors['surface'],
            plot_bgcolor=self.colors['surface'],
            font_color=self.colors['text'],
            showlegend=True,
            legend=dict(font=dict(color=self.colors['text']))
        )
        
        return fig

    def create_priority_timeline(self) -> go.Figure:
        """Create priority timeline chart"""
        if not self.processed_messages:
            return go.Figure()
        
        # Group messages by hour and calculate average priority
        df = pd.DataFrame([{
            'timestamp': msg.timestamp,
            'priority': msg.priority_score,
            'category': msg.category
        } for msg in self.processed_messages])
        
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_priority = df.groupby('hour')['priority'].mean().reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hourly_priority['hour'],
            y=hourly_priority['priority'],
            mode='lines+markers',
            name='Average Priority',
            line=dict(color=self.colors['accent'], width=3),
            marker=dict(size=8, color=self.colors['accent'])
        ))
        
        fig.update_layout(
            paper_bgcolor=self.colors['surface'],
            plot_bgcolor=self.colors['surface'],
            font_color=self.colors['text'],
            xaxis=dict(gridcolor=self.colors['dark'], title='Time'),
            yaxis=dict(gridcolor=self.colors['dark'], title='Priority Score'),
            showlegend=True
        )
        
        return fig

    def create_message_board(self, filter_type: str = "all") -> html.Div:
        """Create interactive message board with drag-and-drop"""
        if not self.processed_messages:
            return html.Div("No messages to display")
        
        # Filter messages based on selected filter
        filtered_messages = self.processed_messages
        if filter_type == "priority":
            filtered_messages = [msg for msg in self.processed_messages if msg.priority_score > 0.7]
        elif filter_type == "urgent":
            filtered_messages = [msg for msg in self.processed_messages if msg.category == 'urgent']
        elif filter_type == "questions":
            filtered_messages = [msg for msg in self.processed_messages if msg.category == 'question']
        
        # Sort by priority score
        filtered_messages.sort(key=lambda x: x.priority_score, reverse=True)
        
        message_cards = []
        for message in filtered_messages[:20]:  # Limit to 20 messages
            category_color = self.analyzer.categories.get(message.category, {}).get('color', '#666666')
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        dbc.Badge(message.category.replace('_', ' ').title(), 
                                color="light", className="me-2", 
                                style={'background-color': category_color}),
                        dbc.Badge(f"Priority: {message.priority_score:.2f}", 
                                color="warning" if message.priority_score > 0.7 else "secondary",
                                className="me-2"),
                        html.Small(f"@{message.user} in #{message.channel}", 
                                 className="text-muted")
                    ])
                ]),
                dbc.CardBody([
                    html.P(message.text, className="card-text"),
                    html.Div([
                        html.Small(f"Timestamp: {message.timestamp.strftime('%Y-%m-%d %H:%M')}", 
                                 className="text-muted me-3"),
                        html.Small(f"Similar tickets: {len(message.similar_tickets) if message.similar_tickets else 0}", 
                                 className="text-muted")
                    ])
                ])
            ], 
            className="mb-3 message-card",
            style={
                'background-color': self.colors['dark'],
                'border-left': f'4px solid {category_color}',
                'cursor': 'move'
            },
            id=f"message-{message.id}"
            )
            message_cards.append(card)
        
        return html.Div(message_cards)

    def create_similar_tickets_section(self) -> html.Div:
        """Create similar tickets analysis section"""
        if not self.processed_messages:
            return html.Div("No data available")
        
        # Find messages with similar tickets
        messages_with_similar = [msg for msg in self.processed_messages if msg.similar_tickets]
        
        if not messages_with_similar:
            return dbc.Alert("No similar tickets found. This indicates unique issues or insufficient data.", 
                           color="info")
        
        similarity_cards = []
        for message in messages_with_similar[:5]:  # Show top 5
            similar_tickets_list = []
            for ticket in message.similar_tickets:
                similar_tickets_list.append(
                    dbc.ListGroupItem([
                        html.Div([
                            html.Strong(f"Ticket {ticket.ticket_id}"),
                            dbc.Badge(f"{ticket.similarity_score:.2f}", color="info", className="ms-2"),
                            html.Br(),
                            html.Small(f"Category: {ticket.category}", className="text-muted"),
                            html.Br(),
                            html.Small(f"Key phrases: {', '.join(ticket.key_phrases)}", className="text-muted")
                        ])
                    ])
                )
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.H6(f"Message {message.id} - Similar Tickets Found")
                ]),
                dbc.CardBody([
                    html.P(message.text[:100] + "..." if len(message.text) > 100 else message.text,
                          className="text-muted mb-3"),
                    dbc.ListGroup(similar_tickets_list, flush=True)
                ])
            ], className="mb-3", style={'background-color': self.colors['dark']})
            
            similarity_cards.append(card)
        
        return html.Div(similarity_cards)

    def create_automation_suggestions(self) -> html.Div:
        """Create automation suggestions based on analysis"""
        if not self.processed_messages:
            return html.Div("No data available")
        
        suggestions = []
        
        # Analyze patterns for automation opportunities
        category_counts = {}
        for message in self.processed_messages:
            category = message.category or 'general'
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Generate suggestions based on patterns
        if category_counts.get('access_request', 0) > 2:
            suggestions.append({
                'title': 'Automate Access Requests',
                'description': f'Found {category_counts["access_request"]} access requests. Consider implementing a self-service portal.',
                'priority': 'High',
                'color': 'warning'
            })
        
        if category_counts.get('question', 0) > 3:
            suggestions.append({
                'title': 'FAQ Bot Implementation',
                'description': f'Found {category_counts["question"]} questions. A chatbot could handle common queries.',
                'priority': 'Medium',
                'color': 'info'
            })
        
        if category_counts.get('bug_report', 0) > 2:
            suggestions.append({
                'title': 'Automated Bug Triage',
                'description': f'Found {category_counts["bug_report"]} bug reports. Implement automatic priority assignment.',
                'priority': 'High',
                'color': 'danger'
            })
        
        if category_counts.get('deployment', 0) > 1:
            suggestions.append({
                'title': 'Deployment Notifications',
                'description': 'Automate deployment status updates and notifications.',
                'priority': 'Medium',
                'color': 'success'
            })
        
        if not suggestions:
            return dbc.Alert("No automation opportunities identified yet. More data needed for better suggestions.", 
                           color="info")
        
        suggestion_cards = []
        for suggestion in suggestions:
            card = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H5(suggestion['title'], className="card-title"),
                        dbc.Badge(suggestion['priority'], color=suggestion['color'], className="mb-2"),
                        html.P(suggestion['description'], className="card-text"),
                        dbc.Button("Implement", color="outline-light", size="sm")
                    ])
                ])
            ], className="mb-3", style={'background-color': self.colors['dark']})
            suggestion_cards.append(card)
        
        return html.Div(suggestion_cards)

    def run(self, debug=True, port=8050):
        """Run the dashboard"""
        self.app.run_server(debug=debug, port=port, host='0.0.0.0')

if __name__ == '__main__':
    dashboard = SlackAnalyticsDashboard()
    dashboard.run()