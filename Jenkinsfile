node {

  def local_elasticurl
  def local_kibanaurl
  //Stage 1: Infrastructure testing	
  stage('Invoke python Job') {
    build job: 'python test build',
    parameters: []
  }
  //Stage 2: Deploy Application on MiniKube
  stage('Deploy Application on MiniKube') {
    sh("kubectl apply -f elastic-stack/elasticsearch-statefulset.yaml")
    sh("kubectl apply -f elastic-stack/kibana-deployment.yaml")
    sh("kubectl apply -f elastic-stack/logstash-configmap.yaml")
    sh("kubectl apply -f elastic-stack/logstash-deployment.yaml")
    sh("kubectl apply -f elastic-stack/filebeat-configmap.yaml")
    sh("kubectl apply -f elastic-stack/filebeat-daemonset.yaml")
  }
  //Stage 3: Get the Service EndPoints
  stage('Get the Service EndPoints') {
    local_elasticurl = sh(returnStdout: true, script: 'minikube service elkaccess --url').trim()
    local_kibanaurl = sh(returnStdout: true, script: 'minikube service kibana --url').trim()
    local_kibanahost = local_kibanaurl.substring(local_kibanaurl.lastIndexOf(":") + 1).trim()
    local_elastichost = local_elasticurl.substring(local_elasticurl.lastIndexOf(":") + 1).trim()

    echo local_kibanaurl
    echo local_kibanahost
    echo local_elastichost
    echo local_elasticurl

  }

  //Stage 3: Invoke Selenium Job
  stage('Invoke Functional Job') {
    build job: 'Testing-Pipeline',
    parameters: [[$class: 'StringParameterValue', name: 'kibanaURL', value: local_kibanaurl], [$class: 'StringParameterValue', name: 'elasticSearchURL', value: local_elasticurl]]
  }
  //Stage 4: Invoke Performance Job
  stage('Invoke Functional Job') {
    build job: 'Performance Report Testing',
    parameters: [[$class: 'StringParameterValue', name: 'kibana_port', value: local_kibanahost], [$class: 'StringParameterValue', name: 'elasticsearch_port', value: local_elastichost]]
  }

}