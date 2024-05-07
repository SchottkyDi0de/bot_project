from os import system

import typer

app = typer.Typer()

@app.command()
def run_server(mode: str):
    if mode == 'prod':
        typer.echo('Starting server in production mode...')
        system(
            'uvicorn web.server.server:run \
            --workers 1 \
            --host blitzhub.eu \
            --port 443 \
            --factory \
            --ssl-keyfile /etc/letsencrypt/live/blitzhub.eu/privkey.pem \
            --ssl-certfile /etc/letsencrypt/live/blitzhub.eu/fullchain.pem'
        )
    elif mode == 'dev':
        typer.echo('Starting server in development mode...')
        system(
            'uvicorn web.server.server:run \
            --workers 1 \
            --host 127.0.0.1 \
            --port 8000 \
            --factory'
        )
    else:
        raise ValueError('Invalid mode. Must be either "prod" or "dev"')
    
if __name__ == '__main__':
    app()