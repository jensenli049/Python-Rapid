# Copyright (c) OpenMMLab. All rights reserved.
from .builder import ROTATED_DATASETS
from .dota import DOTADataset

@ROTATED_DATASETS.register_module()
class ScrewsDataset(DOTADataset):
    """MVTEC Screws dataset for detection."""
    CLASSES = ('long_lag_screw', 'lag_wood_screw', 'wood_screw',
               'short_wood_screw', 'shiny_screw', 'black_oxide_screw',
               'nut', 'bolt', 'large_nut', 'nut', 'nut', 'machine_screw', 'short_machine_screw' )
