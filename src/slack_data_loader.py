"""
Slack Data Loader
Utilities for loading and processing Slack export data
"""

import json
import os
import zipfile
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import logging

class SlackDataLoader:
    """Load and process Slack export data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_from_export(self, export_path: str) -> List[Dict]:
        """Load messages from Slack export file or directory"""
        messages = []
        
        if os.path.isfile(export_path):
            if export_path.endswith('.zip'):
                messages = self._load_from_zip(export_path)
            elif export_path.endswith('.json'):
                messages = self._load_from_json(export_path)
            else:
                raise ValueError("Unsupported file format. Use .zip or .json files.")
        elif os.path.isdir(export_path):
            messages = self._load_from_directory(export_path)
        else:
            raise FileNotFoundError(f"Path not found: {export_path}")
        
        self.logger.info(f"Loaded {len(messages)} messages from {export_path}")
        return messages
    
    def _load_from_zip(self, zip_path: str) -> List[Dict]:
        """Load messages from Slack export ZIP file"""
        messages = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Look for channel directories and JSON files
            for file_info in zip_file.filelist:
                if file_info.filename.endswith('.json') and '/' in file_info.filename:
                    channel_name = file_info.filename.split('/')[0]
                    
                    try:
                        with zip_file.open(file_info.filename) as json_file:
                            data = json.load(json_file)
                            
                            for message in data:
                                if isinstance(message, dict) and 'text' in message:
                                    message['channel'] = channel_name
                                    messages.append(message)
                    
                    except Exception as e:
                        self.logger.warning(f"Error loading {file_info.filename}: {e}")
        
        return messages
    
    def _load_from_json(self, json_path: str) -> List[Dict]:
        """Load messages from single JSON file"""
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'messages' in data:
            return data['messages']
        else:
            raise ValueError("Invalid JSON format. Expected list of messages or object with 'messages' key.")
    
    def _load_from_directory(self, dir_path: str) -> List[Dict]:
        """Load messages from directory containing JSON files"""
        messages = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    channel_name = os.path.basename(root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as json_file:
                            data = json.load(json_file)
                            
                            if isinstance(data, list):
                                for message in data:
                                    if isinstance(message, dict) and 'text' in message:
                                        message['channel'] = channel_name
                                        messages.append(message)
                    
                    except Exception as e:
                        self.logger.warning(f"Error loading {file_path}: {e}")
        
        return messages
    
    def preprocess_messages(self, messages: List[Dict]) -> List[Dict]:
        """Preprocess and clean message data"""
        processed_messages = []
        
        for message in messages:
            try:
                # Skip messages without text or system messages
                if not message.get('text') or message.get('subtype') in ['bot_message', 'channel_join', 'channel_leave']:
                    continue
                
                # Ensure required fields exist
                processed_message = {
                    'id': message.get('client_msg_id', message.get('ts', str(hash(message.get('text', ''))))),
                    'text': message.get('text', ''),
                    'user': message.get('user', 'unknown'),
                    'channel': message.get('channel', 'general'),
                    'ts': message.get('ts', datetime.now().timestamp()),
                    'thread_ts': message.get('thread_ts'),
                    'reactions': self._extract_reactions(message.get('reactions', []))
                }
                
                processed_messages.append(processed_message)
                
            except Exception as e:
                self.logger.warning(f"Error processing message: {e}")
                continue
        
        return processed_messages
    
    def _extract_reactions(self, reactions: List[Dict]) -> List[str]:
        """Extract reaction names from reactions data"""
        if not reactions:
            return []
        
        reaction_names = []
        for reaction in reactions:
            if isinstance(reaction, dict) and 'name' in reaction:
                reaction_names.append(reaction['name'])
        
        return reaction_names
    
    def save_processed_data(self, messages: List[Dict], output_path: str):
        """Save processed messages to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(messages, file, indent=2, default=str)
        
        self.logger.info(f"Saved {len(messages)} processed messages to {output_path}")
    
    def create_sample_export(self, output_path: str):
        """Create a sample Slack export file for testing"""
        sample_data = {
            "channels": [
                {"id": "C1234567890", "name": "general", "created": 1234567890},
                {"id": "C1234567891", "name": "dev-help", "created": 1234567890},
                {"id": "C1234567892", "name": "bug-reports", "created": 1234567890}
            ],
            "users": [
                {"id": "U1234567890", "name": "john_doe", "real_name": "John Doe"},
                {"id": "U1234567891", "name": "jane_smith", "real_name": "Jane Smith"},
                {"id": "U1234567892", "name": "mike_wilson", "real_name": "Mike Wilson"}
            ],
            "messages": [
                {
                    "client_msg_id": "sample-1",
                    "type": "message",
                    "text": "Our production server is down! This is critical!",
                    "user": "U1234567890",
                    "ts": "1640995200.000100",
                    "channel": "C1234567890",
                    "reactions": [{"name": "fire", "count": 3}]
                },
                {
                    "client_msg_id": "sample-2", 
                    "type": "message",
                    "text": "Can someone help me understand the authentication flow?",
                    "user": "U1234567891",
                    "ts": "1640995300.000100",
                    "channel": "C1234567891",
                    "reactions": [{"name": "question", "count": 1}]
                },
                {
                    "client_msg_id": "sample-3",
                    "type": "message", 
                    "text": "Found a bug in the user registration form. Getting 500 errors.",
                    "user": "U1234567892",
                    "ts": "1640995400.000100",
                    "channel": "C1234567892",
                    "reactions": [{"name": "bug", "count": 2}]
                }
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(sample_data, file, indent=2)
        
        self.logger.info(f"Created sample export file: {output_path}")

def main():
    """CLI interface for data loader"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load and process Slack export data')
    parser.add_argument('input_path', help='Path to Slack export file or directory')
    parser.add_argument('--output', '-o', help='Output file path for processed data')
    parser.add_argument('--create-sample', action='store_true', help='Create sample export file')
    
    args = parser.parse_args()
    
    loader = SlackDataLoader()
    
    if args.create_sample:
        loader.create_sample_export(args.input_path)
        return
    
    try:
        messages = loader.load_from_export(args.input_path)
        processed_messages = loader.preprocess_messages(messages)
        
        if args.output:
            loader.save_processed_data(processed_messages, args.output)
        else:
            print(f"Loaded and processed {len(processed_messages)} messages")
            for i, msg in enumerate(processed_messages[:5]):
                print(f"{i+1}. [{msg['channel']}] {msg['user']}: {msg['text'][:50]}...")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()