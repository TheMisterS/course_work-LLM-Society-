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


TEST_TOPIC = "Legalizing same-sex civil partnerships in Lithuania"

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

# Step 5: stance_selector
# from rag.deduplicator import deduplicate
# from rag.extractor import extract_viewpoints
# from rag.query_planner import plan_queries
# from rag.search_tool import execute_queries
# from rag.stance_selector import select_by_stance

# # previous steps
# planned_queries = plan_queries(TEST_TOPIC, query_count=5)
# search_results = execute_queries(planned_queries)
# extracted_viewpoints, _ = extract_viewpoints(TEST_TOPIC, search_results)
# deduplicated_viewpoints = deduplicate(TEST_TOPIC, extracted_viewpoints)

# selected = select_by_stance(deduplicated_viewpoints)
# print(f"\n[stance_selector] {len(selected)} viewpoints selected")
# for vp in selected:
#     print(f"  - {vp['source_name']} [{vp['stance']}]")

# Step 6: background_fetcher
# from rag.background_fetcher import fetch_backgrounds

# enriched = fetch_backgrounds(selected)
# for vp in enriched:
#     print(f"  - {vp['source_name']}: {vp.get('_enrichment_raw', '')[:80]}")

# Step 7: persona_synthesis
# from rag.persona_synthesis import synthesize_personas

# personas = synthesize_personas(TEST_TOPIC, enriched)
# for p in personas:
#     print(f"\n  [{p['name']} / {p['affiliation']}] {p['stance']}")
#     print(f"  role_desc:  {p['role_desc']}")
#     print(f"  background: {p['background']}")

#  Step 8: full pipeline
from rag import build_persona_context

personas = build_persona_context(TEST_TOPIC)
print(f"\n[pipeline] {len(personas)} personas created")
for p in personas:
    print(f"\n  [{p['name']} / {p['affiliation']}] {p['stance']}")
    print(f"  role_desc:  {p['role_desc']}")
    print(f"  background: {p['background']}")
    for kp in p["keypoints"]:
        print(f"    - {kp}")
