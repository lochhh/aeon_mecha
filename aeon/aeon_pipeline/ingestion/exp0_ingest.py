from aeon.aeon_pipeline import subject, experiment, tracking


# ---------------- Subject -----------------
subject.Subject.insert([
    {'subject': 'Dario', 'sex': 'U', 'subject_birth_date': '2021-01-01'},
    {'subject': 'dfs', 'sex': 'U', 'subject_birth_date': '2021-01-01'},
    {'subject': 'f', 'sex': 'U', 'subject_birth_date': '2021-01-01'},
    {'subject': 'BAA-1099590', 'sex': 'U', 'subject_birth_date': '2021-01-01'},
    {'subject': 'BAA-1099591', 'sex': 'U', 'subject_birth_date': '2021-01-01'},
    {'subject': 'BAA-1099592', 'sex': 'U', 'subject_birth_date': '2021-01-01'}
])


# ---------------- Experiment -----------------
experiment.Experiment.insert1({'experiment_name': 'exp0-r0',
                               'experiment_start_time': '2021-03-25 15-00-00',
                               'experiment_description': 'experiment 0',
                               'arena_name': 'circle-2m',
                               'lab': 'SWC',
                               'location': 'room-0'})
experiment.Experiment.Subject.insert([
    {'experiment_name': 'exp0-r0', 'subject': 'BAA-1099590'},
    {'experiment_name': 'exp0-r0', 'subject': 'BAA-1099591'},
    {'experiment_name': 'exp0-r0', 'subject': 'BAA-1099592'}])
experiment.Experiment.Directory.insert1({'experiment_name': 'exp0-r0',
                                         'directory_type': 'raw',
                                         'repository_name': 'ceph_aeon',
                                         'directory_path': 'test2/data/2021-03-25T15-05-34'})
experiment.Experiment.Directory.insert1({'experiment_name': 'exp0-r0',
                                         'directory_type': 'preprocessing',
                                         'repository_name': 'ceph_aeon',
                                         'directory_path': 'aeon/preprocessing/experiment0'})

# ---------------- Equipment -----------------
# Two cameras: FrameTop and FrameSide
experiment.ExperimentCamera.insert([
    {'experiment_name': 'exp0-r0', 'camera_id': 0,
     'camera_install_time': '2021-03-25 15-00-00', 'sampling_rate': 50},
    {'experiment_name': 'exp0-r0', 'camera_id': 1,
     'camera_install_time': '2021-03-25 15-00-00', 'sampling_rate': 125}])

# Single foodpatch (id=0) removed and reinstalled
experiment.ExperimentFoodPatch.insert([
    {'experiment_name': 'exp0-r0', 'food_patch_id': 0,
     'food_patch_install_time': '2021-03-25 15-00-00'}])
experiment.ExperimentFoodPatch.Position.insert([
    {'experiment_name': 'exp0-r0', 'food_patch_id': 0,
     'food_patch_install_time': '2021-03-25 15-00-00',
     'food_patch_position_x': 1,
     'food_patch_position_y': 1}])
experiment.ExperimentFoodPatch.RemovalTime.insert([
    {'experiment_name': 'exp0-r0', 'food_patch_id': 0,
     'food_patch_install_time': '2021-03-25 15-00-00',
     'food_patch_remove_time': '2021-03-26 12:00:00'}])

experiment.ExperimentFoodPatch.insert([
    {'experiment_name': 'exp0-r0', 'food_patch_id': 0,
     'food_patch_install_time': '2021-03-26 12:00:00'}])
experiment.ExperimentFoodPatch.Position.insert([
    {'experiment_name': 'exp0-r0', 'food_patch_id': 0,
     'food_patch_install_time': '2021-03-26 12:00:00',
     'food_patch_position_x': 1,
     'food_patch_position_y': 1}])


# ---------------- Auto Ingestion -----------------
settings = {'suppress_errors': True}

experiment.TimeBin.generate_timebins(experiment_name='exp0-r0')
experiment.SubjectEnterExit.populate(**settings)
experiment.Epoch.populate(**settings)
experiment.FoodPatchEvent.populate(**settings)
tracking.SubjectPosition.populate(**settings)
tracking.EpochPosition.populate(**settings)