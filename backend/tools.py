from backend.logging_config import logger


def db_delete(record_count: int):
    """
    Simulates deleting database records.
    """

    logger.info(f"Deleting {record_count} records.")

    return {
        "status": "success",
        "message": f"{record_count} records deleted."
    }


def send_email(recipient_domain: str):
    """
    Simulates sending an email.
    """

    logger.info(f"Email sent to {recipient_domain}")

    return {
        "status": "success",
        "message": f"Email sent to {recipient_domain}"
    }


def read_file(path: str):
    """
    Simulates reading a confidential file.
    """

    logger.info(f"Reading file {path}")

    return {
        "status": "success",
        "message": f"Read file {path}"
    }


def execute_tool(tool_call: dict):
    """
    Executes the tool AFTER the policy engine allows it.
    """

    tool = tool_call["tool"]
    params = tool_call["params"]

    if tool == "db_delete":
        return db_delete(params["record_count"])

    elif tool == "send_email":
        return send_email(params["recipient_domain"])

    elif tool == "read_file":
        return read_file(params["path"])

    else:
        return {
            "status": "error",
            "message": "Unknown tool"
        }