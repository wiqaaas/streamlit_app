# import os

# # 👇 Qdrant Cloud endpoint (no surrounding quotes!)
# os.environ["QDRANT_URL"]     = "qdrant_url_here"
# os.environ["QDRANT_API_KEY"] = "qdrant_api_key_here"

# # 👇 Your OpenAI key
# os.environ["OPENAI_API_KEY"] = "api_key_here"

# from qdrant_client import QdrantClient

# qdrant = QdrantClient(
#     url=os.environ["QDRANT_URL"],
#     api_key=os.environ["QDRANT_API_KEY"],
# )

# # This should print a list (possibly empty) of your collections:
# print(qdrant.get_collections().collections)                              

# # generate_embeddings_qdrant.py

# import os
# import pandas as pd
# from dotenv import load_dotenv
# from openai import OpenAI
# from qdrant_client import QdrantClient
# from qdrant_client.models import PointStruct, Distance

# # Map each tab to its Excel filename
# FILENAME_MAP = {
#     "Upcoming Match": "df_schedule.xlsx",
#     "Lesson":         "df_lessons.xlsx",
#     "Course":         "df_courses.xlsx",
#     "Article":        "df_article_schedule.xlsx",
# }

# # Compute project & data paths
# DATA_DIR     = os.path.join('./streamlit_app', "data")

# def main():
#     # ─── Load API keys ─────────────────────────────────────────────────────────
#     load_dotenv()
#     API_KEY = os.getenv("OPENAI_API_KEY")
#     if not API_KEY:
#         raise ValueError("Missing OPENAI_API_KEY in environment")

#     openai_client = OpenAI(api_key=API_KEY)
#     qdrant        = QdrantClient(
#         url=os.getenv("QDRANT_URL", "http://localhost:6333"),
#         api_key=os.getenv("QDRANT_API_KEY", None),
#     )

#     # ─── Embedding settings ────────────────────────────────────────────────────
#     EMBEDDING_MODEL = "text-embedding-3-small"
#     VECTOR_SIZE     = 1536
#     DISTANCE        = Distance.COSINE
#     BATCH_SIZE      = 64

#     for category, fname in FILENAME_MAP.items():
#         # Ask user whether to process this category
#         ans = input(f"\nProcess embeddings for category '{category}' (file '{fname}')? [y/n]: ").strip().lower()
#         if ans not in ("y", "yes"):
#             print(f"→ Skipping '{category}'.")
#             continue

#         collection = category.lower().replace(" ", "_")
#         df = pd.read_excel(os.path.join(DATA_DIR, fname))

#         # Ensure collection exists
#         if not qdrant.collection_exists(collection):
#             qdrant.create_collection(
#                 collection_name=collection,
#                 vectors_config={"size": VECTOR_SIZE, "distance": DISTANCE},
#             )

#         # Fetch existing IDs to skip already-processed rows
#         points_list, _ = qdrant.scroll(
#             collection_name=collection,
#             limit=df.shape[0],
#             with_payload=False
#         )
#         existing_ids = {pt.id for pt in points_list}
#         print(f"→ Collection '{collection}' has {len(existing_ids)} rows already indexed.")

#         batch = []
#         for idx, row in df.iterrows():
#             if idx in existing_ids:
#                 continue

#             # Print progress
#             print(f"Processing row index: {idx}")

#             # a) Generate description
#             desc = describe_row(openai_client, row)

#             # b) Embed description
#             emb = openai_client.embeddings.create(
#                 model=EMBEDDING_MODEL,
#                 input=[desc],
#             ).data[0].embedding

#             # c) Prepare payload
#             payload = row.to_dict()
#             payload.update({
#                 "category":    category,
#                 "row_index":   int(idx),
#                 "description": desc,
#             })

#             batch.append(PointStruct(id=idx, vector=emb, payload=payload))

#             # d) Flush batch
#             if len(batch) >= BATCH_SIZE:
#                 qdrant.upsert(collection_name=collection, points=batch)
#                 batch.clear()

#         # Flush any remaining points
#         if batch:
#             qdrant.upsert(collection_name=collection, points=batch)

#         print(f"✅ Indexed new rows into '{collection}'")

#     print("🎉 Done!")


# main()