import boto3
import logging
import json
from typing import Any, Dict
from core import utils
from core import constants as cst


class AwsClient():
    def __init__(self) -> None:
        env_vars = self.get_aws_env_vars()
        self.aws_access_key_id = env_vars.get(cst.AWS_ACCESS_KEY_ID_ENV_VAR)
        self.aws_access_secret = env_vars.get(cst.AWS_ACCESS_SECRET_ENV_VAR)
        self.s3_bucket = env_vars.get(cst.AWS_S3_BUCKET_NAME)
        self.region_name = env_vars.get(cst.AWS_REGION_NAME)
        self.s3_client = boto3.client(
            's3', aws_access_key_id=env_vars.get(cst.AWS_ACCESS_KEY_ID_ENV_VAR), aws_secret_access_key=env_vars.get(cst.AWS_ACCESS_SECRET_ENV_VAR), region_name=env_vars.get(cst.AWS_REGION_NAME))

    @staticmethod
    def get_aws_env_vars():
        logging.info(f'Getting the S3 details name from env var')
        env_vars = utils.get_env_variables(
            [
                cst.AWS_ACCESS_KEY_ID_ENV_VAR, cst.AWS_ACCESS_SECRET_ENV_VAR, cst.AWS_S3_BUCKET_NAME, cst.AWS_REGION_NAME
            ])

        return env_vars

    def read_from_s3(self, bucket_file: str) -> Any:
        logging.info(f'Reading file {bucket_file} from {self.s3_bucket}')
        try:
            obj = self.s3_client.Object(self.s3_bucket, bucket_file)
            data = obj.get()['Body'].read()
            return data
        except Exception as ex:
            logging.error(
                f'An error occurred when reading file {bucket_file} from {self.s3_bucket}')
        return None

    def save_to_s3(self, bucket_file: str, data: Dict) -> bool:
        """

        """
        try:
            logging.info(
                f'Saving object into S3 bucket into folder {bucket_file}')
            self.s3_client.put_object(
                Body=json.dumps(data),
                Bucket=self.s3_bucket,
                Key=bucket_file
            )
            logging.info(f'Succesfully saved object into folder {bucket_file}')
            return True
        except Exception as ex:
            logging.error(
                f'An error occured when saving data into S3\nex: {ex}')
            return False
