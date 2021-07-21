# Smoke test to simplify cluster health validation with CCMs
Smoke test written in Python with the use of Pytest framework and [openshift-restclient-python](https://github.com/openshift/openshift-restclient-python).

Test creates resources on the openshift cluster:
- Project/namespace
- Deployment
- Service
- Route 
- PersistentVolumeClaim
- Job

These resources deploy a nginx webserver on the cluster in its own namespace, and populate it with index.html file from persistent storage. 
Pytest is used to create these resources and verify the exposed webserver has matching content.

---
The test requires kubeconfig for the cluster to be stored as `.kube/config`.

Test can be deployed inside a podman container:
```
make image
make run
```
or run locally inside virtual environment:
```
make venv
make test 
```
