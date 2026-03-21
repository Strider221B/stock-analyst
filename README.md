# stock-analyst

Commands for fresh restart of DB Container
1. docker compose down -v
1. delete the file under versions folder in albemic
1. If you change base image then:
    1. docker builder prune -f && docker compose up -d --build --force-recreate
1. docker compose up -d --build
1. If you get a port still in use error and lsof -i :8000 returns empty then restart docker - sudo systemctl restart docker
1. docker compose exec --user root backend alembic revision --autogenerate -m "Initial schema"
1. sudo chown -R $USER:$USER .  ### on local machine so that we can edit the version file in next step
1. Update the new version file with rls policy code.
1. docker compose exec backend alembic upgrade head

Check if database tables are setup correctly:
1. docker exec -it stock_db_dev psql -U [User_Name] -d [YOUR_DB_NAME]
1. \dt
1. SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname IN ('users', 'portfolios', 'portfolio_items');
1. SELECT * FROM pg_policies WHERE tablename IN ('users', 'portfolios', 'portfolio_items');
1. \d portfolios
1. \d portfolio_items
