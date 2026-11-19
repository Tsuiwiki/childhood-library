"""ingestion 领域路由（T-05 骨架）。"""
from app.api.v1._skeleton import make_domain_router

router = make_domain_router("ingestion", "人工导入、来源 Adapter 与任务记录")
