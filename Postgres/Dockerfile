# Current image as of Aug 2026
FROM pgvector/pgvector:pg18-bookworm

# Define build-time arguments for user and group IDs with sensible defaults.
ARG UID=1000
ARG GID=1000

# The base image entrypoint runs as root initially, so we just need to
# modify the UID/GID of the 'postgres' user it will eventually use.
# The '-o' flag allows using a non-unique UID/GID.
RUN groupmod -o -g ${GID} postgres && \
    usermod -o -u ${UID} postgres
