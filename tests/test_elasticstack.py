import pytest
from kubetest.objects import Deployment
from kubetest.utils import * 
from kubernetes import client
import requests
import subprocess
from kubernetes_py import K8sDeployment, K8sPod, K8sConfig

current_kube_config = "C:\\Users\\sachin\\.kube\\config"

@pytest.mark.namespace(create=False)
def test_elasticstack_namespace(kube):
    print("Getting all the namespaces")
    dict = kube.get_namespaces()
    print("Current namespace in the Cluster: ")
    for k,v in dict.items():
        print("Namespace: " + str(k))

@pytest.mark.applymanifests('..\\elastic-stack', files=['elasticsearch-statefulset.yaml'])
def test_elasticsearch_statefulset(kube):
    """Creating ES deployment on our test namespace"""
    print("Validating ES Yaml and creating it in the test namespace")
    try:
        kube.wait_for_registered(timeout=180)
    except:
        print("Handling the timeout exception")
    deployments = kube.get_statefulsets()
    elasticsearch_state = deployments.get('elasticsearch')
    print("Number of Elastic search is: " + str(len(deployments )))
    assert elasticsearch_state is not None, "Elastic search deployment failed"
     
    pods = elasticsearch_state.get_pods()
    assert len(pods) == 1, 'ELK should deploy 1 elastic search pod'
     
    for pod in pods:
        containers = pod.get_containers()
        assert len(containers) == 1, 'Elastic search pod should have one container'
        status = pod.status()
        print("Status of ES pod is "+ str(status))
        print("Pod is in ready state? "+ str(pod.is_ready()))
     
    services = kube.get_services()
     
    elasticsearch_service = services.get('elasticsearch')
    elkaccess_service = services.get('elkaccess')
     
    elasticsearch_endpoints = elasticsearch_service.get_endpoints()
    print(len(elasticsearch_endpoints))
    assert len(elasticsearch_endpoints) == 1, "Elastic search endpoint is not created"
     
    elkaccess_endpoints = elkaccess_service.get_endpoints()
    print(len(elkaccess_endpoints))
    assert len(elkaccess_endpoints) == 1, "Elastic Access endpoint is not created"
    
        
@pytest.mark.applymanifests('..\\elastic-stack', files=['kibana-deployment.yaml'])
def test_kibana_deployment(kube):
    """Creating Kibana deployment on our test namespace"""

    print("Validating Kibana Yaml and creating it in test namspace")        
    
    deployments = kube.get_deployments()
    kibana_deployment = deployments.get('kibana-deployment')
    print("Number of Kibana deployment is: " + str(len(deployments )))
    
    assert kibana_deployment is not None,  "Kibana deployment failed"
    
    pods = kibana_deployment.get_pods()
    assert len(pods) == 1, 'ELK should deploy 1 Kibana pod'
    
    for pod in pods:
        containers = pod.get_containers()
        assert len(containers) == 1, 'Kibana pod should have one container'

@pytest.mark.applymanifests('..\\elastic-stack', files=['logstash-deployment.yaml','logstash-configmap.yaml'])
def test_logstash_deployment(kube):
    """Creating logstash deployment on our test namespace"""

    print("Validating Logstash Yaml and creating it in test namspace")        
    
    kube.wait_for_registered(timeout=120)
    deployments = kube.get_deployments()
    logstash_deployment_obj = deployments.get('logstash')
    print("Number of logstash deployment is: " + str(len(deployments )))
    
    assert logstash_deployment_obj is not None,  "logstash deployment failed"
    
    pods = logstash_deployment_obj.get_pods()
    assert len(pods) == 1, 'ELK should deploy 1 logstash pod'
    
    for pod in pods:
        pod.wait_until_containers_start(timeout=60)
        containers = pod.get_containers()
        assert len(containers) == 1, 'logstash pod should have one container'
        status = pod.status()
        print("Status of ES pod is "+ str(status))
        print("Pod is in ready state? "+ str(pod.is_ready()))


def filebeat_deployment(kube):
    """Creating filebeat deployment on our test namespace"""

    print("Validating filebeat Yaml and creating it in test namspace")        
    
    kube.wait_for_registered(timeout=120)
    daemonset = kube.get_daemonsets()
    filebeat_obj = daemonset.get('filebeat')
    print("Number of filebeat daemonset is: " + str(len(daemonset)))
    
    assert filebeat_obj is not None, "filebeat deployment failed"
    
    pods = filebeat_obj.get_pods()
    assert len(pods) == 1, 'ELK should deploy 1 filebeat pod'
    
    for pod in pods:
        pod.wait_until_containers_start(timeout=60)
        containers = pod.get_containers()
        assert len(containers) == 1, 'filebeat pod should have one container'
        status = pod.status()
        print("Status of ES pod is "+ str(status))
        print("Pod is in ready state? "+ str(pod.is_ready()))


def verify_apache_server():
    print("Validating apache-server-deployment")
    cfg_other = K8sConfig(kubeconfig=current_kube_config)
    pod = K8sPod(cfg_other, name='apache-server-deployment')
    fail_count = 0
    for pod in pod.list(labels={'app':'webserver'}):
        if not pod.is_ready():
            time.sleep(60)
        if not pod.is_ready:
            fail_count = fail_count + 1
        print("Apache server Pod is in ready state? "+ str(pod.is_ready()))

    if fail_count>2:
        return false
    return true    
    

def test_verify_apache_service():
    import sys
    try:
        bol = verify_apache_server()
        print(bol)
        assert bol, "Deployment is impacting other services"
    except:
        e = sys.exc_info()[1]
