"""Background jobs and tasks for the AI Agent application."""

import asyncio
import logging
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ApiTestItem:
    """Represents an API endpoint to test."""

    endpoint: str
    method: str = "POST"
    payload: Optional[Dict[str, Any]] = None
    name: str = ""


class ApiTester:
    """Python equivalent of the TypeScript CallerScript for testing API endpoints."""

    def __init__(self) -> None:
        self.base_interval_ms = int(settings.api_tester_base_interval_ms)
        self.server_url = f"http://{settings.api_host}:{settings.api_port}"
        self.jitter_percent = settings.api_tester_jitter_percent
        self.enabled = settings.api_tester_enabled
        self.task: Optional[asyncio.Task] = None
        self.client: Optional[httpx.AsyncClient] = None

        # Available API endpoints to test (equivalent to availableItems in TS)
        self.available_items: List[ApiTestItem] = [
            # Plant agent endpoints (doubled for 2x probability like in TS)
            ApiTestItem(
                endpoint="/api/v1/buy-plants",
                payload={"light": "low light", "maintenance": "high"},
                name="buy-plants-low-light-high-maintenance",
            ),
            ApiTestItem(
                endpoint="/api/v1/buy-plants",
                payload={"light": "low light", "maintenance": "low"},
                name="buy-plants-low-light-high-maintenance",
            ),
            ApiTestItem(
                endpoint="/api/v1/buy-plants",
                payload={"light": "medium light", "maintenance": "high"},
                name="buy-plants-medium-light-high-maintenance",
            ),
            ApiTestItem(
                endpoint="/api/v1/buy-plants",
                payload={"light": "medium light", "maintenance": "low"},
                name="buy-plants-medium-light-low-maintenance",
            ),
            ApiTestItem(
                endpoint="/api/v1/buy-plants",
                payload={"light": "full sun", "maintenance": "high"},
                name="buy-plants-full-sun-high-maintenance",
            ),
            ApiTestItem(
                endpoint="/api/v1/buy-plants",
                payload={"light": "full sun", "maintenance": "low"},
                name="buy-plants-full-sun-low-maintenance",
            ),
        ]

    async def start(self) -> None:
        """Start the API tester background task."""
        if not self.enabled:
            logger.info("🚫 API tester is disabled")
            return

        try:
            logger.info("🎨 Starting API tester...")
            logger.info(f"📡 Server URL: {self.server_url}")
            logger.info(f"⏱️  Base interval: {self.base_interval_ms}ms")
            logger.info(f"🎯 Jitter: ±{self.jitter_percent}%")
            logger.info(f"🎲 Available items: {len(self.available_items)} endpoints")

            # Create HTTP client
            self.client = httpx.AsyncClient(
                # timeout=30.0,
                headers={"Content-Type": "application/json"},
            )

            # Test connection
            # await self.test_connection()

            # Start the background task
            self.task = asyncio.create_task(self._run_periodic_tests())

            logger.info("✅ API tester started successfully")

        except Exception as error:
            logger.error(f"❌ Failed to start API tester: {error}")
            raise

    async def stop(self) -> None:
        """Stop the API tester background task."""
        logger.info("🛑 Stopping API tester...")

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

        if self.client:
            await self.client.aclose()
            self.client = None

        logger.info("🛑 API tester stopped")

    async def test_connection(self) -> None:
        """Test connection to the API server."""
        try:
            if not self.client:
                raise Exception("HTTP client not initialized")

            response = await self.client.get(f"{self.server_url}/api/v1/health")
            if response.status_code != 200:
                raise Exception(
                    f"Health check failed with status {response.status_code}"
                )

            result = response.json()
            logger.info(
                f"🔗 Connected to API server - {result.get('status', 'unknown')}"
            )

        except Exception as error:
            logger.error(f"❌ Failed to connect to API server: {error}")
            raise

    def get_random_item(self) -> ApiTestItem:
        """Get a random API endpoint to test."""
        return random.choice(self.available_items)

    def get_seasonal_multiplier(self) -> float:
        """Calculate seasonal multiplier based on time of day and day of week."""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday

        # Time of day seasonality (peak hours have faster intervals)
        if 9 <= hour <= 17:  # Business hours - more active
            time_multiplier = 0.7  # 30% faster
        elif 18 <= hour <= 22:  # Evening - moderate activity
            time_multiplier = 0.9  # 10% faster
        else:  # Night/early morning - slower
            time_multiplier = 1.5  # 50% slower

        # Day of week seasonality
        if 0 <= day_of_week <= 4:  # Weekdays - more active
            day_multiplier = 0.8  # 20% faster
        else:  # Weekends - slower
            day_multiplier = 1.3  # 30% slower

        return time_multiplier * day_multiplier

    def add_jitter(self, base_value: float) -> float:
        """Add random jitter to the base value."""
        jitter_amount = (self.jitter_percent / 100) * base_value
        random_jitter = (
            (random.random() - 0.5) * 2 * jitter_amount
        )  # -jitter to +jitter
        return max(1.0, base_value + random_jitter)  # Minimum 1 second

    def calculate_next_interval(self) -> float:
        """Calculate the next interval with seasonal adjustment and jitter."""
        seasonal_interval = (
            self.base_interval_ms / 1000.0
        ) * self.get_seasonal_multiplier()
        return self.add_jitter(seasonal_interval)

    async def execute_random_call(self) -> None:
        """Execute a random API call."""
        try:
            if not self.client:
                logger.error("❌ HTTP client not available")
                return

            item = self.get_random_item()
            ts = datetime.now().isoformat()
            emoji = "🌱"

            logger.info(
                f"\n{emoji} [{ts}] Calling {item.method} {item.endpoint} ({item.name})"
            )

            url = f"{self.server_url}{item.endpoint}"

            if item.method == "GET":
                response = await self.client.get(url)
                if response.status_code == 200:
                    logger.info("✅ Success")
                else:
                    logger.info(f"❌ Failed - Status {response.status_code}")
            else:  # POST
                response = await self.client.post(url, json=item.payload)
                if response.status_code == 200:
                    logger.info("✅ Success")
                else:
                    logger.info(f"❌ Failed - Status {response.status_code}")

        except Exception as error:
            logger.info(f"❌ Failed - {str(error)}")

    async def _run_periodic_tests(self) -> None:
        """Run periodic API tests with dynamic intervals."""
        try:
            # Run immediately once
            await self.execute_random_call()

            while True:
                # Calculate next interval
                next_interval = self.calculate_next_interval()
                sm = self.get_seasonal_multiplier()

                logger.info(
                    f"⏰ Next call in {next_interval:.1f}s (seasonal: {sm:.2f}x)"
                )
                print(f"⏰ Next call in {next_interval:.1f}s (seasonal: {sm:.2f}x)")

                # Wait for the calculated interval
                await asyncio.sleep(next_interval)

                # Execute the next call
                await self.execute_random_call()

        except asyncio.CancelledError:
            logger.info("🛑 Periodic API testing cancelled")
            raise
        except Exception as error:
            logger.error(f"❌ Error in periodic API testing: {error}")


# Global API tester instance
api_tester = ApiTester()
