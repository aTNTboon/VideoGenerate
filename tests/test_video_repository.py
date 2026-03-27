from MyCode.core.repositories.video_repository import SqlVideoRepository


class FakeDB:
    def __init__(self):
        self.called = None

    def get_pending_videos(self, step):
        self.called = ("get_pending_videos", step)
        return []

    def query_videos(self, filters):
        self.called = ("query_videos", filters)
        return []

    def selectByText(self, text):
        self.called = ("selectByText", text)
        return []

    def delete_from_id(self, id, table):
        self.called = ("delete_from_id", id, table)


def test_repository_delegates_to_db_methods():
    db = FakeDB()
    repo = SqlVideoRepository(db)

    repo.get_pending_videos(1)
    assert db.called == ("get_pending_videos", 1)

    repo.query_videos({"step": 1})
    assert db.called == ("query_videos", {"step": 1})

    repo.select_by_text("abc")
    assert db.called == ("selectByText", "abc")

    repo.delete_video_by_id(9)
    assert db.called == ("delete_from_id", 9, "videos")
