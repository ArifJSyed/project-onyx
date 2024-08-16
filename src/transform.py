import pytest
import json
from moto import mock_aws
import boto3
import os
from dotenv import load_dotenv
import pandas as pd
from src.extract import extract_from_db_write_to_s3
from pprint import pprint


def transform(source_bucket, output_bucket):
    s3_client = boto3.client("s3")
    ingested_data_files = s3_client.list_objects(Bucket=source_bucket)["Contents"]
    ingested_data_files_names = [file_data["Key"] for file_data in ingested_data_files]

    expected = [
        "counterparty",
        "currency",
        "department",
        "design",
        "staff",
        "sales_order",
        "address",
        "payment",
        "purchase_order",
        "payment_type",
        "transaction",
    ]

    file_dict = {name: [] for name in expected}

    for filename in ingested_data_files_names:
        for key in file_dict.keys():
            if filename.startswith(key):
                file_dict[key].append(filename)
                break

    for table, files in file_dict.items():
        if table == "address":
            file = files[0]
            json_file = s3_client.get_object(Bucket=source_bucket, Key=file)
            json_contents = json_file["Body"].read().decode("utf-8")
            data = json.loads(json_contents)["address"]

            df = pd.DataFrame(data)
            df = df.rename(columns={"address_id": "location_id"}).drop(
                ["created_at", "last_updated"], axis=1
            )
            df.to_parquet("dim_location.parquet")
            s3_client.upload_file(
                "dim_location.parquet", output_bucket, "dim_location.parquet"
            )
        elif table == "design":
            file = files[0]
            json_file = s3_client.get_object(Bucket=source_bucket, Key=file)
            json_contents = json_file["Body"].read().decode("utf-8")
            data = json.loads(json_contents)["design"]

            df = pd.DataFrame(data)
            df = df.drop(["created_at", "last_updated"], axis=1)
            df.to_parquet("dim_design.parquet")
            s3_client.upload_file(
                "dim_design.parquet", output_bucket, "dim_design.parquet"
            )
        elif table == "currency":
            file = files[0]
            json_file = s3_client.get_object(Bucket=source_bucket, Key=file)
            json_contents = json_file["Body"].read().decode("utf-8")
            data = json.loads(json_contents)["currency"]

            df = pd.DataFrame(data)
            df = df.drop(["created_at", "last_updated"], axis=1).assign(
                currency_name=[
                    "British Pound Sterling",
                    "United States Dollar",
                    "Euros",
                ]
            )
            df.to_parquet("dim_currency.parquet")
            s3_client.upload_file(
                "dim_currency.parquet", output_bucket, "dim_currency.parquet"
            )
