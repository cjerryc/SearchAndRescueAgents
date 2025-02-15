'''
This Search Agent implements the Search Team Leader.
The Search Agent aims to produce 3 results:
1. Store and manage the retrieval of clues passed to it as a codex. If no additional information is given about the item found,
then an api call is made to give context of what it could possibly be in the context of Search and Rescue operations.
2. Keep track of the Date and Time of the search. The elapsed time since the search started is calculated and presented for users.
3. Keep track of distance searched by search radius. This is a simple distance tracker, with a rate tracing done over the elapsed time.

Note:
- Time is kept in ISO Universal Time (UTC) format, while elapsed time is kept in hours and minutes.
ex. "2025-02-15 08:30:38.173807+00:00"
- The class methods may be used for computation and presentation of the agent. Textual prints also post for users.
- Testing is done with a class made in test_search_agent.py
- The above three main functions of the agent are separated into the methods below.
'''

import google.generativeai as genai
from sar_project.agents.base_agent import SARBaseAgent
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import math

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SearchAgent(SARBaseAgent):
    def __init__(self, name="search_team_leader"):
        super().__init__(
            name=name,
            role="Search Team Leader",
            system_message="""You are a Search Team Leader for SAR operations. Your role is to:
            1. Conduct Ground Searches.
            2. Document Clues found in Search.
            3. Keep track of Area covered in elapsed time.
            4. Keep track of time to contact the persons of interest."""
        )
        # Clues found
        self.clues = {}
        self.cluesCount = 0
        # Search Time [DateTime Formatting]
        self.beginningSearchTime = datetime.now(timezone.utc)
        self.endSearchTime = None
        self.elapsedTime = None  # Stored as a tuple (Hours, Minutes)
        self.firstContactTime = None
        # Area covered
        self.searchRadius = 0.0
        self.area = 0.0
        self.areaCoverRate = 0.0  # (m^2/seconds)

    def query_gemini(self, prompt, model="gemini-pro", max_tokens=200):
        """Query Google Gemini API and return response."""
        try:
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"

    # Time Methods
    def get_time_difference(self, laterTime, earlierTime):
        # Convert to datetime objects
        dateTime_format = "%Y-%m-%d %H:%M:%S.%f%z"
        dateTime1 = datetime.strptime(laterTime, dateTime_format)
        dateTime2 = datetime.strptime(earlierTime, dateTime_format)

        # Calculate time difference
        time_delta = dateTime1 - dateTime2

        # Extract hours and minutes
        hours, remainder = divmod(time_delta.total_seconds(), 3600)
        minutes = remainder // 60

        print(f"Time elapsed: {int(hours)} hours and {int(minutes)} minutes")
        return (hours, minutes)

    def get_elapsed_search_time(self, currentTime):
        self.elapsedTime = self.get_time_difference(currentTime, self.beginningSearchTime)
        return self.elapsedTime

    def get_current_time(self):
        return datetime.now(timezone.utc)

    # Clue Methods
    def add_clue(self, item, information=None):
        if information:
            self.clues[item] = information
        else:
            queryResponse = ag.query_gemini(f"In the context of Search and Rescue, what could a found {item} mean?")
            self.clues[item] = queryResponse
        self.cluesCount += 1

    def remove_clue(self, item):
        if item in self.clues:
            del self.clues[item]
            self.cluesCount -= 1
            return True
        return False

    def get_clue(self, item):
        if item in self.clues:
            print(f"The found clue: {item} tells us: {self.clues[item]}.")
            return self.clues[item]
        else:
            return "This item does not appear to be a clue found yet."

    def update_search_radius(self, radius):
        self.searchRadius = radius

    def get_distance_covered(self):
        distanceCovered = math.pi * (self.searchRadius ** 2)
        print(f"Distance Covered so far: {distanceCovered}.")
        return distanceCovered

    def get_area_covered_by_time(self):
        currentTime = self.get_current_time()
        timeElapsed = self.get_elapsed_search_time(self, currentTime)
        self.areaCoverRate = self.get_distance_covered() / (timeElapsed[0] * 3600 + timeElapsed[1])
        print(f"The rate of distance being covered is: {self.areaCoverRate}.")
        return self.areaCoverRate

    def end_search(self):
        # Mark the duration of the search.
        self.endSearchTime = self.get_current_time()
        self.elapsedTime = self.get_elapsed_search_time(self.endSearchTime)
        print(f"The search started at {self.beginningSearchTime} and ended at {self.endSearchTime}, totaling a duration of {self.elapsedTime[0]} hours and {self.elapsedTime[1]} minutes.")

        # Note the number of clues found and what was found.
        print(f"The number of clues found during the search is {self.cluesCount}")

        # Find the amount of area covered to find the missing persons
        print(f"The rate of area covered during the search is {self.areaCoverRate} in (m^2/seconds).")

ag = SearchAgent()





