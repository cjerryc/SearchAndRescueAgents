import pytest
from sar_project.agents.search_agent import SearchAgent

class TestSearchAgent:
    @pytest.fixture
    def agent(self):
        return SearchAgent()

    def test_initialization(self, agent):
        assert agent.name == "search_team_leader"
        assert agent.role == "Search Team Leader"
        assert agent.mission_status == "standby"

    def test_add_clue(self, agent):
        item = "glasses"
        information = "info"
        agent.add_clue(item, information)
        assert agent.get_clue(item) == information

    def test_get_clue_found(self, agent):
        item = "cloth"
        information = "info"
        agent.add_clue(item, information)
        assert agent.get_clue(item) == information

    def test_get_clue_not_found(self, agent):
        item = "cloth"
        information = "info"
        agent.add_clue(item, information)
        errorMsg = "This item does not appear to be a clue found yet."
        assert agent.get_clue("fakeClue") == errorMsg

    def test_remove_clue(self, agent):
        item = "bandage"
        information = "info"
        agent.add_clue(item, information)
        assert agent.remove_clue(item) == True

    def test_get_time_difference(self, agent):
        laterTime = "2025-02-15 08:30:38.173807+00:00"
        earlierTime = "2025-02-14 08:30:38.173807+00:00"
        assert agent.get_time_difference(laterTime, earlierTime) == (24.0, 0.0)

    def test_get_area_covered_by_time(self, agent):
        radius = 3.0
        agent.update_search_radius(self, radius)
        assert agent.get_distance_covered() == 28.274333882308138


# tst = TestSearchAgent()
# tst.test_get_clue_not_found(tst.agent())
