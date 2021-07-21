import pytest
import yaml
import time
import requests

from kubernetes import client, config
from openshift.dynamic import DynamicClient

NAMESPACE = "ccm-smoke-test"
PATH = "manifests/"


@pytest.fixture
def client():
    """ Fixture to set up openshift client. """
    k8s_client = config.new_client_from_config()
    return DynamicClient(k8s_client)


def read_yaml(filename):
    with open(PATH + filename, 'r') as stream:
        try:
            content = yaml.safe_load(stream)
            print(content)
            return content

        except yaml.YAMLError as exc:
            print(exc)


def wait_for_pod(client, selector):
    """Wait for pod to either run or complete."""
    print("Waiting for pod to be running...")
    timeout = time.time() + 60*5   # 5 minutes from now
    while True:
        status = client.resources.get(api_version='v1', kind='Pod').get(
            namespace=NAMESPACE, label_selector=selector).to_dict().get('items')[0].get('status').get("phase")
        if status == "Pending":
            time.sleep(5)  # sleep 5 seconds
            print("phase: Pending")
            continue
        elif status == "Running" or status == "Succeeded":
            print("hase: Running...")
            return True
        elif time.time() > timeout:
            return False
        else:
            return False


def delete_project(client):
    client.resources.get(api_version='project.openshift.io/v1',
                         kind='Project').delete(name=NAMESPACE)


@pytest.fixture
def prepare_test(client):
    # create namespace
    client.resources.get(api_version='project.openshift.io/v1',
                         kind='Project').create(body=read_yaml('project.yaml'), namespace=NAMESPACE)
    print("Created project.")
    # create pvc and job
    client.resources.get(api_version='v1', kind='PersistentVolumeClaim').create(
        body=read_yaml('pvc.yaml'), namespace=NAMESPACE)
    print("Created PVC.")
    client.resources.get(api_version='batch/v1', kind='Job').create(
        body=read_yaml('job.yaml'), namespace=NAMESPACE)
    print("Created Job.")

    # wait for job
    status = wait_for_pod(client, 'job-name=smoke-test-set-page')
    print(f"status was {status}")

    # delete job
    client.resources.get(api_version='batch/v1', kind='Job').delete(
        namespace=NAMESPACE, label_selector='ccm-smoke-test=nginx')
    print("Deleted job.")

    if not status:
        print("Job failed to complete.")
        delete_project(client)
        exit(-1)
    # create deployment, service and route
    client.resources.get(api_version='v1', kind='Deployment').create(
        body=read_yaml('deployment.yaml'), namespace=NAMESPACE,)
    print("Created deploy.")
    client.resources.get(api_version='v1', kind='Service').create(
        body=read_yaml('service.yaml'), namespace=NAMESPACE)
    print("Created service.")
    client.resources.get(api_version='route.openshift.io/v1',
                         kind='Route').create(body=read_yaml('route.yaml'), namespace=NAMESPACE)
    print("Created route.")

    if not wait_for_pod(client, 'app=nginx'):
        print("Deployment failed to run.")
        delete_project(client)
        exit(-1)

    # run test
    yield

    client.resources.get(
        api_version='project.openshift.io/v1', kind='Project').delete(name=NAMESPACE)


def test_ccm_smoke_test(client, prepare_test):
    print("Starting test .. ")
    url = client.resources.get(api_version='route.openshift.io/v1', kind='Route').get(
        namespace=NAMESPACE).to_dict().get('items')[0].get('spec').get("host")
    res = requests.get("http://" + url)
    expected = "<h1>Hello CCM developer!</h1>"
    assert res.text.strip() == expected
