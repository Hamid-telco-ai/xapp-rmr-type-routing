import time
from ricxappframe.rmr import rmr
from common import LOG, PING_MTYPE, alloc_message, init_rmr, recv_payload

def main():
    ctx = init_rmr()
    seq = 1

    while True:
        out = {
            "type": "ping",
            "seq": seq,
            "ts": time.time(),
        }

        msg = alloc_message(ctx, PING_MTYPE, out)
        msg = rmr.rmr_send_msg(ctx, msg)

        txid = ""
        try:
            txid = rmr.get_xaction(msg).decode(errors="ignore")
        except Exception:
            pass

        print(
            f"PING sent: mtype={PING_MTYPE} seq={seq} txid={txid} "
            f"state={msg.contents.state} tp_state={msg.contents.tp_state}"
        )

        # IMPORTANT: rmr_torcv_msg needs (ctx, msg_buffer, timeout_ms)
        msg = rmr.rmr_torcv_msg(ctx, msg, 2000)

        if msg and msg.contents.state == rmr.RMR_OK:
            payload = recv_payload(msg)
            print(
                f"PONG received: mtype={msg.contents.mtype} payload={payload} "
                f"state={msg.contents.state} tp_state={msg.contents.tp_state}"
            )
        else:
            state = msg.contents.state if msg else "None"
            tp_state = msg.contents.tp_state if msg else "None"
            print(f"No reply or receive error: state={state} tp_state={tp_state}")

        seq += 1
        time.sleep(2)

if __name__ == "__main__":
    main()