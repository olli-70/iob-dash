pipeline {
    agent any
    stages {

        stage('DeployTest') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'b5db816e-19d8-498b-94fa-fd1ee1d8b206', passwordVariable: 'SSHPASSWD', usernameVariable: 'SSHUSER')]) {
                    script {
                        try {
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@c-host1 \"git clone ${env.CHANGE_URL}\""

                        } catch (err) {
                            echo: 'caught error: $err'
                        }
                        
                    }
                }
            }
        }
    }
}