"""catalog 领域路由（T-05 骨架）。"""
from app.api.v1._skeleton import make_domain_router

router = make_domain_router("catalog", "作品、作者、分类、标签与作品关系")
