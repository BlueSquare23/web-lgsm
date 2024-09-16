FROM ubuntu:latest

# Install apt deps.
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install -y sudo

# Create a non-root user 'web-lgsm'.
RUN useradd -m web-lgsm

# Temp allow 'web-lgsm' to use sudo without a password.
RUN echo "web-lgsm ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Set the working directory.
WORKDIR /home/web-lgsm

# Copy the app source code.
COPY . /home/web-lgsm

# Set ownership of the app directory to the web-lgsm user.
RUN chown -R web-lgsm:web-lgsm /home/web-lgsm

# Set the default user to 'web-lgsm'.
USER web-lgsm
ENV USER=web-lgsm

# Install web-lgsm.
RUN /home/web-lgsm/install.sh -d

# Delete temp sudoers rule.
USER root
RUN sed -i '$ d' /etc/sudoers

# Expose app's port.
EXPOSE 12357

# Entrypoint script to start the app.
USER web-lgsm
ENTRYPOINT ["/home/web-lgsm/web-lgsm.py", "-d"]
