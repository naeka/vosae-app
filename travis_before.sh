eu() {
  export AWS_ACCESS_KEY_ID=$EU_AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=$EU_AWS_SECRET_ACCESS_KEY
  export AWS_STORAGE_BUCKET_NAME="eu-vosae-uploads-test-public"
}

if [[ $TRAVIS_PULL_REQUEST != 'false' ]]; then
  echo "This is a pull request. No before script will be done."
elif [[ $TRAVIS_BRANCH == 'master' || $TRAVIS_BRANCH == 'develop' ]]; then
  echo "Going to run the dev script..."
  eu
else
  echo "Nothing to do..."
fi