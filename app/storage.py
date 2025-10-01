import hashlib
from pathlib import Path
from typing import BinaryIO, Optional, Tuple

from .config import settings


class JarStorage:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_path = Path(base_dir or settings.storage_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_sha256(file_like: BinaryIO) -> str:
        sha256 = hashlib.sha256()
        for chunk in iter(lambda: file_like.read(8192), b""):
            sha256.update(chunk)
        file_like.seek(0)
        return sha256.hexdigest()

    def path_for_name(self, name: str) -> Path:
        return self.base_path / name

    def _compute_file_sha256(self, path: Path) -> str:
        with open(path, "rb") as f:
            sha256 = hashlib.sha256()
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _unique_name(self, original_name: str, desired_sha256: str) -> str:
        candidate = self.path_for_name(original_name)
        if not candidate.exists():
            return original_name
        existing_sha = self._compute_file_sha256(candidate)
        if existing_sha == desired_sha256:
            return original_name
        stem = candidate.stem
        suffix = candidate.suffix
        counter = 1
        while True:
            new_name = f"{stem} ({counter}){suffix}"
            new_path = self.base_path / new_name
            if not new_path.exists():
                return new_name
            if self._compute_file_sha256(new_path) == desired_sha256:
                return new_name
            counter += 1

    def save_file(self, file_like: BinaryIO, original_name: str, sha256_hex: str) -> Tuple[str, int]:
        final_name = self._unique_name(original_name, sha256_hex)
        target = self.path_for_name(final_name)
        if not target.exists() or self._compute_file_sha256(target) != sha256_hex:
            with open(target, "wb") as out:
                total = 0
                for chunk in iter(lambda: file_like.read(8192), b""):
                    out.write(chunk)
                    total += len(chunk)
            file_like.seek(0)
        else:
            total = target.stat().st_size
        return final_name, total

    def exists(self, name: str) -> bool:
        return self.path_for_name(name).exists()

    def delete(self, name: str) -> None:
        p = self.path_for_name(name)
        if p.exists():
            p.unlink()

    def open(self, name: str, mode: str = "rb"):
        return open(self.path_for_name(name), mode)
