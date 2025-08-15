pipeline{
    agent any

    // environment {
    //     VENV_DIR = 'venv'
    //     GCP_PROJECT = 'my-bigquery-test-466512' // Replace with your GCP project ID
    //     GCLOUD_PATH = "/var/jenkins/google-cloud-sdk/bin"
    // }

    stages{
        stage('Cloning Github repo to jenkins'){
            steps{
                script{
                    echo 'Cloning the repository...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Pabitra-Biswas/RAG_BASED_PROJECT.git']])
                }
            }
        }
    }
}