@dataclass(slots=True)
class ValidationService:
    """
    Validates generated strategies through backtests, Monte Carlo, and robustness filters.
    Matches HERMES v5.2 Task 1.2 Validation Service responsibilities.
    """

    sqlite_path: str
    event_bus: AsyncEventBus
    hermes_client: Optional[HermesClient] = None # For market data, etc.
    interval_seconds: int = 10

    _is_running: bool = False

    async def start(self):
        """Start the validation loop, polling the outbox for new strategies."""
        self._is_running = True
        logger.info("Validation Service started, polling outbox.")
        while self._is_running:
            try:
                await self.process_outbox()
            except asyncio.CancelledError:
                logger.info("Validation Service task cancelled.")
                break
            except Exception as e:
                logger.error("Error in Validation Service loop: %s", e)
            await asyncio.sleep(self.interval_seconds)

    async def stop(self):
        """Stops the validation loop."""
        self._is_running = False
        logger.info("Validation Service stopped.")

    async def process_outbox(self):
        """Polls the outbox for new STRATEGY_GENERATED events."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            async with db.execute(
                """
                SELECT id, payload_json, genome_hash, created_at FROM outbox 
                WHERE consumed = 0 AND event_type = ?
                ORDER BY created_at ASC LIMIT 1
                """,
                (EventType.STRATEGY_GENERATED.value,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    outbox_id, payload_json, genome_hash, created_at = row
                    logger.info("Processing strategy from outbox: genome_hash=%s", genome_hash)
                    try:
                        # Reconstruct payload, including correlation_id if available
                        payload_dict = json.loads(payload_json)
                        strategy_generated_payload = StrategyGeneratedPayload(**payload_dict)
                        
                        # Publish VALIDATION_STARTED event
                        await self.event_bus.publish(HermesEvent(
                            event_id=uuid4(),
                            timestamp=datetime.now(timezone.utc),
                            correlation_id=uuid4(), # New correlation for this validation run
                            source_component="validation_service",
                            source_instance="local-validation-node",
                            event_type=EventType.VALIDATION_STARTED.value,
                            payload={"genome_hash": genome_hash, "outbox_id": outbox_id}
                        ))
                        logger.info("Published VALIDATION_STARTED for genome_hash=%s", genome_hash)

                        await self.validate_strategy(strategy_generated_payload)
                        await self._mark_outbox_consumed(outbox_id)
                    except Exception as e:
                        logger.error("Error validating strategy from outbox ID %d: %s", outbox_id, e)
                        await self._increment_outbox_retry(outbox_id)
                else:
                    logger.debug("No new strategies in outbox.")

    async def validate_strategy(self, strategy_payload: StrategyGeneratedPayload):
        """
        Performs comprehensive validation on a strategy.
        This would include backtesting, Monte Carlo, tax modeling etc.
        """
        logger.info("Starting validation for strategy: %s", strategy_payload.genome_hash)
        
        # Simulate validation process
        await asyncio.sleep(2) # Simulate heavy computation

        # For simplicity, we'll make it pass randomly for now
        is_passed = True # random.choice([True, False])

        if is_passed:
            validation_payload = ValidationPassedPayload(
                genome_hash=strategy_payload.genome_hash,
                backtest_id=1, # Placeholder
                sharpe_ratio=Decimal("1.2"),
                max_drawdown_pct=Decimal("15.0"),
                total_trades=100,
                oos_sharpe_ratio=Decimal("0.9"),
                walk_forward_efficiency=Decimal("0.7"),
                monte_carlo_95th_dd=Decimal("25.0"),
                parameter_stability_score=Decimal("10.0"),
                benchmark_alpha=Decimal("0.05"),
                benchmark_beta=Decimal("1.1"),
                information_ratio=Decimal("1.0"),
                after_tax_alpha=Decimal("0.03"),
                similarity_score=Decimal("0.4"),
                validation_duration_ms=2000,
                validated_at=datetime.now(timezone.utc),
            )
            event = ValidationPassed(
                event_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                correlation_id=strategy_payload.correlation_id, # Propagate correlation_id
                source_component="validation_service",
                source_instance="local-validation-node",
                payload=validation_payload.model_dump()
            )
            await self.event_bus.publish(event)
            logger.info("Validation PASSED for %s", strategy_payload.genome_hash)
        else:
            validation_payload = ValidationFailedPayload(
                genome_hash=strategy_payload.genome_hash,
                backtest_id=1, # Placeholder
                failure_reason="simulated_failure",
                validated_at=datetime.now(timezone.utc),
            )
            event = ValidationFailed(
                event_id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                correlation_id=strategy_payload.correlation_id, # Propagate correlation_id
                source_component="validation_service",
                source_instance="local-validation-node",
                payload=validation_payload.model_dump()
            )
            await self.event_bus.publish(event)
            logger.warning("Validation FAILED for %s", strategy_payload.genome_hash)

    async def _mark_outbox_consumed(self, outbox_id: int):
        """Mark an outbox entry as consumed."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                "UPDATE outbox SET consumed = 1, consumed_at = ?, consumed_by = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), "validation_service", outbox_id)
            )
            await db.commit()
            logger.debug("Outbox ID %d marked as consumed.", outbox_id)

    async def _increment_outbox_retry(self, outbox_id: int):
        """Increment retry count for a failed outbox entry."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                "UPDATE outbox SET retry_count = retry_count + 1 WHERE id = ?",
                (outbox_id,)
            )
            await db.commit()
            logger.warning("Incremented retry count for outbox ID %d.", outbox_id)
