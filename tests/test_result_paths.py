from MyCode.core.library.result_paths import ResultPathManager


def test_result_path_roundtrip_relative_absolute():
    base = ResultPathManager.ensure_base()
    rel = "video/demo.mp4"
    abs_path = ResultPathManager.to_absolute(rel)
    assert abs_path.startswith(str(base))
    assert ResultPathManager.to_relative(abs_path) == rel
