import logging
from logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

def print_queries(planned_queries: list[str]) -> None:
    print(f"\n[query_planner] {len(planned_queries)} queries:")
    for query_text in planned_queries:
        print(f"  - {query_text}")


def print_search_results(search_results: list[dict], preview_count: int = 3) -> None:
    print(f"\n[search_tool] {len(search_results)} results")
    for result in search_results[:preview_count]:
        url = result.get("url", "")
        content = result.get("content", "")
        print(f"  [{url}] {content[:120]}...")
        print("  " + "-" * 40)


TEST_TOPIC = "Building a bridge over the Neris river in Vilnius"

# ----------------------------------------------------------------------------
#  RAG Pipeline Smoke Tests
# ----------------------------------------------------------------------------

# Step 1: query planner
# from rag.query_planner import plan_queries
# planned_queries = plan_queries(TEST_TOPIC)
# print_queries(planned_queries)
# assert isinstance(planned_queries, list)
# assert all(isinstance(query_text, str) for query_text in planned_queries)

# Step 2: search tool
# from rag.query_planner import plan_queries
# from rag.search_tool import execute_queries

# # previous step
# planned_queries = plan_queries(TEST_TOPIC, query_count=5)  # keep it cheap

# search_results = execute_queries(planned_queries)
# print_search_results(search_results, preview_count=10)

# if search_results:
#     required_keys = ("query", "content", "url")
#     assert all(key in search_results[0] for key in required_keys)

# Step 3: extractor
# from rag.extractor import extract_viewpoints
# from rag.query_planner import plan_queries
# from rag.search_tool import execute_queries

# # previous steps
# planned_queries = plan_queries(TEST_TOPIC, query_count=5)  # keep it cheap
# search_results = execute_queries(planned_queries)

# extracted_viewpoints, extraction_errors = extract_viewpoints(TEST_TOPIC, search_results)
# print(f"\n[extractor] {len(extracted_viewpoints)} viewpoints, {len(extraction_errors)} errors")

# for viewpoint in extracted_viewpoints:
#     print(f"  - {viewpoint['source_name']} [{viewpoint['stance']}]: {viewpoint['key_arguments'][:2]}")
# if extraction_errors:
#     print("  errors:", extraction_errors)

# Step 4: deduplicator
# from rag.deduplicator import deduplicate
# from rag.extractor import extract_viewpoints
# from rag.query_planner import plan_queries
# from rag.search_tool import execute_queries

# # previous steps
# planned_queries = plan_queries(TEST_TOPIC, query_count=5)  # keep it cheap
# search_results = execute_queries(planned_queries)
# extracted_viewpoints, extraction_errors = extract_viewpoints(TEST_TOPIC, search_results)

# deduplicated_viewpoints = deduplicate(TEST_TOPIC, extracted_viewpoints)

# print(f"\n[deduplicator] {len(extracted_viewpoints)} -> {len(deduplicated_viewpoints)} viewpoints after dedup")
# for viewpoint in deduplicated_viewpoints:
#     print(f"  - {viewpoint['source_name']} [{viewpoint['stance']}]")

# ----------------------------------------------------------------------------
#  Step 5: full pipeline
# ----------------------------------------------------------------------------

from rag import build_persona_context

personas = build_persona_context(TEST_TOPIC)
print(f"\n[pipeline] {len(personas)} personas created")
for p in personas:
    print(f"\n  [{p['name']}]")
    for kp in p["keypoints"]:
        print(f"    - {kp}")
