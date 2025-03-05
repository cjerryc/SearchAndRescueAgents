# Search and Rescue (SAR) Agent Framework - CSC 581

## Introduction
In implementing the Search Team Leader, I created a Search Team Leader to lead Search Agents, which may have its current
implementation found in search_agent.py under the agents directory. The corresponding tests for functionality are 
in test_search_agent.py.

## Prerequisites
- Python 3.8 or higher (Uses 3.11 for Google Gemini)

## Development
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
- When using the agents, it would be wise to poll for messages at some set interval to get the most updated information
from an agent's inbox.

## Testing
Run the test suite with:
- pytest tests/test_search_agent.py

## Insights
- Prior implementation allowed for multiple instantiations of Search Agents, but failed to allow these agents to communicate in an effective manner.
This was a challenge of hierarchy and organization that could be solved with a leader figure; thus, I created a "Search Team Leader"
to fill that role. Consequently, each Search Agent now requires a team leader to register with, keeping the movements more organized between agents in the field.
- While the first implementation of Search Agents had a framework for search and basic information that would be useful in a Search and Rescue scenario,
it lacked more creative methods of attacking an SAR problem. So, I needed to include some more creative injections of thought for a team leader. I opted for
an LLM call to google Gemini with some specifications provided by the team leader to better utilize agents in the field. This could potentially give users
more insight in the field when snap critical thinking in searches are needed.
- The prior suite of tests tested the successful functionality of Search Agent Methods but did not handle bad input or edge cases. To make for more robust
tests, I needed to expand on unit testing for both Search Agents and my new Search Team Leader.


## Modifications
- Added a Search Team Leader class for Search Agents to report to. This allows for
messaging between agents and tracking.
- Added increased tests and error behavior testing for Search Agents and Search Team Leader. 
- Tests now check for bad input and runtime errors that are thrown from ValueErrors.
- Units are explicitly defined where appropriate for agent methods with user level prints. This is to help maintain consistency.
- Agent Registration is implicitly tested by testing for agent logging for team leaders and messaging functionality between agents under the same team leader.
- Added another LLM call with specifications on Terrain, Number of Agents, and Location to 
suggest an optimized Search and Rescue strategy from outside knowledge.