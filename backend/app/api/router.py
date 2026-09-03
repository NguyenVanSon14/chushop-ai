from fastapi import APIRouter

from app.modules.analytics.router import router as analytics_router
from app.modules.assistant.router import router as assistant_router
from app.modules.auth.router import router as auth_router
from app.modules.businesses.router import router as businesses_router
from app.modules.expenses.router import router as expenses_router
from app.modules.products.router import router as products_router
from app.modules.sales.router import router as sales_router

api_router = APIRouter()
api_router.include_router(analytics_router)
api_router.include_router(assistant_router)
api_router.include_router(auth_router)
api_router.include_router(businesses_router)
api_router.include_router(products_router)
api_router.include_router(sales_router)
api_router.include_router(expenses_router)
