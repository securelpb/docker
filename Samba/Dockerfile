FROM dperson/samba

# Create the alex group and user with UID/GID 1000
# -D: No password, -H: No home dir, -s: No shell access
RUN addgroup -g 1000 alex && \
    adduser -D -H -G alex -s /bin/false -u 1000 alex