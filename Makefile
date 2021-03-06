all: build run
.PHONY: all

build:
	docker build -t trader .

run: 
	docker run -p 8080:80 trader

clean:
	docker system prune --all