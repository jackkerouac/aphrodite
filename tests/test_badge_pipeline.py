import unittest
import sys
import importlib.util
from pathlib import Path

# Dynamically load badge processing modules without requiring full service dependencies
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir / "aphrodite-v2"))

badge_dir = parent_dir / "aphrodite-v2" / "api" / "app" / "services" / "badge_processing"

# Load types module
types_spec = importlib.util.spec_from_file_location("badge_processing.types", badge_dir / "types.py")
types_module = importlib.util.module_from_spec(types_spec)
sys.modules["badge_processing.types"] = types_module
types_spec.loader.exec_module(types_module)

# Load pipeline module
pipeline_spec = importlib.util.spec_from_file_location(
    "badge_processing.pipeline", badge_dir / "pipeline.py", submodule_search_locations=[str(badge_dir)]
)
pipeline_module = importlib.util.module_from_spec(pipeline_spec)
sys.modules["badge_processing.pipeline"] = pipeline_module
pipeline_spec.loader.exec_module(pipeline_module)

UniversalBadgeProcessor = pipeline_module.UniversalBadgeProcessor
UniversalBadgeRequest = pipeline_module.UniversalBadgeRequest
SingleBadgeRequest = pipeline_module.SingleBadgeRequest
BulkBadgeRequest = pipeline_module.BulkBadgeRequest
ProcessingMode = pipeline_module.ProcessingMode

class TestBadgePipeline(unittest.IsolatedAsyncioTestCase):
    async def test_single_processing(self):
        processor = UniversalBadgeProcessor()
        request = UniversalBadgeRequest(
            single_request=SingleBadgeRequest(
                poster_path="/tmp/poster.jpg",
                badge_types=["audio"],
            ),
            processing_mode=ProcessingMode.IMMEDIATE,
        )
        result = await processor.process_request(request)
        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].applied_badges, ["audio"])

    async def test_bulk_processing_auto_mode(self):
        processor = UniversalBadgeProcessor()
        request = UniversalBadgeRequest(
            bulk_request=BulkBadgeRequest(
                poster_paths=[f"poster_{i}.jpg" for i in range(6)],
                badge_types=["audio", "resolution"],
            ),
            processing_mode=ProcessingMode.AUTO,
        )
        result = await processor.process_request(request)
        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 6)
        for r in result.results:
            self.assertIn("audio", r.applied_badges)
            self.assertIn("resolution", r.applied_badges)
