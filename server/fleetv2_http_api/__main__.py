#!/usr/bin/env python3
import connexion  # type: ignore
import logging

from fleetv2_http_api import encoder  # type: ignore


logger = logging.getLogger("werkzeug")


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Fleet v2 HTTP API'},
                pythonic_params=True)

    logger.info("Starting the Fleet Protocol v2 HTTP API server.")
    app.run(port=8080)


if __name__ == '__main__':
    main()
