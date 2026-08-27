from flask import Blueprint, current_app, g, jsonify, request

from app.common.auth import auth_required
from app.services.memory_service import MemoryService

memory_bp = Blueprint("memory", __name__, url_prefix="/api/v1/memory")


def _get_memory_service() -> MemoryService:
    """Returns memory service instance, allowing test overrides via app.extensions."""
    return current_app.extensions.get("memory_service") or MemoryService()


@memory_bp.post("")
@memory_bp.post("/")
@auth_required
def create_memory():
    """Store a new user memory and generate its vector embedding."""
    data = request.get_json(silent=True) or {}
    content = data.get("content")
    memory_type = data.get("memory_type", "preference")
    importance = data.get("importance", "medium")
    metadata = data.get("metadata")

    service = _get_memory_service()
    try:
        memory = service.create_memory(
            user_id=g.current_user.id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata,
        )
        return jsonify({
            "success": True,
            "data": {
                "memory": memory,
            },
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e),
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400
    except Exception as e:
        current_app.logger.exception(f"Failed to create memory: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Failed to persist memory record.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 500


@memory_bp.get("")
@memory_bp.get("/")
@auth_required
def list_memories():
    """Retrieve recent memories for the authenticated user."""
    limit_arg = request.args.get("limit", 20)
    memory_type = request.args.get("type")

    try:
        limit = int(limit_arg)
    except (ValueError, TypeError):
        limit = 20

    service = _get_memory_service()
    try:
        memories = service.list_memories(
            user_id=g.current_user.id,
            limit=limit,
            memory_type=memory_type,
        )
        return jsonify({
            "success": True,
            "data": {
                "memories": memories,
                "count": len(memories),
            },
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e),
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400


@memory_bp.get("/search")
@auth_required
def search_memories():
    """Perform semantic vector search across authenticated user's memories."""
    query = request.args.get("q")
    if not query or not query.strip():
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Search query parameter 'q' is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    limit_arg = request.args.get("limit", 5)
    threshold_arg = request.args.get("threshold")
    memory_type = request.args.get("type")

    try:
        limit = int(limit_arg)
    except (ValueError, TypeError):
        limit = 5

    threshold = None
    if threshold_arg is not None:
        try:
            threshold = float(threshold_arg)
        except (ValueError, TypeError):
            threshold = None

    service = _get_memory_service()
    try:
        results = service.search_memories(
            user_id=g.current_user.id,
            query=query.strip(),
            limit=limit,
            threshold=threshold,
            memory_type=memory_type,
        )
        return jsonify({
            "success": True,
            "data": {
                "query": query.strip(),
                "results": results,
                "count": len(results),
            },
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e),
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400
    except Exception as e:
        current_app.logger.exception(f"Semantic search failed: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Semantic memory search failed.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 500


@memory_bp.delete("/<memory_id>")
@auth_required
def delete_memory(memory_id: str):
    """Delete a memory record owned by the authenticated user."""
    service = _get_memory_service()
    try:
        deleted = service.delete_memory(
            user_id=g.current_user.id,
            memory_id=memory_id,
        )
        if not deleted:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Memory not found or not owned by user.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "deleted": True,
            },
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e),
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400
