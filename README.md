# xApp-to-xApp Communication in O-RAN through RMR

<img width="511" height="605" alt="xAPP-xAPP-RMR drawio - No RTS drawio" src="https://github.com/user-attachments/assets/45fba9cf-be1c-4f94-8388-cba2ffff6b28" />

This repository demonstrates a xApp-to-xApp communication pattern using the O-RAN SC RMR (RIC Message Router).

- `hello` sends `PING` messages (`mtype=10000`)
- `hello-b` receives them and replies with `PONG` (`mtype=10001`)

The demo runs inside a Kubernetes-based Near-RT RIC environment using two xApps deployed in the `ricxapp` namespace.

## Routing Model Used

This demo uses **message-type-based routing** rather than RTS (Return-To-Sender).

While RMR supports RTS for automatic reply-to-origin semantics, in Kubernetes environments
RTS requires a stable and routable sender identity (e.g., via `RMR_SRC_ID`).

For simplicity, this demo uses:

- `mtype=10000` → routed to `hello-b`
- `mtype=10001` → routed to `hello`

This ensures deterministic bidirectional communication using static routing.

This demo follows the O-RAN SC RMR model where routing is based on **message type** rather than direct IP addressing. A static route table is loaded using `RMR_SEED_RT`, while `RMR_RTG_SVC=-1` disables the Route Manager for standalone local testing.

## Key Difference: Message-Type Routing vs RTS

| Feature            | Message-Type Routing              | Return-To-Sender (RTS)         |
|--------------------|----------------------------------|--------------------------------|
| Routing logic      | Based on `mtype`                 | Based on sender context        |
| Communication      | One-to-many                      | One-to-one                     |
| Response path      | Not guaranteed                   | Automatic return to sender     |
| Behavior in demo   | Message is consumed by receiver  | Request → Response loop        |

## Repository Structure

- `app/hello.py`: sender xApp
- `app/hello_b.py`: responder xApp
- `app/common.py`: shared RMR helpers
- `k8s/*.yaml`: Kubernetes manifests for `ricxapp`
- `Dockerfile`: container image

## Prerequisites

You already have the key platform steps documented in your command notes: local kind cluster, RIC deployment repo, and RIC namespaces such as `ricplt`, `ricinfra`, and `ricxapp`.

Before running this demo, confirm:
1. Docker works.
2. `kubectl` points to your `kind-ric` cluster.
3. The `ricxapp` namespace exists.
4. Kubernetes can see locally loaded images.

## Run guide

### 1) Unzip

```bash
unzip xapp-xapp-rmr-demo.zip
cd xapp-xapp-rmr-demo
```

### 2) Build the image

```bash
docker build -t hello-xapp-rmr:latest .
```

If the `rmr_<version>_amd64.deb` download in the Dockerfile fails, update `RMR_VER` to a package version that exists in packagecloud for your lab release. The reason this Dockerfile installs a Debian package is that the Python wrapper depends on the **RMR shared library** being present in the image.

### 3) Load the image into kind

```bash
kind load docker-image hello-xapp-rmr:latest --name ric
```

### 4) Confirm your RIC namespace exists

```bash
kubectl get ns | grep ricxapp
```

### 5) Apply the route table and services

```bash
kubectl apply -f k8s/hello-routes-configmap.yaml
kubectl apply -f k8s/hello-service.yaml
kubectl apply -f k8s/hello-b-service.yaml
```

### 6) Deploy the two xApps

```bash
kubectl apply -f k8s/hello-deployment.yaml
kubectl apply -f k8s/hello-b-deployment.yaml
```

### 7) Watch the pods

```bash
kubectl get pods -n ricxapp -w
```

Wait until both are `Running`.

### 8) Check logs

In terminal 1:

```bash
kubectl logs -n ricxapp deploy/hello -f
```

In terminal 2:

```bash
kubectl logs -n ricxapp deploy/hello-b -f
```

## Sample Output

### Sender xApp (`hello`)

```
PING sent: mtype=10000 seq=1 state=0 tp_state=0
PONG received: mtype=10001 payload={"type": "pong", "got": "..."} state=0 tp_state=0

PING sent: mtype=10000 seq=2 state=0 tp_state=0
PONG received: mtype=10001 payload={"type": "pong", "got": "..."} state=0 tp_state=0
```

### Responder xApp (`hello-b`)

```
PING received: mtype=10000 payload={"type": "ping", "seq": 1} state=0 tp_state=0
PONG sent: mtype=10001 state=0 tp_state=0

PING received: mtype=10000 payload={"type": "ping", "seq": 2} state=0 tp_state=0
PONG sent: mtype=10001 state=0 tp_state=0
```

## Notes

- This demo uses a **static RMR route table** via `RMR_SEED_RT`
- `RMR_RTG_SVC=-1` disables Route Manager for standalone testing
- Communication is based entirely on **message types**, not IP addresses
- The Python implementation uses the official `ricxappframe.rmr` bindings

## References

RMR (RIC Message Router) User Guide — O-RAN Software Community:  
https://docs.o-ran-sc.org/projects/o-ran-sc-ric-plt-lib-rmr/en/latest/user-guide.html
