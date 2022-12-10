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
                             def s = checkout scm;
                             if      (s.GIT_URL != null) GIT_REPO_URL= s.GIT_URL
                             else if (s.SVN_URL != null) GIT_REPO_URL= s.SVN_URL
                             else GIT_REPO_URL=s
                           }
                    script {
                        try {
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@c-host1 \"rm -rf iob-dash; echo tried to remove existing folder\""
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@c-host1 \"git clone ${GIT_REPO_URL}\""
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@c-host1 \"cd iob-dash; docker build -f Dockerfile -t iob-dash .\""
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@c-host1 \"docker rm -f iob-dash\""
                            sh "sshpass -p '$SSHPASSWD' -v ssh -o StrictHostKeyChecking=no $SSHUSER@c-host1 \"sudo /var/lib/docker/startscripts/iob-dash.sh\""
                        } catch (err) {
                            echo: 'caught error: $err'
                        }
                        
                    }
                }
            }
        }
    }
}