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
#     # ─── Load environment variables ────────────────────────────────────────────
#     load_dotenv()
#     API_KEY = os.getenv("OPENAI_API_KEY")
#     if not API_KEY:
#         raise ValueError("Missing OPENAI_API_KEY in environment")

#     # ─── Instantiate clients ──────────────────────────────────────────────────
#     openai_client = OpenAI(api_key=API_KEY)
#     qdrant = QdrantClient(
#         url=os.getenv("QDRANT_URL", "http://localhost:6333"),
#         api_key=os.getenv("QDRANT_API_KEY", None),
#     )

#     EMBEDDING_MODEL = "text-embedding-ada-002"
#     DISTANCE        = Distance.COSINE

#     # ─── Process each category interactively ──────────────────────────────────
#     for category, fname in FILENAME_MAP.items():
#         answer = input(f"\nProcess embeddings for category '{category}' "
#                        f"(file '{fname}')? [y/n]: ").strip().lower()
#         if answer not in ("y", "yes"):
#             print(f"→ Skipping '{category}'.")
#             continue

#         collection_name = category.lower().replace(" ", "_")
#         file_path = os.path.join(DATA_DIR, fname)
#         print(f"→ Loading '{fname}' for category '{category}'…")
#         df = pd.read_excel(file_path)

#         # 1) Create collection if it doesn't exist
#         if not qdrant.collection_exists(collection_name):
#             qdrant.create_collection(
#                 collection_name=collection_name,
#                 vectors_config={"size": 1536, "distance": DISTANCE},
#             )
#             print(f"   Created collection '{collection_name}'.")
#         else:
#             print(f"   Collection '{collection_name}' already exists; using it.")

#         # 2) Compute & upsert embeddings in batches
#         BATCH_SIZE = 64
#         batch = []
#         for idx, row in df.iterrows():
#             # a) Build row text
#             text = "  ".join(f"{col}: {row[col]}" for col in df.columns)
#             # b) Embed
#             resp = openai_client.embeddings.create(
#                 model=EMBEDDING_MODEL,
#                 input=[text],
#             )
#             emb = resp.data[0].embedding
#             # c) Prepare payload
#             payload = row.to_dict()
#             payload.update({
#                 "category":  category,
#                 "row_index": int(idx),
#             })
#             # d) Append point
#             batch.append(PointStruct(id=idx, vector=emb, payload=payload))

#             # e) Flush batch
#             if len(batch) >= BATCH_SIZE:
#                 qdrant.upsert(collection_name=collection_name, points=batch)
#                 batch = []

#         # 3) Flush remaining
#         if batch:
#             qdrant.upsert(collection_name=collection_name, points=batch)

#         print(f"✅ Indexed {len(df)} rows into '{collection_name}'.")

#     print("\n🎉 All done!")

# main()