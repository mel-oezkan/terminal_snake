import json
import pathlib
from pydoc import source_synopsis
from typing import List
from datetime import datetime

from config import LeaderboardItem


def load_settings():
    settings_path = pathlib.Path("settings.json").absolute()

    data: dict = {}
    if settings_path.exists() and settings_path.stat().st_size > 0:
        try:
            with open(settings_path, "r") as source:
                data = json.load(source)
        except:
            # It can happen that the write process fails 
            return {}

    return data


def write_settings(new_data: dict):
    with open("settings.json", "w") as source:
        json.dump(new_data, source, indent=3)


def read_leaderboard() -> dict:
    """Reads and returns the data contained in the leaderboard file
    
    Additionally checks if the file exists and returns an empty list
    if it does not or doen't contain any information

    :returns list containing the leaderboard items
    """
    file_path = pathlib.Path("leaderboard.json")
    
    if file_path.exists() and file_path.stat().st_size > 1:
        with open("leaderboard.json", "r") as source:
            score_data = json.load(source)
            return score_data

    return []


def add_score(
    leaderboard_list: List[LeaderboardItem], 
    leaderboard_item: LeaderboardItem
) -> List[LeaderboardItem]:
    """ Takes a new Leaderboard entry, adds it to the leaderboard 
    and additionally sorts the scores according to their score values
    
    :param leaderboard_list: liset of leaderboard items
    :param leaderboard_item: leaderboard item

    :returns sorted leaderboard with new item
    """

    expanded_leaderboard = leaderboard_list
    expanded_leaderboard.append(leaderboard_item)

    # sort the leaderboard items based on the score
    sorted_scores = sorted(
        expanded_leaderboard, 
        key=lambda item: item["score"]
    )

    return sorted_scores[::-1]
    

def write_score(game_score: dict) -> None:
    """ Given a new score item adds the item to the leaderboard
    on its respecitve position and writes the updated leaderboard
    
    :param game_score: dict containing the score of the snake game
    """

    time_now = datetime.now()
    time_str = time_now.strftime("%m/%d/%Y, %H:%M:%S")
    
    new_item: LeaderboardItem = {
        "time": time_str,
        "score": game_score["score"]
    }

    leaderboard: List[LeaderboardItem] = read_leaderboard()
    updated_leaderboard = add_score(leaderboard, new_item)

    with open("leaderboard.json", "w") as source:
        json.dump(updated_leaderboard, source, indent=3)
