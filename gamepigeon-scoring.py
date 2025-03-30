#!/usr/bin/env python3
"""
GamePigeon Results Analyzer
This script analyzes text messages exported from iMessage containing GamePigeon game results,
counts the number of wins, losses, and draws for the user, and plots them over time.
"""
import re
from datetime import datetime
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

def parse_gamepigeon_results(filename):
    """
    Parse a text file containing iMessage exports and extract GamePigeon results.
    
    Args:
        filename (str): Path to the text file with iMessage exports
        
    Returns:
        dict: Dictionary with counts for wins, losses, and draws, and lists of timestamped results
    """
    # Initialize counters
    results = {
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'timestamped_results': []  # List to store [timestamp, result] pairs
    }
    
    # Track who sent each message
    current_sender = None
    gamepigeon_flag = False
    current_timestamp = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Check if this is a timestamp line (indicates new message)
                timestamp_match = re.match(r"(\w{3}\s\d{1,2},\s\d{4})\s+(\d{1,2}:\d{2}:\d{2}\s[AP]M)", line)
                if not timestamp_match:
                    timestamp_match = re.match(r"(\w{3}\s\d{1,2},\s\d{4})\s\s(\d{1,2}:\d{2}:\d{2}\s[AP]M)", line)
                
                if timestamp_match and i+1 < len(lines):
                    # Parse the timestamp
                    date_str = timestamp_match.group(1)
                    time_str = timestamp_match.group(2)
                    timestamp_str = f"{date_str} {time_str}"
                    try:
                        current_timestamp = datetime.strptime(timestamp_str, "%b %d, %Y %I:%M:%S %p")
                    except ValueError:
                        # If parsing fails, try another format
                        try:
                            current_timestamp = datetime.strptime(timestamp_str, "%a %d, %Y %I:%M:%S %p")
                        except ValueError:
                            current_timestamp = None
                    
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
                            if current_timestamp:
                                results['timestamped_results'].append([current_timestamp, 'win'])
                        else:
                            results['losses'] += 1
                            if current_timestamp:
                                results['timestamped_results'].append([current_timestamp, 'loss'])
                        gamepigeon_flag = False
                    elif line == "You Won!":
                        if current_sender == "Me":
                            results['losses'] += 1
                            if current_timestamp:
                                results['timestamped_results'].append([current_timestamp, 'loss'])
                        else:
                            results['wins'] += 1
                            if current_timestamp:
                                results['timestamped_results'].append([current_timestamp, 'win'])
                        gamepigeon_flag = False
                    elif line == "Draw!":
                        results['draws'] += 1
                        if current_timestamp:
                            results['timestamped_results'].append([current_timestamp, 'draw'])
                        gamepigeon_flag = False
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    # Sort results by timestamp
    results['timestamped_results'].sort(key=lambda x: x[0])
    
    return results

def plot_results_over_time(results):
    """
    Plot the game results over time.
    
    Args:
        results (dict): Dictionary with timestamped results
    """
    if not results['timestamped_results']:
        print("No timestamped results to plot.")
        return
    
    # Prepare data for plotting
    timestamps = [item[0] for item in results['timestamped_results']]
    result_types = [item[1] for item in results['timestamped_results']]
    
    # Calculate cumulative wins, losses, and draws
    cum_wins = []
    cum_losses = []
    cum_draws = []
    win_count = 0
    loss_count = 0
    draw_count = 0
    
    for result in result_types:
        if result == 'win':
            win_count += 1
        elif result == 'loss':
            loss_count += 1
        elif result == 'draw':
            draw_count += 1
        
        cum_wins.append(win_count)
        cum_losses.append(loss_count)
        cum_draws.append(draw_count)
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot cumulative results over time
    ax1.plot(timestamps, cum_wins, 'g-', label='Wins')
    ax1.plot(timestamps, cum_losses, 'r-', label='Losses')
    ax1.plot(timestamps, cum_draws, 'b-', label='Draws')
    ax1.set_title('Cumulative GamePigeon Results Over Time')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Count')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Format the x-axis to show dates nicely
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    
    # Calculate win percentage over time (using a sliding window of 5 games)
    window_size = min(5, len(result_types))
    win_percentages = []
    dates = []
    
    if len(result_types) >= window_size:
        for i in range(len(result_types) - window_size + 1):
            window = result_types[i:i+window_size]
            win_count = window.count('win')
            win_percentage = (win_count / window_size) * 100
            win_percentages.append(win_percentage)
            dates.append(timestamps[i + window_size - 1])
    
        # Plot win percentage over time
        ax2.plot(dates, win_percentages, 'o-', color='purple')
        ax2.set_title(f'Win Percentage (Sliding Window of {window_size} Games)')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Win Percentage (%)')
        ax2.set_ylim([0, 100])
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_locator(MaxNLocator(11))  # 0, 10, 20, ..., 100
    else:
        ax2.text(0.5, 0.5, f'Need at least {window_size} games to calculate win percentage',
                horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)
    
    plt.tight_layout()
    plt.savefig('gamepigeon_results.png')
    print("Plot saved as 'gamepigeon_results.png'")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze GamePigeon results from iMessage exports')
    parser.add_argument('file', help='Text file containing iMessage exports')
    args = parser.parse_args()
    
    print(f"Analyzing GamePigeon results from {args.file}...")
    results = parse_gamepigeon_results(args.file)
    
    if results:
        total_games = sum([results['wins'], results['losses'], results['draws']])
        win_percentage = (results['wins'] / total_games * 100) if total_games > 0 else 0
        
        print("\n📊 GamePigeon Results Summary 📊")
        print(f"Total games played: {total_games}")
        print(f"Wins: {results['wins']}")
        print(f"Losses: {results['losses']}")
        print(f"Draws: {results['draws']}")
        print(f"Win percentage: {win_percentage:.1f}%")
        print(f"Loss percentage: {(results['losses'] / total_games * 100) if total_games > 0 else 0:.1f}%")
        print(f"Draw percentage: {(results['draws'] / total_games * 100) if total_games > 0 else 0:.1f}%")
        
        # Plot results over time
        if total_games > 0:
            print("\nGenerating timeline plot...")
            plot_results_over_time(results)

if __name__ == "__main__":
    main()