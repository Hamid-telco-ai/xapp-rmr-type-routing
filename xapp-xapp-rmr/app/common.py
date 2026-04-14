import json
import logging
import os
import time

from ricxappframe.rmr import rmr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
LOG = logging.getLogger("xapp-rmr")

RMR_PORT = os.getenv("RMR_PORT", "4560")
PING_MTYPE = int(os.getenv("PING_MTYPE", "10000"))
PONG_MTYPE = int(os.getenv("PONG_MTYPE", "10001"))
APP_NAME = os.getenv("APP_NAME", "hello")


def init_rmr():
    ctx = rmr.rmr_init(
        RMR_PORT.encode(),
        rmr.RMR_MAX_RCV_BYTES,
        rmr.RMRFL_NONE,
    )
    LOG.info("%s: rmr_init completed on port %s", APP_NAME, RMR_PORT)

    for _ in range(120):
        if rmr.rmr_ready(ctx):
            LOG.info("%s: RMR is ready", APP_NAME)
            return ctx
        time.sleep(1)

    raise RuntimeError(f"{APP_NAME}: RMR route table never became ready")


def alloc_message(ctx, mtype: int, payload_dict: dict):
    payload = json.dumps(payload_dict).encode()
    msg = rmr.rmr_alloc_msg(ctx, len(payload), mtype=mtype)
    rmr.set_payload_and_length(payload, msg)
    return msg


def recv_payload(msg) -> str:
    payload = rmr.get_payload(msg)
    if not payload:
        return ""
    if isinstance(payload, bytes):
        return payload.decode(errors="ignore")
    return str(payload)