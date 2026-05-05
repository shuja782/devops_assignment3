pipeline {
    agent any

    environment {
        APP_DIR = "${WORKSPACE}"
        TEST_IMAGE = "todo-test-image"
        RESULTS_DIR = "${WORKSPACE}/test-results"
    }

    stages {

        stage('Clone Repository') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Start Application') {
            steps {
                echo 'Starting app with Docker Compose...'
                sh '''
                    cd ${APP_DIR}
                    docker compose down || true
                    docker compose up -d --build
                    echo "Waiting for app to be ready..."
                    sleep 15
                    curl -f http://localhost:5000/health || exit 1
                    echo "App is up!"
                '''
            }
        }

        stage('Build Test Image') {
            steps {
                echo 'Building test Docker image...'
                sh '''
                    cd ${APP_DIR}
                    docker build -f Dockerfile.test -t ${TEST_IMAGE} .
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running Selenium tests...'
                sh '''
                    mkdir -p ${RESULTS_DIR}
                    docker run --rm \
                        --network host \
                        -v ${RESULTS_DIR}:/tests/results \
                        ${TEST_IMAGE}
                '''
            }
            post {
                always {
                    junit '**/test-results/test-results.xml'
                }
            }
        }
    }

    post {
        always {
            echo 'Sending email with test results...'
            script {
                def jobName = env.JOB_NAME
                def buildNum = env.BUILD_NUMBER
                def buildStatus = currentBuild.currentResult
                def pusherEmail = sh(
                    script: "git log -1 --format='%ae'",
                    returnStdout: true
                ).trim()

                emailext(
                    to: "${pusherEmail}",
                    subject: "[Jenkins] ${jobName} #${buildNum} - ${buildStatus}",
                    body: """
                        <h2>Build ${buildStatus}</h2>
                        <p><b>Job:</b> ${jobName}</p>
                        <p><b>Build Number:</b> ${buildNum}</p>
                        <p><b>Status:</b> ${buildStatus}</p>
                        <p><b>Check full results:</b> 
                           <a href="${env.BUILD_URL}">${env.BUILD_URL}</a>
                        </p>
                    """,
                    mimeType: 'text/html',
                    attachmentsPattern: 'test-results/test-results.xml'
                )
            }
            sh 'docker compose down || true'
        }
    }
}
