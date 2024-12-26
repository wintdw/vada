import mysql.connector
from urllib.parse import urlparse
import time
import argparse
import hashlib
import json
import datetime
import requests

def convert_datetime_to_timestamp(data):
    for record in data:
        for key, value in record.items():
            if isinstance(value, datetime.datetime):
                record[key] = int(value.timestamp() * 1000)
    return data

def query_updated_tables_and_rows(mysql_uri, target, interval):

    query_time = int(time.time() * 1000)
    time_value = query_time - (interval * 60 * 1000)
    chunk_size = 100

    query_time_str = str(query_time).encode('utf-8')
    query_id = hashlib.sha256(query_time_str).hexdigest()

    try:
        url = urlparse(mysql_uri)

        connection = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            port=url.port,
            database="mysql"
        )
        cursor = connection.cursor(dictionary=True)

        null_items = [
            "demo_hni_app.places",
            "demo_hni_app.visitor_history",
            "demo_hni_bpms_ioc.places",
            "demo_hni_bpms_ioc.role_user",
            "demo_hni_bpms_ioc.status"
        ]

        modified_at_items = [
            "demo_hni_app.user",
            "demo_hni_app.status"
        ]

        updated_at_items = [
            "demo_hni_bpms_ioc.agencies",
            "demo_hni_bpms_ioc.common_category",
            "demo_hni_bpms_ioc.fields",
            "demo_hni_bpms_ioc.group_members",
            "demo_hni_bpms_ioc.groups",
            "demo_hni_bpms_ioc.process_request_tokens",
            "demo_hni_bpms_ioc.roles",
            "demo_hni_bpms_ioc.report_status",
            "demo_hni_bpms_ioc.users",
            "demo_hni_bpms_ioc_data.issue",
            "demo_hni_bpms_ioc.priority",
            "demo_hni_bpms_ioc.process_requests"
        ]

        for item in null_items:
            query = f"""
            SELECT *
            FROM {item}
            """
            cursor.execute(query)

            database, table = item.split(".")

            while True:
                results = cursor.fetchmany(chunk_size)

                if not results:
                    break

                results = convert_datetime_to_timestamp(results)
                json_string = json.dumps(results)
                data_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()

                data = {
                    "query_id": query_id,
                    "query_time": query_time,
                    "time_value": time_value,
                    "time_field": "null",
                    "database": database,
                    "table": table,
                    "table_fullname": item,
                    "data_hash": data_hash,
                    "data": results
                }
                headers = {'Content-Type': 'application/json'}
                response = requests.post(target, json=data, headers=headers)

        for item in modified_at_items:
            query = f"""
            SELECT *
            FROM {item}
            WHERE modified_at BETWEEN FROM_UNIXTIME({time_value}/1000) AND FROM_UNIXTIME({query_time}/1000)
            """
            cursor.execute(query)

            database, table = item.split(".")

            while True:
                results = cursor.fetchmany(chunk_size)

                if not results:
                    break

                results = convert_datetime_to_timestamp(results)
                json_string = json.dumps(results)
                data_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()

                data = {
                    "query_id": query_id,
                    "query_time": query_time,
                    "time_value": time_value,
                    "time_field": "modified_at",
                    "database": database,
                    "table": table,
                    "table_fullname": item,
                    "data_hash": data_hash,
                    "data": results
                }
                headers = {'Content-Type': 'application/json'}
                response = requests.post(target, json=data, headers=headers)

        for item in updated_at_items:
            query = f"""
            SELECT *
            FROM {item}
            WHERE updated_at BETWEEN FROM_UNIXTIME({time_value}/1000) AND FROM_UNIXTIME({query_time}/1000)
            """
            cursor.execute(query)

            database, table = item.split(".")

            while True:
                results = cursor.fetchmany(chunk_size)
                if not results:
                    break
                
                results = convert_datetime_to_timestamp(results)
                json_string = json.dumps(results)
                data_hash = hashlib.sha256(json_string.encode('utf-8')).hexdigest()

                data = {
                    "query_id": query_id,
                    "query_time": query_time,
                    "time_value": time_value,
                    "time_field": "updated_at",
                    "database": database,
                    "table": table,
                    "table_fullname": item,
                    "data_hash": data_hash,
                    "data": results
                }
                headers = {'Content-Type': 'application/json'}
                response = requests.post(target, json=data, headers=headers)

    except Exception as err:
        data = {
            "query_id": query_id,
            "query_time": query_time,
            "time_value": time_value,
            "database": "error",
            "table": "error",
            "table_fullname": "error.error",
            "data": err
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(target, json=data, headers=headers)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query MySQL database for recently updated tables and rows.")
    parser.add_argument("--mysql", default="mysql://root:root@127.0.0.1:3306", help="MySQL URI (default: mysql://root:root@127.0.0.1:3306)")
    parser.add_argument("--target", help="Target API")
    parser.add_argument("--interval", default=10, type=int, help="Interval in minutes (default: 10)")

    args = parser.parse_args()

    query_updated_tables_and_rows(
        mysql_uri=args.mysql,
        target=args.target,
        interval=args.interval
    )

