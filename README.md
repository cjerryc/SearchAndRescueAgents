# Search and Rescue (SAR) Agent Framework - CSC 581

## Introduction
In implementing the Search Team Leader, I created a Search Agent, which may have its current
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

Note:
- Time is kept in ISO Universal Time (UTC) format, while elapsed time is kept in hours and minutes.
ex. "2025-02-15 08:30:38.173807+00:00"
- The class methods may be used for computation and presentation of the agent. Textual prints also post for users.
- Testing is done with a class made in test_search_agent.py
- The above three main functions of the agent are separated into the methods below.

