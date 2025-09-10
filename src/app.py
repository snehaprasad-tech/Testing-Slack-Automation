#!/usr/bin/env python3
"""
Slack Message Analytics Dashboard
Main application entry point
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard import SlackAnalyticsDashboard
from message_analyzer import MessageAnalyzer

def setup_logging(log_level="INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('slack_analytics.log')
        ]
    )

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Slack Message Analytics Dashboard')
    parser.add_argument('--port', type=int, default=8050, help='Port to run the dashboard on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set the logging level')
    parser.add_argument('--data-dir', type=str, default='data', help='Directory containing Slack export data')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Slack Message Analytics Dashboard...")
    logger.info(f"Dashboard will be available at: http://localhost:{args.port}")
    
    try:
        # Create data directory if it doesn't exist
        data_dir = Path(args.data_dir)
        data_dir.mkdir(exist_ok=True)
        
        # Initialize and run the dashboard
        dashboard = SlackAnalyticsDashboard()
        
        # Check if there are any data files to pre-load
        json_files = list(data_dir.glob('*.json'))
        if json_files:
            logger.info(f"Found {len(json_files)} JSON files in data directory")
            # TODO: Pre-load data files
        
        logger.info("Dashboard initialized successfully")
        dashboard.run(debug=args.debug, port=args.port)
        
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()