import sys

sys.path.append("..")
from decanter_ai_sdk.client import Client
import os
from decanter_ai_sdk.enums.evaluators import ClassificationMetric
from decanter_ai_sdk.enums.data_types import DataType
import pandas as pd
from typing import List


def test_iid():
    print("---From test iid---")

    client = Client(
        auth_key="auth_API_key",
        project_id="project_id",
        host="host_url",
        dry_run_type="iid",
    )

    current_path = os.path.dirname(os.path.abspath(__file__))

    train_file_path = os.path.join(current_path, "train.csv")
    train_file = open(train_file_path, "rb")
    train_id = client.upload(train_file, "test_file")

    test_file_path = os.path.join(current_path, "test.csv")
    test_file = open(test_file_path, "rb")
    test_id = client.upload(test_file, "test_file")

    assert isinstance(client.get_table_list(), List)

    exp_name = "exp_name"
    experiment = client.train_iid(
        experiment_name=exp_name,
        experiment_table_id=train_id,
        target="Survived",
        evaluator=ClassificationMetric.AUC,
        custom_feature_types={
            "Pclass": DataType.categorical,
            "Parch": DataType.categorical,
        },
    )

    best_model = experiment.get_best_model()
    assert (
        experiment.get_best_model_by_metric(
            ClassificationMetric.MISCLASSIFICATION
        ).model_id
        == "630439eced266c3d7b2f83f6"
    )
    assert (
        experiment.get_best_model_by_metric(ClassificationMetric.AUC).model_id
        == "630439f8ed266c3d7b2f83fa"
    )
    assert (
        experiment.get_best_model_by_metric(
            ClassificationMetric.LIFT_TOP_GROUP
        ).model_id
        == "630439f6ed266c3d7b2f83f9"
    )
    assert (
        experiment.get_best_model_by_metric(ClassificationMetric.LOGLOSS).model_id
        == "630439fbed266c3d7b2f83fb"
    )
    assert (
        experiment.get_best_model_by_metric(
            ClassificationMetric.MEAN_PER_CLASS_ERROR
        ).model_id
        == "630439fbed266c3d7b2f83fb"
    )

    assert isinstance(experiment.get_model_list(), List)
    assert experiment.experiment_info()["name"] == exp_name

    predict = client.predict_iid(
        keep_columns=[], non_negative=False, test_table_id=test_id, model=best_model
    )

    assert isinstance(predict.get_predict_df(), pd.DataFrame)