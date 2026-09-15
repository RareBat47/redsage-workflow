# Authorization index repair required

`redsage_v3_assessment_authorization_cohere_v1` was known damaged at migration audit time. Its 183 document/metadata rows were present, but Chroma query failed with `Error creating hnsw segment reader: Nothing found on disk`. Do not report this collection as healthy. Preserve the manifests/receipts for forensic reference and rebuild/revalidate before enabling it in consolidated retrieval. Rebuild may require Cohere embeddings and user approval.
