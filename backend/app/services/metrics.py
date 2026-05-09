from datetime import UTC, datetime, timedelta
from random import Random


class MetricsService:
    async def query(self, promql: str) -> list[dict]:
        rng = Random(promql)
        now = datetime.now(UTC)
        return [
            {
                "timestamp": (now - timedelta(minutes=(11 - index) * 5)).isoformat(),
                "value": round(35 + rng.random() * 45 + index * 0.7, 2),
            }
            for index in range(12)
        ]

