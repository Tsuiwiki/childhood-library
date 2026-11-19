"""versions 领域路由（T-05 骨架）。"""
from app.api.v1._skeleton import make_domain_router

router = make_domain_router("versions", "歌词版本、录音版本、乐谱版本")
