The same `server.py` as the Kubernetes experiment, packaged for DigitalOcean App Platform.
It reports its hostname and a `GEN` environment variable in every response, so a load
generator can see exactly when a redeploy cuts traffic over to the new version.
`SHUTDOWN_MODE` selects the shutdown behaviour, as in the parent directory.
