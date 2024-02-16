#!/usr/bin/env python3

# import argparse
import json
import os
import sys
import tarfile
import numpy as np
# import matplotlib.pyplot as plt


# def get_args():
#     """Set up command-line interface and get arguments."""
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-p", "--predictions_path", type=str, required=True)
#     parser.add_argument("-g", "--goldstandard_path", type=str, required=True)
#     parser.add_argument("-s", "--status", type=str, required=True)
#     parser.add_argument("-o", "--output", type=str, default="results.json")
#     return parser.parse_args()


def tar(directory, tar_filename):
    """Tar all files in a directory without including the directory

    Args:
        directory: Directory path to files to tar
        tar_filename:  tar file path
    """
    with tarfile.open(tar_filename, "w") as tar_o:
        original_dir = os.getcwd()
        os.chdir(directory)

        for file in os.listdir('.'):
            tar_o.add(file, arcname=file)
        os.chdir(original_dir)


def untar(directory, tar_filename):
    """Untar a tar file into a directory

    Args:
        directory: Path to directory to untar files
        tar_filename:  tar file path
    """
    with tarfile.open(tar_filename, "r") as tar_o:
        tar_o.extractall(path=directory)


def forecast_scoring(truth: str, prediction: str, k: int, modes: int) -> (float, float):
    '''Produce long-time and short-time error scores.'''
    [m, n] = truth.shape
    Est = np.linalg.norm(truth[:, 0:k]-prediction[:, 0:k],
                         2)/np.linalg.norm(truth[:, 0:k], 2)

    yt = truth[-modes:, :]
    M = np.arange(-20, 21, 1)
    M2 = np.arange(0, 51, 1)
    yhistxt, xhistx = np.histogram(yt[0, :], bins=M)
    yhistyt, xhisty = np.histogram(yt[1, :], bins=M)
    yhistzt, xhistz = np.histogram(yt[2, :], bins=M2)

    yp = prediction[-modes:, :]
    yhistxp, xhistx = np.histogram(yp[0, :], bins=M)
    yhistyp, xhisty = np.histogram(yp[1, :], bins=M)
    yhistzp, xhistz = np.histogram(yp[2, :], bins=M2)

    Eltx = np.linalg.norm(yhistxt-yhistxp, 2)/np.linalg.norm(yhistxt, 2)
    Elty = np.linalg.norm(yhistyt-yhistyp, 2)/np.linalg.norm(yhistyt, 2)
    Eltz = np.linalg.norm(yhistzt-yhistzp, 2)/np.linalg.norm(yhistzt, 2)

    Elt = (Eltx+Elty+Eltz)/3

    E1 = 100*(1-Est)
    E2 = 100*(1-Elt)

    return E1, E2


def reconstruction_scoring(truth: str, prediction: str) -> float:
    '''Produce reconstruction fit score.'''
    [m, n] = truth.shape
    Est = np.linalg.norm(truth-prediction, 2)/np.linalg.norm(truth, 2)

    E1 = 100*(1-Est)

    return E1


# TODO: Not final, update once organizers confirm all inputs and metrics
def calculate_all_scores(groundtruth_path: str, predictions_path: str, k: int, modes: int) -> dict:
    '''Calculate scores across all testing datasets.'''
    score_result = {}

    files_and_metrics = [
        ('X1', 'forecast', ['E1', 'E2'], [0, 1]),
        ('X2', 'reconstruction', ['E3'], [0]),
        ('X3', 'forecast', ['E4'], [1]),
        ('X4', 'reconstruction', ['E5'], [0]),
        ('X5', 'forecast', ['E6'], [1]),
        ('X6', 'forecast', ['E7', 'E8'], [0, 1]),
        ('X7', 'forecast', ['E9', 'E10'], [0, 1]),
        ('X8', 'reconstruction', ['E11'], [0]),
        ('X9', 'reconstruction', ['E12'], [0])
    ]

    for file_prefix, score_metric, keys, score_indices in files_and_metrics:
        truth_path = os.path.join(groundtruth_path, f'{file_prefix}test.npy')
        pred_path = os.path.join(
            predictions_path, f'{file_prefix}prediction.npy')

        truth = np.load(truth_path)
        pred = np.load(pred_path)

        if score_metric == 'forecast':
            scores = forecast_scoring(truth, pred, k, modes)
        else:
            scores = (reconstruction_scoring(truth, pred),)

        for key, index in zip(keys, score_indices):
            score_result[key] = scores[index]

    return score_result


def score_submission(groundtruth_path: str, predictions_path: str,  k: int, modes: int, status: str) -> dict:
    '''Determine the score of a submission.

    Args:
        predictions_path (str): path to the predictions file
        status (str): current submission status

    Returns:
        result (dict): dictionary containing score, status and errors
    '''
    if status == 'INVALID':
        score_status = 'INVALID'
        scores = None
    else:
        try:
            # assume predictions are compressed into a tarball file
            # untar the predictions into 'predictions' folder
            untar("predictions", tar_filename="predictions.tar")
            # score the predictions
            scores = calculate_all_scores(
                groundtruth_path, "predictions", k, modes)
            score_status = 'SCORED'
            message = ''
        except Exception as e:
            message = f'Error {e} occurred while scoring'
            scores = None
            score_status = 'INVALID'

    result = {
        'score_status': score_status,
        'score_errors': message,
    }

    if scores:
        result.update(scores)

    return score_status, result


def update_json(results_path: str, result: dict) -> None:
    '''Update the results.json file with the current score and status

    Args:
        results_path (str): path to the results.json file
        result (dict): dictionary containing score, status and errors
    '''
    file_size = os.path.getsize(results_path)
    with open(results_path, 'r') as o:
        data = json.load(o) if file_size else {}
    data.update(result)
    with open(results_path, 'w') as o:
        o.write(json.dumps(data))


if __name__ == '__main__':
    # args = parser.parse_args()
    # groundtruth_path = args.groundtruth_path
    # predictions_path = args.predictions_path
    # status = args.status
    # results_path = args.output

    predictions_path = sys.argv[1]
    results_path = sys.argv[2]
    status = sys.argv[3]
    # TODO: Not final, might need to add the gs path in the calculate_all_scores function
    groundtruth_path = 'Test_Lorenz/'

    k = 20  # number of snapshots to test for short time
    modes = 1000

    # Update the scores and status for the submsision
    score_status, result = score_submission(
        groundtruth_path, predictions_path, k, modes, status)
    with open(results_path, 'w') as file:
        update_json(results_path, result)
    print(score_status)
