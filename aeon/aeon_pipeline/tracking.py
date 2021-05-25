import datajoint as dj
import pathlib
import pandas as pd
import datetime
import numpy as np

from aeon.preprocess import exp0_api

from . import experiment
from . import get_schema_name


schema = dj.schema(get_schema_name('tracking'))


@schema
class AnimalPosition(dj.Imported):
    definition = """
    -> experiment.SubjectEpoch
    ---
    timestamps:        longblob  # (s) timestamps of the position data, w.r.t the start of the TimeBlock containing this Epoch
    position_x:        longblob  # (m) animal's x-position, in the arena's coordinate frame
    position_y:        longblob  # (m) animal's y-position, in the arena's coordinate frame
    position_z=null:   longblob  # (m) animal's z-position, in the arena's coordinate frame
    speed=null:        longblob  # (m/s) speed
    """

    def make(self, key):
        time_bin_start, time_bin_end = (experiment.TimeBin * experiment.SubjectEpoch
                                        & key).fetch1('time_bin_start', 'time_bin_end')
        epoch_start, epoch_end = (experiment.SubjectEpoch & key).fetch1(
            'epoch_start', 'epoch_end')

        file_repo, file_path = (experiment.TimeBin.File * experiment.DataRepository
                                * experiment.SubjectEpoch
                                & 'data_category = "VideoCamera"'
                                & 'file_name LIKE "FrameTop%.avi"'
                                & key).fetch('repository_path', 'file_path', limit=1)
        file_path = pathlib.Path(file_repo[0]) / file_path[0]
        # Retrieve FrameTop video timestamps for this TimeBin
        video_timestamps = exp0_api.harpdata(file_path.parent.parent.as_posix(),
                                             device='VideoEvents',
                                             register=68,
                                             start=pd.Timestamp(time_bin_start),
                                             end=pd.Timestamp(time_bin_end))
        video_timestamps = video_timestamps[video_timestamps[0] == 4]  # frametop timestamps
        # Read preprocessed position data for this TimeBin and animal
        preprocess_dir = pathlib.Path('/ceph/aeon/aeon/preprocessing/experiment0') / key['subject']
        tracking_dfs = []
        for frametop_csv in preprocess_dir.rglob('FrameTop.csv'):
            parent_timestamp = datetime.datetime.strptime(
                frametop_csv.parent.name, '%Y-%m-%dT%H-%M-%S')
            if parent_timestamp < time_bin_start or parent_timestamp >= time_bin_end:
                continue

            clips_csv = frametop_csv.parent / 'FrameTop-Clips.csv'
            clips = pd.read_csv(clips_csv)
            frametop_df = pd.read_csv(frametop_csv,
                                      names=['X', 'Y', 'Orientation', 'MajorAxisLength',
                                             'MinoxAxisLength', 'Area'])

            matched_clip_idx = clips[clips.path == file_path.as_posix()].index[0]
            matched_clip = clips.iloc[matched_clip_idx]

            harp_start_idx = matched_clip.start
            harp_end_idx = harp_start_idx + matched_clip.duration

            tracking_data_starting_idx = 0 if matched_clip_idx == 0 else clips.iloc[matched_clip_idx - 1].duration
            tracking_data = frametop_df[tracking_data_starting_idx:tracking_data_starting_idx + matched_clip.duration].copy()
            tracking_data['timestamps'] = video_timestamps[harp_start_idx:harp_end_idx].index
            tracking_data.set_index('timestamps', inplace=True)
            tracking_dfs.append(tracking_data)

        if not tracking_dfs:
            return

        timebin_tracking = pd.concat(tracking_dfs, axis=1).sort_index()
        epoch_tracking = timebin_tracking[np.logical_and(timebin_tracking.index >= epoch_start,
                                                         timebin_tracking.index < epoch_end)]

        timestamps = (epoch_tracking.index.values - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
        timestamps = np.array([datetime.datetime.utcfromtimestamp(t) for t in timestamps])

        self.insert1({**key,
                      'timestamps': timestamps,
                      'position_x': epoch_tracking.X.values,
                      'position_y': epoch_tracking.Y.values})


@schema
class EpochPosition(dj.Computed):
    definition = """  # All unique positions (x,y,z) of an animal in a given epoch
    -> AnimalPosition
    x: decimal(5, 3)
    y: decimal(5, 3)
    z: decimal(5, 3)
    """

    def make(self, key):
        unique_positions = set((AnimalPosition & key).fetch1(
            'position_x', 'position_y', 'position_z'))
        self.insert([{**key, 'x': x, 'y': y, 'z': z}
                     for x, y, z in unique_positions])
