import pytest
from sar_project.agents.search_agent import SearchTeamLeader, SearchAgent


class TestSearchAgent:
    @pytest.fixture
    def leader(self):
        """Team Leader"""
        return SearchTeamLeader()

    @pytest.fixture
    def agent(self, leader):
        """Agent 1"""
        return SearchAgent(name="Agent_1", leader=leader)

    @pytest.fixture
    def agent2(self, leader):
        """Agent 2"""
        return SearchAgent(name="Agent_2", leader=leader)

    def test_agent_has_leader(self, agent, leader):
        """Verify that the agent correctly references the leader."""
        assert agent.leader == leader

    def test_agent_registers_with_leader(self, agent, leader):
        """Ensure the leader registers the agent."""
        assert "Agent_1" in leader.agents

    def test_agent_initialization_fails_without_leader(self):
        """Ensure SearchAgent raises an error when no leader is provided."""
        with pytest.raises(ValueError, match="must have a SearchTeamLeader assigned."):
            SearchAgent(name="Agent_Without_Leader", leader=None)

    def test_agent_rejects_invalid_leader(self):
        """Ensure SearchAgent raises a TypeError for invalid leader type."""
        with pytest.raises(TypeError, match="received an invalid leader. Expected a SearchTeamLeader instance."):
            SearchAgent(name="Agent_Invalid_Leader", leader="NotALeader")

    def test_initialization(self, agent):
        assert agent.name == "Agent_1"
        assert agent.role == "Search Agent"
        assert agent.mission_status == "standby"

    def test_add_clue(self, agent):
        """Add a clue to the dictionary of clues for an agent"""
        item = "glasses"
        information = "info"
        agent.add_clue(item, information)
        assert agent.get_clue(item) == information

    def test_get_clue_found(self, agent):
        """Getting information about a clue that exists should return its associated information"""
        item = "cloth"
        information = "info"
        agent.add_clue(item, information)
        assert agent.get_clue(item) == information

    def test_get_clue_not_found(self, agent):
        """Getting information about a clue that does not exist should return an error"""
        item = "cloth"
        information = "info"
        agent.add_clue(item, information)
        errorMsg = "This item does not appear to be a clue found yet."
        assert agent.get_clue("fakeClue") == errorMsg

    def test_remove_clue(self, agent):
        """Successfully remove a clue"""
        item = "bandage"
        information = "info"
        agent.add_clue(item, information)
        assert agent.remove_clue(item) == True

    def test_get_time_difference(self, agent):
        """Calculate the time difference"""
        laterTime = "2025-02-15 08:30:38.173807+00:00"
        earlierTime = "2025-02-14 08:30:38.173807+00:00"
        assert agent.get_time_difference(laterTime, earlierTime) == (24.0, 0.0)

    def test_get_area_covered_by_time(self, agent):
        """Find the area covered by radius"""
        radius = 3.0
        agent.update_search_radius(radius)
        assert agent.get_distance_covered() == 28.274333882308138

    def test_agent2_registers_with_leader(self, agent2, leader):
        """Ensure the leader registers the agent."""
        assert "Agent_2" in leader.agents

    def test_send_message_success(self, leader, agent, agent2):
        """Send and Receive messages successfully via the team leader"""
        message = "Hello Agent_2"
        agent.send_message(agent2.alias, message)
        assert agent2.receive_messages() == [(agent.alias, message)]

    def test_send_message_wrong_agent_empty_inbox(self, leader, agent, agent2):
        """Send messages to another agent, a third party should not receive messages"""
        message = "Hello Agent_2"
        agent.send_message("Agent_3", message)
        assert agent2.receive_messages() == []

    def test_get_other_agent_location(self, leader, agent, agent2):
        """Get the location of a fellow agent, under the same Team Leader"""
        latitude = "35.3050° N"
        longitude = "120.6625° W"
        agent.update_location(latitude, longitude)
        assert agent2.get_location(agent.alias) == (latitude, longitude)

    def test_get_unregistered_agent_location_failure(self, leader, agent, agent2):
        """Trying to get the location of an unregistered agent should return None"""
        latitude = "35.3050° N"
        longitude = "120.6625° W"
        agent.update_location(latitude, longitude)
        assert agent2.get_location("Agent_3") is None

    def test_get_other_agent_location_Unknown_location(self, leader, agent, agent2):
        """No Location set yet for agent, so retrieval should return Unknown"""
        assert agent2.get_location(agent.alias) == "Location unknown"

