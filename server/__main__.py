import sys
sys.path.append("server")


from server.fleetv2_http_api.__main__ import main as orig_main


def main()->None:
    orig_main()


if __name__ == '__main__':
    print("\n\nStarting the server\n\n")
    main()
