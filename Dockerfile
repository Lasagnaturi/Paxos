FROM java:8

# Create work directory
WORKDIR /app

# Get the role and id of the process from env
ENV APP_ROLE ''
ENV ID ''

# copy the content of the local src directory to the working directory
COPY . .

# compile files
RUN javac Paxos.java 

RUN ls -la
# command to run on container start
CMD java Paxos ${APP_ROLE} ${ID}