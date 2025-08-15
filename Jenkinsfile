pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        // GCP_PROJECT = 'my-bigquery-test-466512' // Replace with your GCP project ID
        // GCLOUD_PATH = "/var/jenkins/google-cloud-sdk/bin"
    }

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

            stage('Setting up our Virtual Environment and installing dependencies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and installing dependencies'
                    sh '''
                    python -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
}