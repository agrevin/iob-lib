import os

from iob_module import iob_module

from iob_add import iob_add
from iob_or import iob_or


class iob_aoi(iob_module):
    name = "iob_aoi"
    version = "V0.10"
    flows = "sim"
    setup_dir = os.path.dirname(__file__)

    @classmethod
    def _create_submodules_list(cls):
        """Create submodules list with dependencies of this module"""
        super()._create_submodules_list(
            [
                iob_add,
                iob_or,
            ]
        )
