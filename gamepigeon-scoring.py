#!/usr/bin/env python3
"""
GamePigeon Results Analyzer

This script analyzes text messages exported from iMessage containing GamePigeon game results
and counts the number of wins, losses, and draws for the user.
"""

import re
from datetime import datetime
import argparse


def parse_gamepigeon_results(filename):
    """
    Parse a text file containing iMessage exports and extract GamePigeon results.
    
    Args:
        filename (str): Path to the text file with iMessage exports
        
    Returns:
        dict: Dictionary with counts for wins, losses, and draws
    """
    # Initialize counters
    results = {
        'wins': 0,
        'losses': 0,
        'draws': 0
    }
    
    # Track who sent each message
    current_sender = None
    gamepigeon_flag = False
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Check if this is a timestamp line (indicates new message)
                timestamp_match = re.match(r"\w{3}\s\d{1,2},\s\d{4}\s+\d{1,2}:\d{2}:\d{2}\s[AP]M", line)
                if not timestamp_match:
                    timestamp_match = re.match(r"\w{3}\s\d{1,2},\s\d{4}\s\s\d{1,2}:\d{2}:\d{2}\s[AP]M", line)
                
                if timestamp_match and i+1 < len(lines):
                    # Next line should be the sender
                    current_sender = lines[i+1].strip()
                    gamepigeon_flag = False
                
                # Check for GamePigeon message indicator
                if line == "GamePigeon message:":
                    gamepigeon_flag = True
                    continue
                
                # Process result if we're looking at a line after GamePigeon message
                if gamepigeon_flag and i > 0:
                    if line == "I won!":
                        if current_sender == "Me":
                            results['wins'] += 1
                        else:
                            results['losses'] += 1
                        gamepigeon_flag = False
                    elif line == "You Won!":
                        if current_sender == "Me":
                            results['losses'] += 1
                        else:
                            results['wins'] += 1
                        gamepigeon_flag = False
                    elif line == "Draw!":
                        results['draws'] += 1
                        gamepigeon_flag = False
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
        
    return results


def main():
    parser = argparse.ArgumentParser(description='Analyze GamePigeon results from iMessage exports')
    parser.add_argument('file', help='Text file containing iMessage exports')
    
    args = parser.parse_args()
    
    print(f"Analyzing GamePigeon results from {args.file}...")
    results = parse_gamepigeon_results(args.file)
    
    if results:
        total_games = sum(results.values())
        win_percentage = (results['wins'] / total_games * 100) if total_games > 0 else 0
        
        print("\n📊 GamePigeon Results Summary 📊")
        print(f"Total games played: {total_games}")
        print(f"Wins: {results['wins']}")
        print(f"Losses: {results['losses']}")
        print(f"Draws: {results['draws']}")
        print(f"Win percentage: {win_percentage:.1f}%")


if __name__ == "__main__":
    main()