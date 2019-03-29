'''
Integration Test Suite for Backend Client API Library.

You should be running the API service on http://localhost:8081 to run this test
suite.  Of course, the service must be fully configured as follows:

 - The gateway server must have at least one agent.

   An example sequence to run both manager & agent locally:

   docker run -e POSTGRES_DB=sorna \
              -e POSTGRES_PASSWORD=develove \
              -p 5432:5432 -d \
              --name sorna-db \
              postgres
   python -m ai.backend.client.gateway.models \
          --create-tables --populate-fixtures
   docker run -p 6379:6379 -d \
              --name sorna-redis \
              redis
   python -m ai.backend.client.agent.server \
          --volume-root=`pwd`/volume-temp --max-kernels 3
   python -m ai.backend.client.gateway.server --service-port=8081

 - The agent should have access to a Docker daemon and the
   "lablup/python" docker image.

 - The gateway must have access to a test database that has pre-populated
   fixture data.
   (Check out `python -m ai.backend.client.gateway.models --populate-fixtures`)
'''

# TODO: add test cases for execution with custom env-vars
# TODO: add test cases for execution via websockets
# TODO: add test cases for batch mode build/clean commands
# TODO: add test cases for vfolder functions including invitations
# TODO: add test cases for service ports (future)
