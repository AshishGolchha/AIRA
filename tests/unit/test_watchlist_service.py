import pytest
from app.services.financial.service import FinancialDataService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture
def watchlist_service():
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    return WatchlistService(financial_service=fin_service)


def test_watchlist_service_symbol_and_priority_validation(watchlist_service):
    """Verify input validation for user_id, symbol, and priority."""
    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        watchlist_service.add_item(user_id=0, symbol="NVDA")

    with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
        watchlist_service.add_item(user_id=1, symbol="")

    with pytest.raises(ValueError, match="Invalid symbol format"):
        watchlist_service.add_item(user_id=1, symbol="INVALID_TOO_LONG_TICKER")

    with pytest.raises(ValueError, match="Invalid priority"):
        watchlist_service.add_item(user_id=1, symbol="NVDA", priority="urgent")


def test_watchlist_service_crud_lifecycle(app, watchlist_service):
    """Verify adding, listing, getting, updating, and deleting watchlist items with multi-tenant scoping."""
    # 1. Add item
    item = watchlist_service.add_item(
        user_id=1,
        symbol="nvda",
        notes="First watchlist item",
        priority="high",
    )
    assert item["symbol"] == "NVDA"
    assert item["priority"] == "high"
    assert item["company_name"] == "NVDA Inc."  # Resolved from MockFinancialProvider
    item_id = item["id"]

    # 2. Duplicate symbol for same user rejected
    with pytest.raises(ValueError, match="already exists in your watchlist"):
        watchlist_service.add_item(user_id=1, symbol="NVDA")

    # 3. Different user can add the same symbol
    item_u2 = watchlist_service.add_item(user_id=2, symbol="NVDA", priority="low")
    assert item_u2["id"] != item_id
    assert item_u2["priority"] == "low"

    # 4. List items for user 1
    items_u1 = watchlist_service.list_items(user_id=1)
    assert len(items_u1) == 1
    assert items_u1[0]["id"] == item_id

    # 5. List items filtered by priority
    high_items = watchlist_service.list_items(user_id=1, priority="high")
    assert len(high_items) == 1
    low_items = watchlist_service.list_items(user_id=1, priority="low")
    assert len(low_items) == 0

    # 6. Retrieve item (user 1 gets item, user 2 gets None for user 1's item)
    assert watchlist_service.get_item(user_id=1, item_id=item_id) is not None
    assert watchlist_service.get_item(user_id=2, item_id=item_id) is None

    # 7. Update item
    updated = watchlist_service.update_item(user_id=1, item_id=item_id, notes="Updated note", priority="normal")
    assert updated["notes"] == "Updated note"
    assert updated["priority"] == "normal"

    # User 2 cannot update User 1's item
    assert watchlist_service.update_item(user_id=2, item_id=item_id, notes="Hacked") is None

    # 8. Delete item
    # User 2 cannot delete User 1's item
    assert watchlist_service.delete_item(user_id=2, item_id=item_id) is False
    # User 1 deletes successfully
    assert watchlist_service.delete_item(user_id=1, item_id=item_id) is True
    assert watchlist_service.get_item(user_id=1, item_id=item_id) is None
