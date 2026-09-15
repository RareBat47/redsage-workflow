from KB.consolidated_retrieval import KBProfile, search_consolidated


class Embedder:
    def embed_query(self, query):
        return [0.1, 0.2]


class Collection:
    def __init__(self, rows):
        self.rows = rows

    def query(self, **kwargs):
        return self.rows


class Client:
    def __init__(self, collections):
        self.collections = collections

    def get_collection(self, name):
        return self.collections[name]


class FreshClientFactory:
    def __init__(self, collections):
        self.collections = collections
        self.created = 0

    def get_client(self):
        self.created += 1
        return Client(self.collections)


def result_rows(*items):
    return {
        "ids": [[item["id"] for item in items]],
        "documents": [[item["text"] for item in items]],
        "metadatas": [[item["metadata"] for item in items]],
        "distances": [[item.get("distance", 0.1) for item in items]],
    }


def metadata(path, source_type="owasp", approved=True, unsafe=False, scope="authorized_engagement"):
    return {
        "path": path, "source_id": "s", "source_version_id": "v", "document_id": "d",
        "title": "Guide", "locator": path, "source_type": source_type,
        "content_class": "reference", "environment_scope": scope,
        "is_approved": approved, "is_unsafe": unsafe, "trust_level": 4,
        "content_hash": "a" * 64,
    }


def test_consolidated_search_combines_profiles_and_writes_receipt(tmp_path):
    client = Client({
        "assessment": Collection(result_rows({"id": "a", "text": "authorization evidence", "metadata": metadata("03_owasp/a.md")})),
        "identity": Collection(result_rows({"id": "i", "text": "session evidence", "metadata": metadata("03_owasp/i.md")})),
    })
    result = search_consolidated(
        "authorized authentication and authorization review",
        profiles=[KBProfile("assessment", "assessment", "assessment-v1"), KBProfile("identity", "identity", "identity-v1")],
        client=client, embedder=Embedder(), receipt_directory=tmp_path,
    )
    assert len(result["citations"]) == 2
    assert {x["kb_domain"] for x in result["citations"]} == {"assessment", "identity"}
    assert result["candidate_count"] == 2
    assert result["filtered_count"] == 0
    assert (tmp_path / f"{result['query_id']}.json").exists()


def test_consolidated_search_excludes_unapproved_unsafe_and_lab_content(tmp_path):
    client = Client({
        "assessment": Collection(result_rows(
            {"id": "ok", "text": "ok", "metadata": metadata("03_owasp/ok.md")},
            {"id": "draft", "text": "draft", "metadata": metadata("03_owasp/draft.md", approved=False)},
            {"id": "unsafe", "text": "unsafe", "metadata": metadata("03_owasp/unsafe.md", unsafe=True)},
            {"id": "lab", "text": "lab", "metadata": metadata("08_lab_ctf/lab.md", source_type="lab", scope="lab_only")},
        )),
    })
    result = search_consolidated("authorized web assessment", profiles=[KBProfile("assessment", "assessment", "assessment-v1")], client=client, embedder=Embedder(), receipt_directory=tmp_path)
    assert [x["chunk_id"] for x in result["citations"]] == ["ok"]
    assert result["filtered_count"] == 3
    assert result["filtered_reasons"] == {"lab_excluded": 1, "not_approved": 1, "unsafe": 1}


def test_duplicate_chunk_ids_keep_distinct_citation_keys(tmp_path):
    rows = result_rows({"id": "same", "text": "guidance", "metadata": metadata("03_owasp/item.md")})
    client = Client({"one": Collection(rows), "two": Collection(rows)})
    result = search_consolidated("authorized guidance", profiles=[KBProfile("one", "web", "v1"), KBProfile("two", "api", "v1")], client=client, embedder=Embedder(), receipt_directory=tmp_path)
    assert len({item["citation_key"] for item in result["citations"]}) == 2
    assert {item["chunk_id"] for item in result["citations"]} == {"same"}
