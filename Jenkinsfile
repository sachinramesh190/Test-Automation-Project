node {
  //Stage 1: Checkout Code from Git
    stage('Application Code Checkout from Git') {
        checkout scm
    }
    //Stage 2: Deploy Application on MiniKube
    stage('Deploy Application on MiniKube') {
                sh("kubectl apply -f elastic-stack/elasticsearch-service.yaml")
                sh("kubectl apply -f elastic-stack/elasticsearch-statefulset.yaml")
                sh("kubectl apply -f elastic-stack/elasticsearch-externalservice.yaml")
                sh("kubectl apply -f elastic-stack/kibana-service.yaml")
                sh("kubectl apply -f elastic-stack/kibana-deployment.yaml")
        }
   }
