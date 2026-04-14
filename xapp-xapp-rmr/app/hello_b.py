import json
import time
from ricxappframe.rmr import rmr
from common import PING_MTYPE, PONG_MTYPE, init_rmr, recv_payload

def main():
    ctx = init_rmr()

    rx_msg = rmr.rmr_alloc_msg(ctx, rmr.RMR_MAX_RCV_BYTES)

    while True:
        rx_msg = rmr.rmr_torcv_msg(ctx, rx_msg, 5000)

        if not rx_msg:
            print("Receive returned no buffer")
            rx_msg = rmr.rmr_alloc_msg(ctx, rmr.RMR_MAX_RCV_BYTES)
            continue

        if rx_msg.contents.state != rmr.RMR_OK:
            print(
                f"Receive timeout/error: state={rx_msg.contents.state} "
                f"tp_state={rx_msg.contents.tp_state}"
            )
            continue

        payload = recv_payload(rx_msg)
        print(
            f"PING received: mtype={rx_msg.contents.mtype} payload={payload} "
            f"state={rx_msg.contents.state} tp_state={rx_msg.contents.tp_state}"
        )

        if rx_msg.contents.mtype == PING_MTYPE:
            reply_dict = {
                "type": "pong",
                "got": payload,
                "ts": time.time(),
            }
            reply_payload = json.dumps(reply_dict).encode()

            tx_msg = rmr.rmr_alloc_msg(ctx, len(reply_payload))
            tx_msg.contents.mtype = PONG_MTYPE
            rmr.set_payload_and_length(reply_payload, tx_msg)

            tx_msg = rmr.rmr_send_msg(ctx, tx_msg)

            print(
                f"PONG sent: mtype={PONG_MTYPE} "
                f"state={tx_msg.contents.state} tp_state={tx_msg.contents.tp_state}"
            )

if __name__ == "__main__":
    main()