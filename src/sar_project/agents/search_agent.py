'''
This Search Agent implements the Search Agents associated with a Search Team Leader.
Each Search Agent is attached to a Search Team Leader, who essentially serves as a communication and location hub for the
Search Agents.
The Search Agent aims to produce 3 results:
1. Store and manage the retrieval of clues passed to it as a codex. If no additional information is given about the item found,
then an api call is made to give context of what it could possibly be in the context of Search and Rescue operations.
2. Keep track of the Date and Time of the search. The elapsed time since the search started is calculated and presented for users.
3. Keep track of distance searched by search radius. This is a simple distance tracker, with a rate tracing done over the elapsed time.

The Search Team Leader effectively does the following:
1. Allow for general terrain traversal strategy by LLM querying on terrain type, number of agents, agent locations.
2. Allow for inter-agent messaging between Search Agents.
3. Agent Registration with a leader.

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


class SearchTeamLeader:
    """Central leader managing SAR search agents, messages, and locations."""
    def __init__(self, name="search_team_leader"):
        self.messages = {}  # Stores messages for each agent
        self.terrain = "Unknown" # General description of the terrain (ex. forrest, desert, etc.)
        self.agent_locations = {}  # Stores locations for each agent
        self.agents = []
        self.numAgents = 0 # Keeps track of number of agents in the field

    # Communication between search agents
    def register_agent(self, agent_name):
        """Register a new agent with an inbox and location storage."""
        if agent_name in self.messages:
            raise ValueError(f"Agent '{agent_name}' is an already existing agent. Please choose another name.")
        self.messages[agent_name] = []
        self.agent_locations[agent_name] = "Location unknown"
        self.numAgents += 1
        self.agents.append(agent_name)
        print(f"Agent {agent_name} has been registered.")

    def send_message(self, sender, recipient, message):
        """Send a message between agents via the leader."""
        if recipient in self.messages:
            self.messages[recipient].append((sender, message))
            print(f"A message from agent {sender} has been sent to agnet {recipient}.")
        else:
            print(f"Agent {recipient} not found!")

    def receive_messages(self, agent_name):
        """Retrieve all messages for a specific agent."""
        if agent_name in self.messages:
            received = self.messages[agent_name]
            self.messages[agent_name] = []  # Clear inbox after retrieval
            return received
        else:
            print(f"Agent {agent_name} is not registered!")
            return []

    # Location bookkeeping
    def update_location(self, agent_name, latitude, longitude):
        """Update an agent's location."""
        if agent_name in self.agent_locations:
            self.agent_locations[agent_name] = (latitude, longitude)
            print(f"The location of Agent {agent_name} has been updated to {latitude, longitude}")
        else:
            print(f"Agent {agent_name} is not registered!")

    def get_location(self, agent_name):
        """Retrieve an agent's last known location."""
        if agent_name in self.agent_locations:
            return self.agent_locations.get(agent_name, "Location unknown")
        else:
            print(f"Agent {agent_name} is not registered!")
            return None

    def set_terrain(self, terrain):
        self.terrain = terrain

    def query_gemini(self, prompt, model="gemini-pro", max_tokens=200):
        """Query Google Gemini API and return response."""
        try:
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"

    def query_llm_for_strategy(self):
        prompt = f"""
        You are a team leader in Search and Rescue (SAR) operations. 
        Given the following information, provide an optimal search strategy:

        - **Terrain Type:** {self.terrain}
        - **Number of Agents:** {self.numAgents}
        - **Last Known Position of Agents:** {self.agent_locations}

        Suggest how agents should space out, key areas to prioritize, 
        and any considerations based on terrain conditions.
        """

        response = self.query_gemini(prompt)

        return response


class SearchAgent(SARBaseAgent):
    def __init__(self, name="search_agent", leader=None):
        super().__init__(
            name=name,
            role="Search Agent",
            system_message="""You are a Search Agent for SAR operations. Your role is to:
            1. Conduct Ground Searches.
            2. Document Clues found in Search.
            3. Keep track of Area covered in elapsed time.
            4. Keep track of time to contact the persons of interest."""
        )

        # Exception Handling: Ensure the leader is valid
        if leader is None:
            raise ValueError(f"Agent '{name}' must have a SearchTeamLeader assigned.")
        if not isinstance(leader, SearchTeamLeader):
            raise TypeError(f"Agent '{name}' received an invalid leader. Expected a SearchTeamLeader instance.")

        # Information for bookkeeping for Search Team Leader
        self.alias = name
        self.leader = leader
        self.leader.register_agent(self.alias)
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
            queryResponse = self.query_gemini(f"In the context of Search and Rescue, what could a found {item} mean?")
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
        print(f"The radius has been updated to : {self.searchRadius} meters.")

    def get_distance_covered(self):
        distanceCovered = math.pi * (self.searchRadius ** 2)
        print(f"Distance Covered so far: {distanceCovered} m^2.")
        return distanceCovered

    def get_area_covered_by_time(self):
        currentTime = self.get_current_time()
        timeElapsed = self.get_elapsed_search_time(self, currentTime)
        self.areaCoverRate = self.get_distance_covered() / (timeElapsed[0] * 3600 + timeElapsed[1])
        print(f"The rate of distance being covered is: {self.areaCoverRate} m^2/seconds.")
        return self.areaCoverRate

    def send_message(self, recipient, message):
        """Send a message via the leader to the recipient by alias."""
        self.leader.send_message(self.alias, recipient, message)

    def receive_messages(self):
        """Retrieve messages from the leader."""
        return self.leader.receive_messages(self.alias)

    def update_location(self, latitude, longitude):
        """Send location updates to the leader."""
        self.leader.update_location(self.alias, latitude, longitude)

    def get_location(self, agent_name):
        """Retrieve another agent's location via the leader."""
        return self.leader.get_location(agent_name)

    def end_search(self):
        # Mark the duration of the search.
        self.endSearchTime = self.get_current_time()
        self.elapsedTime = self.get_elapsed_search_time(self.endSearchTime)
        print(f"The search started at {self.beginningSearchTime} and ended at {self.endSearchTime}, totaling a duration of {self.elapsedTime[0]} hours and {self.elapsedTime[1]} minutes.")

        # Note the number of clues found and what was found.
        print(f"The number of clues found during the search is {self.cluesCount}")

        # Find the amount of area covered to find the missing persons
        print(f"The rate of area covered during the search is {self.areaCoverRate} in (m^2/seconds).")

# leader = SearchTeamLeader()
# ag = SearchAgent("Agent_1", leader)





