from datetime import datetime, timezone
from app.models.watchlist import WatchlistItem


def test_watchlist_item_model_instantiation_and_serialization():
    """Verify WatchlistItem model instantiates with defaults and serializes correctly."""
    item = WatchlistItem(
        id=10,
        user_id=1,
        symbol="nvda",
        company_name="NVIDIA Corporation",
        notes="Core AI infrastructure position",
        priority="HIGH",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert item.symbol == "NVDA"
    assert item.priority == "high"
    assert item.company_name == "NVIDIA Corporation"

    data = item.to_dict()
    assert data["id"] == 10
    assert data["symbol"] == "NVDA"
    assert data["company_name"] == "NVIDIA Corporation"
    assert data["notes"] == "Core AI infrastructure position"
    assert data["priority"] == "high"
    assert "user_id" not in data  # Internal foreign keys omitted from client payload
    assert "created_at" in data
    assert "updated_at" in data


def test_watchlist_item_default_priority():
    """Verify WatchlistItem defaults to 'normal' priority."""
    item = WatchlistItem(
        user_id=2,
        symbol="AAPL",
    )
    assert item.priority == "normal"
    assert item.symbol == "AAPL"
