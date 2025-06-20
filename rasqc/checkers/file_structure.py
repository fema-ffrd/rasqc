"""Checks related to the file structure of a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from json import dumps


@register_check(["ble"])
class FileStructure(RasqcChecker):
    """HEC-RAS model file structure checker.

    Reports the file structure of the target HEC-RAS model to be reviewed
    by the user. Result status is 'note'.
    """

    name = "File Structure"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute file structure check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        msg_dict = {
            "filename": ras_model.prj_file.filename,
            "title": ras_model.prj_file.title,
            "description": ras_model.prj_file.description,
            "plans": {},
        }
        for plan in ras_model.plans:
            geom = ras_model.geom_files[plan.geom_file_ext]
            flow = ras_model.unsteady_flow_files[plan.flow_file_ext]
            msg_dict["plans"][plan.path.suffix.strip(".")] = {
                "filename": plan.filename,
                "title": plan.title,
                "short id": plan.short_id,
                "description": plan.description,
                "geometry": {
                    "filename": geom.filename,
                    "title": geom.title,
                    "description": geom.description,
                },
                "unsteady": {
                    "filename": flow.filename,
                    "title": flow.title,
                    "description": flow.description,
                },
            }
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict),
        )
