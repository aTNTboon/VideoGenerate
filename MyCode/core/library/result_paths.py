import os
from pathlib import Path


class ResultPathManager:
    _repo_root = Path(__file__).resolve().parents[3]
    BASE_DIR = Path(os.getenv("RESULT_BASE_DIR", str(_repo_root / "result"))).resolve()

    @classmethod
    def ensure_base(cls) -> Path:
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
        return cls.BASE_DIR

    @classmethod
    def subdir(cls, name: str) -> Path:
        path = cls.ensure_base() / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def to_relative(cls, path: str) -> str:
        p = Path(path)
        if not p.is_absolute():
            return str(p).replace("\\", "/")
        try:
            rel = p.resolve().relative_to(cls.ensure_base())
            return str(rel).replace("\\", "/")
        except Exception:
            return str(p).replace("\\", "/")

    @classmethod
    def to_absolute(cls, path: str) -> str:
        p = Path(path)
        if p.is_absolute():
            return str(p)
        return str((cls.ensure_base() / p).resolve())

    @classmethod
    def resolve_for_serving(cls, relative_path: str) -> str:
        target = (cls.ensure_base() / relative_path).resolve()
        base = cls.ensure_base().resolve()
        if not str(target).startswith(str(base)):
            raise ValueError("非法路径")
        return str(target)
