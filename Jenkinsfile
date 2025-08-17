pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'my-bigquery-test-466512'
        GCLOUD_PATH = "/var/jenkins/google-cloud-sdk/bin"

        // --- CHANGE 1: Define Jenkins credentials for your secrets ---
        // These IDs must match the credentials you create in the Jenkins UI.
        GCS_BUCKET = credentials('gcs-bucket-name-cred')
        GOOGLE_API_KEY = credentials('google-api-key-cred')
    }

    stages {
        stage('Cloning Github repo to jenkins') {
            steps {
                script {
                    echo 'Cloning the repository...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Pabitra-Biswas/RAG_BASED_PROJECT.git']])
                }
            }
        }
        stage('Setting up our Virtual Environment and installing dependencies') {
            steps {
                script {
                    echo 'Setting up our Virtual Environment and installing dependencies'
                    // Switched to requirements.txt to match Dockerfile for consistency
                    sh '''
                    python -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Building Docker Image and Pushing to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building Docker Image and Pushing to GCR'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/gcp-mlops-project:latest .
                        docker push gcr.io/${GCP_PROJECT}/gcp-mlops-project:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Google Cloud Run') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Deploying to Google Cloud Run'
                        // --- CHANGE 2: Modify the deployment command ---
                        // Use a multi-line shell script for readability and add the --set-env-vars flag.
                        sh """
                        export PATH=\$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy gcp-mlops-project \\
                          --image=gcr.io/${GCP_PROJECT}/gcp-mlops-project:latest \\
                          --platform managed \\
                          --region=us-central1 \\
                          --allow-unauthenticated \\
                          --set-env-vars="GCS_BUCKET_NAME=${GCS_BUCKET},GOOGLE_API_KEY=${GOOGLE_API_KEY},CHROMA_PERSIST_DIRECTORY=/code/chroma_db_storage"
                        """
                    }
                }
            }
        }
    }
}