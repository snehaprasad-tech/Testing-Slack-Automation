# Slack Message Analytics Dashboard

An intelligent, interactive dashboard for analyzing Slack messages, categorizing them automatically, and finding similar tickets to help with automation and prioritization.

## 🚀 Features

### Core Analytics
- **Automatic Message Categorization**: Uses NLP to classify messages into categories like bug reports, feature requests, questions, urgent issues, etc.
- **Priority Scoring**: Intelligent priority scoring based on keywords, urgency indicators, and context
- **Similar Ticket Matching**: Finds similar messages using semantic similarity and fuzzy matching
- **Real-time Processing**: Processes messages in real-time with batch processing capabilities

### Interactive Dashboard
- **Modern UI**: Dark theme with contrasting colors for better visibility
- **Drag & Drop Interface**: Interactive message cards that can be dragged and reorganized
- **Dynamic Filtering**: Filter messages by priority, category, or custom criteria
- **Visual Analytics**: Charts and graphs showing category distribution and priority trends

### Automation Insights
- **Pattern Recognition**: Identifies recurring patterns and suggests automation opportunities
- **Workflow Optimization**: Recommends process improvements based on message analysis
- **Priority Management**: Helps identify which issues need immediate attention

## 🎨 Visual Design

The dashboard features a modern dark theme with carefully chosen contrasting colors:
- **Background**: Deep dark theme (#1A1A1A) for reduced eye strain
- **Accent Colors**: Vibrant oranges (#F39C12) and blues (#3498DB) for highlights
- **Category Colors**: Distinct colors for each message category
- **Interactive Elements**: Smooth animations and hover effects

## 📋 Categories

The system automatically categorizes messages into:

| Category | Color | Description |
|----------|-------|-------------|
| 🐛 Bug Report | Red (#FF6B6B) | Error reports, crashes, issues |
| ✨ Feature Request | Teal (#4ECDC4) | Enhancement requests, new features |
| ❓ Question | Blue (#45B7D1) | Help requests, clarifications |
| 🚨 Urgent | Bright Red (#FF4757) | Critical issues, production problems |
| 🚀 Deployment | Orange (#FFA726) | Release notes, CI/CD issues |
| 🔐 Access Request | Purple (#AB47BC) | Permission requests, login issues |
| 📢 General | Green (#66BB6A) | Announcements, updates, FYI |

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd slack-message-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   python src/app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8050`

### Advanced Installation

For development or custom configurations:

```bash
# Install in development mode
pip install -e .

# Run with custom port and debug mode
python src/app.py --port 8080 --debug --log-level DEBUG

# Create sample data for testing
python src/slack_data_loader.py sample_data.json --create-sample
```

## 📊 Usage

### Data Input Methods

1. **Upload Slack Export**
   - Export your Slack workspace data
   - Drag and drop the ZIP file into the dashboard
   - The system will automatically process and analyze the messages

2. **JSON Files**
   - Upload individual JSON files containing message data
   - Support for both single files and batch uploads

3. **Sample Data**
   - The dashboard includes sample data for demonstration
   - Perfect for testing and understanding the features

### Dashboard Sections

#### 1. **Upload & Quick Stats**
- File upload area with drag-and-drop support
- Real-time statistics showing message counts and priorities

#### 2. **Visual Analytics**
- **Category Chart**: Pie chart showing message distribution
- **Priority Timeline**: Line chart showing priority trends over time

#### 3. **Interactive Message Board**
- Drag-and-drop message cards
- Filter buttons for different views
- Color-coded priority indicators

#### 4. **Similar Ticket Analysis**
- Shows messages with similar content
- Similarity scores and key phrase extraction
- Helps identify recurring issues

#### 5. **Automation Suggestions**
- AI-powered recommendations for process automation
- Priority-based suggestions for workflow improvements

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Dashboard Configuration
DASH_PORT=8050
DASH_DEBUG=True
LOG_LEVEL=INFO

# Data Processing
MAX_MESSAGES=10000
SIMILARITY_THRESHOLD=0.3
CATEGORY_CONFIDENCE_THRESHOLD=0.5

# NLP Configuration
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
ENABLE_GPU=False
```

### Custom Categories

Modify `src/message_analyzer.py` to add custom categories:

```python
self.categories['custom_category'] = {
    'keywords': ['custom', 'keyword'],
    'patterns': [r'custom.*pattern'],
    'color': '#CUSTOM_COLOR'
}
```

## 📈 API Reference

### MessageAnalyzer Class

```python
from src.message_analyzer import MessageAnalyzer

analyzer = MessageAnalyzer()

# Process a single message
message = analyzer.process_message(message_data)

# Batch process messages
messages = analyzer.batch_process_messages(messages_list)

# Get statistics
stats = analyzer.get_category_stats()
```

### SlackDataLoader Class

```python
from src.slack_data_loader import SlackDataLoader

loader = SlackDataLoader()

# Load from Slack export
messages = loader.load_from_export('export.zip')

# Preprocess messages
processed = loader.preprocess_messages(messages)
```

## 🚀 Advanced Features

### Custom Filters
Add custom filtering logic by extending the dashboard:

```python
def custom_filter(messages, criteria):
    return [msg for msg in messages if criteria(msg)]
```

### Export Functionality
Export processed data in multiple formats:

```python
# JSON export
json_data = analyzer.export_data('json')

# CSV export
csv_data = analyzer.export_data('csv')
```

### Integration with Other Tools
The dashboard can be integrated with:
- Slack Bot APIs
- Ticketing systems (Jira, ServiceNow)
- Monitoring tools (Grafana, DataDog)
- CI/CD pipelines

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_message_analyzer.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please:
1. Check the [Issues](issues) page for known problems
2. Create a new issue with detailed information
3. Include logs and error messages when reporting bugs

## 🔮 Roadmap

### Upcoming Features
- [ ] Real-time Slack integration
- [ ] Machine learning model training
- [ ] Custom dashboard themes
- [ ] Mobile responsive design
- [ ] Advanced analytics and reporting
- [ ] Integration with ticketing systems
- [ ] Automated response suggestions
- [ ] Team performance analytics

### Version History
- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Enhanced UI and drag-and-drop features
- **v1.2.0**: Advanced similarity matching and automation suggestions

---

Made with ❤️ for better Slack workflow management