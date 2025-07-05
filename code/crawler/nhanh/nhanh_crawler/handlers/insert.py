def add_insert_metadata(batch_report: list, index_name: str) -> dict:
    return {"meta": {"index_name": index_name}, "data": batch_report}
