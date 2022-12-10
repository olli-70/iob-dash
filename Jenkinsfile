pipeline {
    agent any
    stages {
        stages {
        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    app = docker.build("ehome/iob-dash")
                }
            }
        }
        stage('DeployTest') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'b5db816e-19d8-498b-94fa-fd1ee1d8b206', passwordVariable: 'SSHPASSWD', usernameVariable: 'SSHUSER')]) {
                    script {
                        try {
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@$prod_ip \"touch 0815.txt\""

                        } catch (err) {
                            echo: 'caught error: $err'
                        }
                        
                    }
                }
            }
        }
    }
}