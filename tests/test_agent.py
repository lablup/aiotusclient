import pytest

from ai.backend.client.session import Session


@pytest.mark.asyncio
class TestAgent:

    @pytest.mark.integration
    async def test_list_agent(self):
        with Session() as sess:
            result = sess.Agent.list_with_limit(1, 0)
            assert len(result['items']) == 1
