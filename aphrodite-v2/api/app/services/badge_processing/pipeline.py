from __future__ import annotations

import time
from typing import List

from aphrodite_logging import get_logger

from .types import (
    UniversalBadgeRequest,
    SingleBadgeRequest,
    BulkBadgeRequest,
    ProcessingResult,
    PosterResult,
    ProcessingMode,
)


class UniversalBadgeProcessor:
    """Universal entry point for badge processing."""

    def __init__(self):
        self.logger = get_logger("aphrodite.badge.pipeline")

    async def process_request(self, request: UniversalBadgeRequest) -> ProcessingResult:
        start = time.perf_counter()

        if request.processing_mode == ProcessingMode.AUTO:
            mode = await self.auto_select_mode(request)
        else:
            mode = request.processing_mode

        if mode == ProcessingMode.IMMEDIATE and request.single_request:
            result = await self.process_single(request.single_request)
        elif mode == ProcessingMode.QUEUED and request.bulk_request:
            result = await self.process_bulk(request.bulk_request)
        else:
            result = ProcessingResult(success=False, results=[], error="Invalid request")

        result.processing_time = time.perf_counter() - start
        return result

    async def process_single(self, request: SingleBadgeRequest) -> ProcessingResult:
        self.logger.debug(f"Processing single poster: {request.poster_path}")
        # Placeholder image processing logic
        result = PosterResult(
            source_path=request.poster_path,
            output_path=request.output_path or request.poster_path,
            applied_badges=request.badge_types,
            success=True,
        )
        return ProcessingResult(success=True, results=[result])

    async def process_bulk(self, request: BulkBadgeRequest) -> ProcessingResult:
        self.logger.debug(f"Processing bulk posters: {len(request.poster_paths)}")
        results: List[PosterResult] = []
        for path in request.poster_paths:
            single_result = await self.process_single(
                SingleBadgeRequest(
                    poster_path=path,
                    badge_types=request.badge_types,
                    use_demo_data=request.use_demo_data,
                    output_path=None,
                )
            )
            results.extend(single_result.results)
        return ProcessingResult(success=True, results=results)

    async def auto_select_mode(self, request: UniversalBadgeRequest) -> ProcessingMode:
        if request.bulk_request and len(request.bulk_request.poster_paths) > 5:
            return ProcessingMode.QUEUED
        return ProcessingMode.IMMEDIATE
