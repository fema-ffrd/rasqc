import json
from rasqc.result import RasqcResult, ResultStatus, RasqcResultEncoder
from geopandas import GeoDataFrame
import pandas as pd
from shapely.geometry import Point


def test_result_status_enum():
    """Test that ResultStatus enum works correctly."""
    assert ResultStatus.OK.value == "ok"
    assert ResultStatus.WARNING.value == "warning"
    assert ResultStatus.ERROR.value == "error"


def test_result_basic():
    """Test basic RasqcResult functionality."""
    result = RasqcResult(result=ResultStatus.OK, name="Test Check", filename="test.prj")

    assert result.result == ResultStatus.OK
    assert result.name == "Test Check"
    assert result.filename == "test.prj"
    assert result.message is None
    assert result.gdf is None


def test_result_with_message():
    """Test RasqcResult with message."""
    result = RasqcResult(
        result=ResultStatus.WARNING,
        name="Test Check",
        filename="test.prj",
        message="This is a warning message",
    )

    assert result.result == ResultStatus.WARNING
    assert result.name == "Test Check"
    assert result.filename == "test.prj"
    assert result.message == "This is a warning message"
    assert result.gdf is None


def test_result_with_gdf():
    """Test RasqcResult with GeoDataFrame."""
    # Create a simple GeoDataFrame
    df = pd.DataFrame({"id": [1, 2], "value": [10, 20]})
    geometry = [Point(0, 0), Point(1, 1)]
    gdf = GeoDataFrame(df, geometry=geometry)

    result = RasqcResult(
        result=ResultStatus.ERROR,
        name="Test Check",
        filename="test.prj",
        message="This is an error message",
        gdf=gdf,
    )

    assert result.result == ResultStatus.ERROR
    assert result.name == "Test Check"
    assert result.filename == "test.prj"
    assert result.message == "This is an error message"
    assert result.gdf is not None
    assert len(result.gdf) == 2


def test_result_encoder():
    """Test RasqcResultEncoder for JSON serialization."""
    # Create a result with enum
    result = RasqcResult(
        result=ResultStatus.ERROR,
        name="Test Check",
        filename="test.prj",
        message="This is an error message",
    )
    output = {
        "model": "test.prj",
        "checksuite": "test",
        "timestamp": "2023-08-01T12:00:00Z",
        "checks": [result.to_dict()],
    }

    # Serialize to JSON
    json_str = json.dumps(output, cls=RasqcResultEncoder)
    json_obj = json.loads(json_str)

    # Check serialization
    check_result = json_obj["checks"][0]
    assert check_result["result"] == "error"  # Enum converted to string value
    assert check_result["name"] == "Test Check"
    assert check_result["filename"] == "test.prj"
    assert check_result["message"] == "This is an error message"
    assert check_result["gdf"] is None


def test_result_encoder_with_gdf():
    """Test RasqcResultEncoder with GeoDataFrame."""
    # Create a simple GeoDataFrame
    df = pd.DataFrame({"id": [1], "value": [10]})
    geometry = [Point(0, 0)]
    gdf = GeoDataFrame(df, geometry=geometry)

    result = RasqcResult(
        result=ResultStatus.WARNING,
        name="Test Check",
        filename="test.prj",
        message="This is a warning message",
        gdf=gdf,
    )
    output = {
        "model": "test.prj",
        "checksuite": "test",
        "timestamp": "2023-08-01T12:00:00Z",
        "checks": [result.to_dict()],
    }

    # Serialize to JSON
    json_str = json.dumps(output, cls=RasqcResultEncoder)
    json_obj = json.loads(json_str)

    # Check serialization
    check_result = json_obj["checks"][0]
    assert check_result["result"] == "warning"
    assert check_result["name"] == "Test Check"
    assert check_result["filename"] == "test.prj"
    assert check_result["message"] == "This is a warning message"
    assert check_result["gdf"] is not None
    assert "features" in check_result["gdf"]  # GeoJSON format
