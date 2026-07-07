import os
import threading
import logging
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_QUOTA_KEYWORDS = [
    "rate limit",
    "quota",
    "monthly",
    "credits",
    "payment required",
    "too many requests",
    "exceeded",
]


class HFTokenManager:
    """
    Mengelola pool token HuggingFace dengan auto-rotate saat quota habis.
    Membaca HUGGINGFACEHUB_API_TOKEN_1, _2, _3 dari environment.
    Fallback ke HUGGINGFACEHUB_API_TOKEN (tanpa angka) jika tidak ada token bernomor.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.tokens = self._load_tokens()
        self.current_index = 0
        self.exhausted_indices: set[int] = set()
        self._llm_cache: dict[int, ChatHuggingFace] = {}

        if not self.tokens:
            raise ValueError(
                "Tidak ada token HuggingFace yang tersedia. "
                "Set HUGGINGFACEHUB_API_TOKEN_1 (atau HUGGINGFACEHUB_API_TOKEN) di .env"
            )

        logger.info(f"[HFTokenManager] {len(self.tokens)} token tersedia.")

    def _load_tokens(self) -> list[str]:
        tokens = []
        for i in range(1, 10):  # maksimum 9 token
            token = os.getenv(f"HUGGINGFACEHUB_API_TOKEN_{i}", "").strip()
            if token:
                tokens.append(token)

        if not tokens:
            single = os.getenv("HUGGINGFACEHUB_API_TOKEN", "").strip()
            if single:
                tokens.append(single)

        return tokens

    def _build_llm(self, token: str) -> ChatHuggingFace:
        endpoint = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            huggingfacehub_api_token=token,
            temperature=0.7,
            max_new_tokens=512,
            task="conversational",
        )
        return ChatHuggingFace(llm=endpoint)

    def _get_current_llm(self) -> ChatHuggingFace:
        idx = self.current_index
        if idx not in self._llm_cache:
            self._llm_cache[idx] = self._build_llm(self.tokens[idx])
        return self._llm_cache[idx]

    def _is_quota_error(self, error: Exception) -> bool:
        error_str = str(error).lower()
        return any(kw in error_str for kw in _QUOTA_KEYWORDS)

    def _rotate(self) -> bool:
        """
        Tandai token saat ini sebagai exhausted dan pindah ke token berikutnya.
        Returns True jika berhasil rotate, False jika semua token sudah habis.
        """
        with self._lock:
            self.exhausted_indices.add(self.current_index)
            logger.warning(
                f"[HFTokenManager] Token #{self.current_index + 1} habis. "
                f"Mencari token berikutnya ({len(self.exhausted_indices)}/{len(self.tokens)} exhausted)."
            )

            for i in range(1, len(self.tokens) + 1):
                next_idx = (self.current_index + i) % len(self.tokens)
                if next_idx not in self.exhausted_indices:
                    self.current_index = next_idx
                    logger.info(f"[HFTokenManager] Beralih ke token #{next_idx + 1}.")
                    return True

            logger.error("[HFTokenManager] Semua token HuggingFace sudah habis.")
            return False

    def invoke(self, messages):
        """
        Invoke LLM dengan auto-fallback.
        Interface identik dengan llm.invoke() — tidak perlu ubah routes/chat.py.
        """
        while True:
            try:
                return self._get_current_llm().invoke(messages)
            except Exception as e:
                if self._is_quota_error(e):
                    if not self._rotate():
                        raise RuntimeError(
                            "Semua token HuggingFace telah habis. "
                            "Tambahkan token baru di environment variables."
                        ) from e
                    # lanjut loop — coba dengan token baru
                else:
                    raise  # error lain (network, model error, dll) langsung raise

    @property
    def active_token_index(self) -> int:
        """Untuk monitoring/logging — token ke-berapa yang sedang aktif."""
        return self.current_index + 1

    @property
    def available_tokens(self) -> int:
        """Berapa token yang masih belum exhausted."""
        return len(self.tokens) - len(self.exhausted_indices)


# Singleton — dipakai di seluruh aplikasi
token_manager = HFTokenManager()