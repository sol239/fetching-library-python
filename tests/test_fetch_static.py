import pytest


from core import FetchResult
from core import FetchingHelper


@pytest.mark.asyncio
async def test_fetch_static():
    # Arrange
    should_contain: str = "Seznam Zprávy"

    # Act
    result: FetchResult = await FetchingHelper.fetch_static("https://www.seznam.cz/")

    # Assert
    assert result.is_success
    assert should_contain in result.content
