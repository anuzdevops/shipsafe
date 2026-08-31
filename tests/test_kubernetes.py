from pathlib import Path

from shipsafe.parsers.kubernetes import (
    extract_deployment,
    extract_service,
    parse_kubernetes_file,
)


def test_parse_kubernetes_deployment(tmp_path: Path):
    manifest = tmp_path / "deployment.yaml"

    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: backend:1.0
          ports:
            - containerPort: 3000
""",
        encoding="utf-8",
    )

    resources = parse_kubernetes_file(manifest)

    deployment = extract_deployment(resources[0])

    assert deployment is not None
    assert deployment.name == "backend"
    assert deployment.labels == {"app": "backend"}
    assert deployment.containers[0].name == "backend"
    assert len(deployment.containers[0].ports) == 1
    assert deployment.containers[0].ports[0].name is None
    assert deployment.containers[0].ports[0].port == 3000


def test_parse_kubernetes_service(tmp_path: Path):
    manifest = tmp_path / "service.yaml"

    manifest.write_text(
        """
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
    - port: 80
      targetPort: 3000
""",
        encoding="utf-8",
    )

    resources = parse_kubernetes_file(manifest)

    service = extract_service(resources[0])

    assert service is not None
    assert service.name == "backend-service"
    assert service.selector == {"app": "backend"}
    assert service.target_ports == [3000]
