import json
import pytest

from fetching_library_python import FetchResult, FetchingHelper


@pytest.mark.asyncio
async def test_fetch_api():
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"

    # Act
    result: FetchResult = await FetchingHelper.fetch_api(url)

    # Assert
    assert result.is_success

    data = json.loads(result.content)

    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "title" in data[0]
    assert "body" in data[0]