from typing import Any

from loguru import logger
from requests.api import post

from .dataclasses import BasicMetric


def send_summary_to_backend(host_id: str, endpoint: str, data: Any) -> None:
    try:
        url = endpoint + host_id
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        response = post(url=url, headers=headers, data=data.to_json())
        logger.info(f"SENT SUMMARY TO {url}. STATUS CODE: {response.status_code}")
    except Exception as e:
        logger.error(f"FAILED TO SEND SUMMARY TO {url}")


def get_metric_from_data(metric_name: str, data: Any) -> BasicMetric:
    if metric_name in ["virtual_memory", "disk_memory"]:
        return BasicMetric(data.used, data.total, data.percent)
    elif metric_name == "host_cpu_usage":
        percentage = data
        return BasicMetric(percentage, 100, percentage)
    elif metric_name == "container_cpu_usage":
        # NOTE (@bplewnia) - Divide by number of nanoseconds in second -> 10e9
        percentage = (
            abs(
                data["cpu_stats"]["cpu_usage"]["total_usage"]
                - data["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            * 100
            / 10 ** 9
        )
        return BasicMetric(percentage, 100, percentage)
    elif metric_name == "container_memory_usage":
        return (
            BasicMetric(0, 0, 0)
            if not data
            else BasicMetric(
                data["usage"], data["limit"], (data["usage"] / data["limit"]) * 100
            )
        )
    else:
        logger.error(f"DID NOT FIND OPTION FOR {metric_name}")
        return BasicMetric(0, 0, 0)
