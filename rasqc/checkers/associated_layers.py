from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class AssociatedLayers(RasqcChecker):
    name = "Associated Layers"

    def run(self, ras_model: RasModel) -> RasqcResult:
        filenames = []
        messages = []
        for geom_hdf_path in ras_model.geometry_hdf_paths:
            filenames.append(geom_hdf_path.name)
            geom_hdf = RasGeomHdf(geom_hdf_path)
            geom_attrs = geom_hdf.get_geom_attrs()
            messages.append(
                {
                    "terrain": geom_attrs["Terrain Filename"]
                    if "Terrain Filename" in geom_attrs
                    else None,
                    "land cover": geom_attrs["Land Cover Filename"]
                    if "Land Cover Filename" in geom_attrs
                    else None,
                    "infiltration": geom_attrs["Infiltration Filename"]
                    if "Infiltration Filename" in geom_attrs
                    else None,
                }
            )
        return RasqcResult(
            name=self.name,
            filename=filenames,
            result=ResultStatus.NOTE,
            message=messages,
        )
