import pytest
import json
from moto import mock_aws
import boto3
import os
from dotenv import load_dotenv
from src.extract import extract_from_db_write_to_s3
from pprint import pprint
from utilities.utils_for_testing import (
    create_s3_bucket,
    upload_to_s3,
    view_bucket_contents,
    credentials_storer,
    secret_retriever
)


load_dotenv()


@pytest.fixture()
def s3_client():
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture()
def s3_resource():
    with mock_aws():
        yield boto3.resource("s3")


@pytest.fixture()
def secretsmanager_client():
    with mock_aws():
        yield boto3.client("secretsmanager")


@pytest.fixture(scope="function")
def create_secrets(secretsmanager_client):
    secret_string={
        "username": os.getenv("Username"),
        "password": os.getenv("Password"),
        "host": os.getenv("Hostname"),
        "port": os.getenv("Port"),
        "dbname": os.getenv("Database")
    }
    secret=json.dumps(secret_string)
    secretsmanager_client.create_secret(
        Name="project-onyx/totesys-db-login", SecretString=secret
    )


def test_get_secret(secretsmanager_client):
    credentials_storer("secret", "bob", "marley", secretsmanager_client)
    assert secret_retriever("secret", secretsmanager_client) == {
        "username": "bob",
        "password": "marley",
    }


class TestExtract:
    def test_extract_writes_to_s3(self, s3_client, create_secrets):
        s3_client.create_bucket(Bucket="bucket", CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-2',
            'Location': {
                'Type': 'AvailabilityZone',
                'Name': 'string'
            }})
        result = extract_from_db_write_to_s3(s3_client, "bucket")
        expected_list_bucket = s3_client.list_objects(Bucket="bucket")['Contents']
        expected = [bucket["Key"] for bucket in expected_list_bucket]
        print(result)
        assert result == expected
    
    @pytest.mark.skip()
    def test_initial_extract_entire_db_into_s3(self, s3_client, create_secrets):
        s3_client.create_bucket(Bucket="bucket", CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-2',
            'Location': {
                'Type': 'AvailabilityZone',
                'Name': 'string'
            }})
        result = extract_from_db_write_to_s3(s3_client, "bucket")
        expected_list_bucket = s3_client.list_objects(Bucket="bucket")['Contents']
        expected = [bucket["Key"] for bucket in expected_list_bucket]
        print(result)
        assert result == expected

