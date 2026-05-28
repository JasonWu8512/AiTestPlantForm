#!/bin/bash

echo "=== 启动 Jenkins 服务 ==="
docker-compose -f docker-compose.jenkins.yml up -d

echo "等待 Jenkins 启动..."
sleep 60

echo "=== 获取 Jenkins 初始密码 ==="
docker exec aitest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword

echo "=== Jenkins 启动完成 ==="
echo ""
echo "访问地址: http://localhost:8080"
echo "初始密码已显示在上方"
echo ""
echo "请按照以下步骤配置:"
echo "1. 访问 http://localhost:8080"
echo "2. 输入初始密码"
echo "3. 选择「安装推荐插件」"
echo "4. 创建管理员账户"
echo "5. 创建流水线任务"
echo "6. 配置 Git 仓库地址"
echo "7. 指定 Jenkinsfile 路径"