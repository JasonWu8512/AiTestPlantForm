pipeline {
    agent any

    environment {
        BACKEND_IMAGE = "aitest-backend"
        FRONTEND_IMAGE = "aitest-frontend"
        BACKEND_TAG = "latest"
        FRONTEND_TAG = "latest"
        DOCKER_REGISTRY = ""
        COMPOSE_FILE = "docker-compose.prod.yml"
    }

    tools {
        nodejs 'node20'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "=== 检出代码 ==="
                    checkout scm
                }
            }
        }

        stage('Backend Tests') {
            steps {
                script {
                    echo "=== 运行后端测试 ==="
                    dir('backend') {
                        sh 'pip install -r requirements.txt'
                        sh 'python manage.py test apps.users.tests apps.projects.tests apps.testcases.tests apps.executions.tests apps.reports.tests --verbosity=2'
                    }
                }
            }
        }

        stage('Frontend Install') {
            steps {
                script {
                    echo "=== 安装前端依赖 ==="
                    dir('frontend') {
                        sh 'npm install'
                    }
                }
            }
        }

        stage('Frontend Tests') {
            steps {
                script {
                    echo "=== 运行前端测试 ==="
                    dir('frontend') {
                        sh 'npm run test:run'
                    }
                }
            }
        }

        stage('Frontend Build') {
            steps {
                script {
                    echo "=== 构建前端 ==="
                    dir('frontend') {
                        sh 'npm run build'
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "=== 构建后端Docker镜像 ==="
                    sh "docker build -t ${BACKEND_IMAGE}:${BACKEND_TAG} -f backend/Dockerfile backend/"
                    
                    echo "=== 构建前端Docker镜像 ==="
                    sh "docker build -t ${FRONTEND_IMAGE}:${FRONTEND_TAG} -f frontend/Dockerfile frontend/"
                }
            }
        }

        stage('Push Docker Images') {
            when {
                branch 'main'
            }
            steps {
                script {
                    if (env.DOCKER_REGISTRY) {
                        echo "=== 推送镜像到Docker仓库 ==="
                        sh "docker tag ${BACKEND_IMAGE}:${BACKEND_TAG} ${DOCKER_REGISTRY}/${BACKEND_IMAGE}:${BACKEND_TAG}"
                        sh "docker tag ${FRONTEND_IMAGE}:${FRONTEND_TAG} ${DOCKER_REGISTRY}/${FRONTEND_IMAGE}:${FRONTEND_TAG}"
                        sh "docker push ${DOCKER_REGISTRY}/${BACKEND_IMAGE}:${BACKEND_TAG}"
                        sh "docker push ${DOCKER_REGISTRY}/${FRONTEND_IMAGE}:${FRONTEND_TAG}"
                    } else {
                        echo "未配置Docker仓库，跳过镜像推送"
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    echo "=== 部署到测试环境 ==="
                    sh "docker-compose -f ${COMPOSE_FILE} down"
                    sh "docker-compose -f ${COMPOSE_FILE} up -d"
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "=== 部署到生产环境 ==="
                    sh "docker-compose -f ${COMPOSE_FILE} down"
                    sh "docker-compose -f ${COMPOSE_FILE} up -d"
                }
            }
        }

        stage('Post Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "=== 部署后检查 ==="
                    sh 'sleep 30'
                    sh "docker-compose -f ${COMPOSE_FILE} ps"
                }
            }
        }
    }

    post {
        success {
            echo "=== 流水线执行成功 ==="
        }
        failure {
            echo "=== 流水线执行失败 ==="
        }
        cleanup {
            echo "=== 清理工作空间 ==="
            deleteDir()
        }
    }
}