"""Module for structure checks."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, GeomFile
from ..result import RasqcResult, ResultStatus, RasqcResultEncoder
from ..utils import (
    chunk_text,
    get_lines_between_keywords,
    get_text_between_keywords,
    is_valid_number,
)

from pathlib import Path
from typing import List
import re
from json import dumps


@register_check(["ble"])
class BridgeXsData(RasqcChecker):
    """Checker for 2D bridge cross section data.

    Checks if the bank stations are set to a valid point station within the
    cross section and that they are congruent with manning's breaks for the
    channel.
    """

    name = "Bridge XS Data"

    def _check(self, geom: GeomFile) -> RasqcResult:
        """Check the bridge cross section data for a RAS geometry file.

        Parameters
        ----------
            geom: The HEC-RAS geometry file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        if not re.search("Conn Routing Type= 32", geom.content):  # if no bridges
            return RasqcResult(
                result=ResultStatus.OK,
                name=self.name,
                filename=geom.filename,
                message="No bridges located within geometry.",
            )
        struct_info = geom.content.split("Connection=")[1:]

        # args = (text, start delimeter)
        single_line_data = lambda args: tuple(
            float(n) if is_valid_number(n) else None
            for n in get_text_between_keywords(*args, "\n").split(",")
        )

        # args = (text, start delimeter, end delimeter)
        multi_line_data = lambda args: list(
            tuple(float(n) if is_valid_number(n) else None for n in chunk_text(pnt, 8))
            for pnt in chunk_text(str().join(get_lines_between_keywords(*args)), 16)
        )

        bridge_info = {}
        msg_dict = {}
        for si in struct_info:
            if re.search("Conn Routing Type= 32", si):  # if struct is a bridge
                bridge_name = si.split(",", 1)[0].strip()
                bridge_info |= {
                    bridge_name: {
                        "br1": {
                            "se": multi_line_data(
                                (
                                    si,
                                    "Conn BR: BR SE=1",
                                    "Conn BR: BR Bank Stations=1",
                                )
                            ),
                            "banks": single_line_data(
                                (si, "Conn BR: BR Bank Stations=1,")
                            ),
                            "mann": multi_line_data(
                                (si, "Conn BR: BR Mann=1", "Conn BR: BR SE=2")
                            ),
                        },
                        "br2": {
                            "se": multi_line_data(
                                (
                                    si,
                                    "Conn BR: BR SE=2",
                                    "Conn BR: BR Bank Stations=2",
                                )
                            ),
                            "banks": single_line_data(
                                (si, "Conn BR: BR Bank Stations=2,")
                            ),
                            "mann": multi_line_data((si, "Conn BR: BR Mann=2", "=")),
                        },
                        "xs1": {
                            "se": multi_line_data(
                                (
                                    si,
                                    "Conn BR: XS SE=1",
                                    "Conn BR: XS Bank Stations=1",
                                )
                            ),
                            "banks": single_line_data(
                                (si, "Conn BR: XS Bank Stations=1,")
                            ),
                            "mann": multi_line_data(
                                (si, "Conn BR: XS Mann=1", "Conn BR: XS SE=2")
                            ),
                        },
                        "xs2": {
                            "se": multi_line_data(
                                (
                                    si,
                                    "Conn BR: XS SE=2",
                                    "Conn BR: XS Bank Stations=2",
                                )
                            ),
                            "banks": single_line_data(
                                (si, "Conn BR: XS Bank Stations=2,")
                            ),
                            "mann": multi_line_data(
                                (si + "=", "Conn BR: XS Mann=2", "=")
                            ),
                        },
                    }
                }

                for xs in bridge_info[bridge_name].values():
                    mann_dict = {sta: val for sta, val in xs["mann"]}
                    mann_sta_set = set(mann_dict.keys())
                    interior_se_sta_set = set(list(sta for sta, elev in xs["se"])[1:-1])
                    if not set(xs["banks"]).issubset(mann_sta_set):
                        msg_dict.setdefault(bridge_name, set()).add(
                            "bridge XSs without manning's breaks at the banks"
                        )
                    if mann_dict.get(xs["banks"][0]) > 0.06:
                        msg_dict.setdefault(bridge_name, set()).add(
                            "bridge XSs with elevated channel n value(s)"
                        )
                    if not set(xs["banks"]).issubset(interior_se_sta_set):
                        msg_dict.setdefault(bridge_name, set()).add(
                            "bridge XSs without banks set to valid stations"
                        )

        if msg_dict:
            return RasqcResult(
                result=ResultStatus.ERROR,
                name=self.name,
                filename=geom.filename,
                message=dumps(msg_dict, cls=RasqcResultEncoder),
            )

        return RasqcResult(
            name=self.name, result=ResultStatus.OK, filename=geom.filename
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the bridge cross section data for all RAS geometry files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        return list(self._check(geom_file) for geom_file in ras_model.geometries)


@register_check(["ble"])
class OverflowMethod(RasqcChecker):
    name = "Structure Overflow Method"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_hdf_path = ras_model.current_geometry.hdf_path
        filename = geom_hdf_path.name
        if not geom_hdf_path.exists():
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.WARNING,
                message=f"{filename} does not exist within the specified directory",
            )
        with RasGeomHdf(geom_hdf_path) as geom_hdf:
            structs = geom_hdf.structures()
            flags = (
                structs.loc[
                    (structs["Use 2D for Overflow"] == 0)
                    & (structs["Mode"] == "Weir/Gate/Culverts")
                ]["Connection"]
                if not structs.empty
                else structs
            )
        if flags.empty:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.OK,
                message="any applicable structures found use 2d for overflow comps",
            )
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.WARNING,
            message={
                "message": f"{flags.shape[0]} applicable structures found not using 2d for overflow comps",
                "structure names": flags.to_list(),
            },
        )
