build:
	docker build --rm --no-cache -f docker/Dockerfile -t chatbot:latest .
	docker compose -f docker/docker-compose.yml up -d
	# docker rmi $(docker images -f dangling=true -q)

destroy:
	docker compose -f docker/docker-compose.yml down
	docker rmi chatbot
	docker builder prune -f
