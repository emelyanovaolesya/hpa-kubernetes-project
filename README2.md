## Состав
`postgres.yaml` - Деплоймент PostgreSQL в Kubernetes  
`deployment-users.yaml` - Деплоймент и сервис для микросервиса service-users  
`deployment-orders.yaml` - Деплоймент и сервис для микросервиса service-orders  
`deployment-gateway.yaml` - Деплоймент и сервис для API Gateway  
`alertmanager-telegram.example.yaml` - Шаблон конфигурации Alertmanager для Telegram (нужно вставить свои токены)  
`error-budget-rule.yaml` - Правило Prometheus для алерта на частые перезапуски подов  

## Старт
Добавление репозитория:  
`helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`  
`helm repo update`

Установка kube-prometheus-stack:  
`helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace`

Деплой приложения:  
`kubectl apply -f postgres.yaml`  
`kubectl apply -f deployment-users.yaml`  
`kubectl apply -f deployment-orders.yaml`  
`kubectl apply -f deployment-gateway.yaml`  

Настройка Alertmanager:  
1. Подставить свои токен и chat_id  
2. `kubectl apply -f alertmanager-telegram.yaml`  
`kubectl rollout restart statefulset alertmanager-monitoring-kube-prometheus-alertmanager -n monitoring`

Установка правил алертов:  
`kubectl apply -f error-budget-rule.yaml`

## Тестирование алерта
Необходимо несколько перезапусков:  
`kubectl exec -it <pod-name> -- /bin/sh -c "kill 1"`
