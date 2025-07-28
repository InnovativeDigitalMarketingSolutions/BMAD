# ETL Pipeline Template (Prefect)

from prefect import flow, task


@task
def extract():
    # Data extractie
    pass

@task
def transform(data):
    # Data cleaning/feature engineering
    pass

@task
def load(data):
    # Data laden in database
    pass

@flow
def etl_flow():
    data = extract()
    clean = transform(data)
    load(clean)
