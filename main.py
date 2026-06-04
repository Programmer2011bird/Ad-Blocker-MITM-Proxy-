from proxy import ThreadingServer, MITMProxyServer
import config
import sys
import os

def set_env_proxy():
    os.environ["http_proxy"] = config.UPSTREAM_PROXY_HTTP
    os.environ["https_proxy"] = config.UPSTREAM_PROXY_HTTPS

def main():
    # set_env_proxy()

    try:
        server: ThreadingServer = ThreadingServer((config.HOST, config.PORT), MITMProxyServer)
        server.serve_forever()

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

