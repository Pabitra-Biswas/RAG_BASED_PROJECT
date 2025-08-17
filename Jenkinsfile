pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'my-bigquery-test-466512'
        GCLOUD_PATH = "/var/jenkins/google-cloud-sdk/bin"

        // --- FIXED: Changed GCS_BUCKET to GCS_BUCKET_NAME to match your config file ---
        // These IDs must match the credentials you create in the Jenkins UI.
        GCS_BUCKET_NAME = credentials('gcs-bucket-name-cred')
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

        // --- IMPROVED: Better test validation ---
        stage('Run Tests (Optional)') {
            steps {
                script {
                    echo 'Running tests...'
                    sh '''
                    . $VENV_DIR/bin/activate
                    # Validate that all required environment variables are available
                    echo "Validating environment variables..."
                    echo "GCS_BUCKET_NAME is set: ${GCS_BUCKET_NAME:+yes}"
                    echo "GOOGLE_API_KEY is set: ${GOOGLE_API_KEY:+yes}"
                    
                    # Test app import with proper environment
                    python -c "from app.main import app; print('App imports successfully')"
                    
                    # If you have actual tests, uncomment the line below:
                    # python -m pytest tests/ -v
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
                        
                        echo "Activating service account..."
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        
                        echo "Setting project..."
                        gcloud config set project ${GCP_PROJECT}
                        
                        echo "Configuring Docker..."
                        gcloud auth configure-docker --quiet
                        
                        echo "Building Docker image..."
                        docker build -t gcr.io/${GCP_PROJECT}/gcp-mlops-project:latest .
                        
                        echo "Pushing Docker image..."
                        docker push gcr.io/${GCP_PROJECT}/gcp-mlops-project:latest
                        
                        echo "Docker build and push completed successfully"
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
                        // --- FIXED: Changed GCS_BUCKET to GCS_BUCKET_NAME in the deployment ---
                        sh """
                        export PATH=\$PATH:${GCLOUD_PATH}
                        
                        echo "Activating service account for deployment..."
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        echo "Deploying to Cloud Run..."
                        gcloud run deploy gcp-mlops-project \\
                          --image=gcr.io/${GCP_PROJECT}/gcp-mlops-project:latest \\
                          --platform managed \\
                          --region=us-central1 \\
                          --allow-unauthenticated \\
                          --port=8080 \\
                          --memory=2Gi \\
                          --cpu=2 \\
                          --timeout=900 \\
                          --max-instances=10 \\
                          --concurrency=80 \\
                          --set-env-vars="GCS_BUCKET_NAME=${GCS_BUCKET_NAME},GOOGLE_API_KEY=${GOOGLE_API_KEY},CHROMA_PERSIST_DIRECTORY=/code/chroma_db_storage"
                        
                        echo "Getting service URL..."
                        SERVICE_URL=\$(gcloud run services describe gcp-mlops-project --region=us-central1 --format="value(status.url)")
                        echo "Service deployed successfully at: \$SERVICE_URL"
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                // Clean up virtual environment to save space
                sh 'rm -rf $VENV_DIR || true'
                
                // Clean up Docker images to save space (optional)
                sh 'docker system prune -f || true'
            }
        }
        
        success {
            echo 'Pipeline completed successfully!'
            // You could add notifications here
        }
        
        failure {
            echo 'Pipeline failed! Check the logs above for details.'
            // You could add failure notifications here
        }
    }
}