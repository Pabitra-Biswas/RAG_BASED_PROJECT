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

        // --- CHANGE 2: Add optional testing stage ---
        stage('Run Tests (Optional)') {
            when {
                // Only run tests if test files exist
                expression { fileExists('tests/') }
            }
            steps {
                script {
                    echo 'Running tests...'
                    sh '''
                    . $VENV_DIR/bin/activate
                    # Add your test commands here, e.g.:
                    # python -m pytest tests/ -v
                    # For now, just validate the app can import
                    python -c "from app.main import app; print('App imports successfully')"
                    '''
                }
            }
        }

        stage('Building Docker Image and Pushing to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building Docker Image and Pushing to GCR'
                        // --- CHANGE 3: Add error handling and better logging ---
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
                        // --- CHANGE 4: Enhanced deployment with better configuration ---
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
                          --set-env-vars="GCS_BUCKET_NAME=${GCS_BUCKET},GOOGLE_API_KEY=${GOOGLE_API_KEY},CHROMA_PERSIST_DIRECTORY=/code/chroma_db_storage"
                        
                        echo "Getting service URL..."
                        SERVICE_URL=\$(gcloud run services describe gcp-mlops-project --region=us-central1 --format="value(status.url)")
                        echo "Service deployed successfully at: \$SERVICE_URL"
                        """
                    }
                }
            }
        }
    }

    // --- CHANGE 5: Add post-build actions ---
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