# backend/routes/piazza.py
from fastapi import APIRouter
from ..services.piazza_service import PiazzaService

router = APIRouter()

piazza_service = PiazzaService()

@router.get("/fetch_piazza_data")
async def fetch_piazza_data(num_posts: int = 100):
    """Fetch Piazza posts, comments, and replies."""
    try:
        data = piazza_service.fetch_posts(num_posts=num_posts)
        return {"piazza_data": data}
    except Exception as e:
        return {"error": str(e)}
