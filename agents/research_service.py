@dataclass(slots=True)
class ResearchService:
    """
    Manages strategy discovery through genetic algorithms and LLM hypotheses.
    Matches HERMES v5.2 Task 1.2 Research Service responsibilities.
    """

    sqlite_path: str
    event_bus: AsyncEventBus
    hermes_client: Optional[HermesClient] = None # For Ollama structured output
    multi_model_router: Optional[MultiModelRouter] = None # For Ollama
    interval_seconds: int = 60

    _is_running: bool = False

    async def start(self):
        """Starts the research loop."""
        self._is_running = True
        logger.info("Research Service started.")
        while self._is_running:
            try:
                await self.generate_and_store_strategy()
            except asyncio.CancelledError:
                logger.info("Research Service task cancelled.")
                break
            except Exception as e:
                logger.error("Error in Research Service loop: %s", e)
            await asyncio.sleep(self.interval_seconds)

    async def stop(self):
        """Stops the research loop."""
        self._is_running = False
        logger.info("Research Service stopped.")

    async def generate_and_store_strategy(self):
        """
        Generates a new strategy (or set of mutations) and stores it in the outbox.
        """
        logger.info("Generating new strategy hypothesis...")
        
        # 1. Hypothesis Generation (via Ollama/LLM)
        hypothesis = await self._generate_hypothesis_with_ollama()

        if not hypothesis:
            logger.warning("Failed to generate a valid hypothesis. Skipping strategy generation.")
            return

        # 2. Genetic Engine (simplified for initial implementation)
        genome_content = self._create_simple_genome(hypothesis)
        genome_hash = self._hash_genome(genome_content)
        
        strategy_payload = StrategyGeneratedPayload(
            genome=genome_content,
            genome_hash=genome_hash,
            parent_genome_hash=None,
            hypothesis_id=str(uuid4()),
            sector=hypothesis.get("sector", "unknown"),
            category=hypothesis.get("category", "midcap"),
            regime=hypothesis.get("regime", "normal"),
            generated_at=datetime.now(timezone.utc),
            outbox_id=0 # Will be updated after DB insert
        )

        # 3. Store in Outbox (Research PostgreSQL)
        outbox_id = await self._store_in_outbox(strategy_payload)
        strategy_payload.outbox_id = outbox_id

        # 4. Publish STRATEGY_GENERATED event
        strategy_event = StrategyGenerated(
            event_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            correlation_id=uuid4(),
            source_component="research_service",
            source_instance="local-research-node",
            payload=strategy_payload.model_dump()
        )
        await self.event_bus.publish(strategy_event)
        logger.info("Published STRATEGY_GENERATED event for genome_hash=%s, outbox_id=%d", genome_hash, outbox_id)

    async def _generate_hypothesis_with_ollama(self) -> Dict[str, Any]:
        """Simulate LLM structured output for a strategy hypothesis."""
        prompt = "Generate a new trading strategy hypothesis in JSON format, including 'sector', 'category', 'regime', and a brief 'description'."
        
        if self.multi_model_router:
            try:
                # In a real scenario, this would be a call to the LLM
                # For now, simulate a response
                response_str = json.dumps({
                    "strategy_name": "Momentum Breakout",
                    "sector": "technology",
                    "category": "largecap",
                    "regime": "normal",
                    "description": "Buy on 52-week high breakout with increased volume, sell on RSI divergence.",
                    "indicators": ["RSI", "Volume", "SMA"]
                })
                logger.info("Ollama (simulated) generated hypothesis: %s", response_str)
                return json.loads(response_str)
            except Exception as e:
                logger.error("Error calling Ollama/multi_model_router: %s", e)
                return {}
        else:
            logger.warning("MultiModelRouter not configured for ResearchService. Using dummy hypothesis.")
            return {
                "strategy_name": "Dummy Strategy",
                "sector": "finance",
                "category": "midcap",
                "regime": "volatile",
                "description": "A dummy strategy for testing purposes.",
                "indicators": []
            }

    def _create_simple_genome(self, hypothesis: Dict[str, Any]) -> str:
        """Create a dummy genome based on hypothesis."""
        return f"// PineScript v5
strategy("{hypothesis.get('strategy_name', 'Unnamed')}", overlay=true)
// Generated from: {hypothesis.get('description')}
plot(close)"

    def _hash_genome(self, genome_content: str) -> str:
        """Generate SHA-256 hash of the genome content."""
        import hashlib
        return hashlib.sha256(genome_content.encode()).hexdigest()

    async def _store_in_outbox(self, payload: StrategyGeneratedPayload) -> int:
        """Store the strategy payload in the outbox table."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO outbox (
                    event_type, payload_json, genome_hash, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    EventType.STRATEGY_GENERATED.value,
                    json.dumps(payload.model_dump(), default=str),
                    payload.genome_hash,
                    datetime.now(timezone.utc).isoformat(),
                    (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                )
            )
            await db.commit()
            return cursor.lastrowid
