up:
	docker-compose -f docker-compose-local.yaml up -d && docker-compose -f docker-compose-local.yaml logs -f

down:
	docker-compose -f docker-compose-local.yaml down && docker network prune --force
