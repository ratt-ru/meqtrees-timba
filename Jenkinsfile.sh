set -e
echo "----------------------------------------------"
echo "$JOB_NAME build $BUILD_NUMBER"
WORKSPACE_ROOT="$WORKSPACE/$BUILD_NUMBER"
echo "Setting up build in $WORKSPACE_ROOT"
TEST_OUTPUT_DIR_REL=testcase_output
TEST_OUTPUT_DIR="$WORKSPACE_ROOT/$TEST_OUTPUT_DIR_REL"
TEST_DATA_DIR="$WORKSPACE/../../../test-data"
PROJECTS_DIR_REL="projects"
PROJECTS_DIR=$WORKSPACE_ROOT/$PROJECTS_DIR_REL
mkdir $TEST_OUTPUT_DIR
echo "----------------------------------------------"
echo "\nEnvironment:"
df -h .
echo "----------------------------------------------"
cat /proc/meminfo
echo "----------------------------------------------"

#build using docker file in directory:
cd $PROJECTS_DIR/meqtrees-timba
IMAGENAME="mttimbapr"

# build and test
docker build -f .ci/ubuntu20.04.docker -t "${IMAGENAME}38:$BUILD_NUMBER" --no-cache=true .
docker build -f .ci/ubuntu22.04.docker -t "${IMAGENAME}310:$BUILD_NUMBER" --no-cache=true .
