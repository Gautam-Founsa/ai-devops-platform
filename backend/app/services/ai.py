import httpx

from app.core.config import get_settings


class AIOrchestrator:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def answer(self, prompt: str, context: dict) -> tuple[str, list[dict]]:
        if self.settings.ai_provider == "ollama":
            return await self._ollama_answer(prompt, context)

        answer = (
            "I reviewed the available Phase 1 telemetry context. "
            "No live anomaly source is connected yet, so this response is based on scaffolded "
            "Prometheus integration and stored platform context. "
            f"Recommended next step: inspect `{prompt[:120]}` with service metrics, recent deploys, "
            "and correlated logs once collectors are enabled."
        )
        citations = [
            {"label": "Prometheus metrics endpoint", "source": "/metrics"},
            {"label": "Phase 1 AI chat context", "source": "backend/app/services/ai.py"},
        ]
        return answer, citations

    async def _ollama_answer(self, prompt: str, context: dict) -> tuple[str, list[dict]]:
        system = (
            "You are an expert SRE copilot. Give concise, operationally useful answers. "
            "Call out uncertainty and suggest verification steps."
        )
        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"},
            ],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.settings.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", ""), [
            {"label": "Ollama local model", "source": self.settings.ollama_model}
        ]

