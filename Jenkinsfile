pipeline {
    // Keep the default agent for simple stages like checkout
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Cloning Github repo to jenkins') {
            steps {
                script {
                    echo 'Cloning the repository...'
                    // Your original checkout command is correct
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Pabitra-Biswas/RAG_BASED_PROJECT.git']])
                }
            }
        }
        
        // --- THIS STAGE HAS BEEN MODIFIED ---
        stage('Setting up our Virtual Environment and installing dependencies') {
            // *** CHANGE 1: Define a Docker agent for this stage ***
            // This tells Jenkins to run these steps inside a temporary container
            // that has Python 3.10 pre-installed.
            agent {
                docker { image 'python:3.10-slim' }
            }
            steps {
                script {
                    echo 'Setting up our Virtual Environment and installing dependencies'
                    
                    // *** CHANGE 2 & 3: Combine commands and fix pip install ***
                    sh '''
                    # All these commands run in the same shell now
                    
                    # 1. Create the virtual environment
                    python -m venv $VENV_DIR
                    
                    # 2. Activate the virtual environment
                    source $VENV_DIR/bin/activate
                    
                    # 3. Upgrade pip and install dependencies from requirements.txt
                    pip install --upgrade pip
                    pip install --no-cache-dir -r requirements.txt
                    '''
                }
            }
        }

        // You will add more stages here later, like 'Build Docker Image' and 'Deploy'
    }
}