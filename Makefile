build:
	docker build --rm --no-cache -f docker/Dockerfile -t chatbot:latest .
	docker compose -f docker/docker-compose.yml up -d
	docker builder prune -f

destroy:
	docker compose -f docker/docker-compose.yml down
	docker rmi chatbot
	docker builder prune -f
