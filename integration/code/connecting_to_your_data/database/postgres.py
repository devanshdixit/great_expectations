from ruamel import yaml

import great_expectations as ge
from integration.code.connecting_to_your_data.database.util import (
    load_data_into_database,
)

CONNECTION_STRING = "postgresql+psycopg2://postgres:@localhost/test_ci"
load_data_into_database(
    "taxi_data",
    "./data/reports/yellow_tripdata_sample_2019-01.csv",
    CONNECTION_STRING,
)

context = ge.get_context()

datasource_yaml = """
name: my_postgres_datasource
class_name: Datasource
execution_engine:
  class_name: SqlAlchemyExecutionEngine
  connection_string: postgresql+psycopg2://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>
data_connectors:
   default_runtime_data_connector_name:
       class_name: RuntimeDataConnector
       batch_identifiers:
           - default_identifier_name
   default_inferred_data_connector_name:
       class_name: InferredAssetSqlDataConnector
       name: whole_table
"""
datasource_yaml = datasource_yaml.replace(
    "postgresql+psycopg2://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>",
    CONNECTION_STRING,
)

context.add_datasource(**yaml.load(datasource_yaml))

# First test for RuntimeBatchRequest using a query
batch_request = ge.core.batch.RuntimeBatchRequest(
    datasource_name="my_postgres_datasource",
    data_connector_name="default_runtime_data_connector_name",
    data_asset_name="default_name",  # this can be anything that identifies this data
    runtime_parameters={"query": "SELECT * from taxi_data LIMIT 10"},
    batch_identifiers={"default_identifier_name": "something_something"},
)

context.create_expectation_suite(
    expectation_suite_name="test_suite", overwrite_existing=True
)
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())

# Second test for BatchRequest naming a table
batch_request = ge.core.batch.BatchRequest(
    datasource_name="my_postgres_datasource",
    data_connector_name="default_inferred_data_connector_name",
    data_asset_name="taxi_data",  # this is the name of the table you want to retrieve
)
context.create_expectation_suite(
    expectation_suite_name="test_suite", overwrite_existing=True
)
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())