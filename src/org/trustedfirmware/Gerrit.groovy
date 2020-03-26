/*
 * Copyright (c) 2020, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */

package org.trustedfirmware

def verifyStatus(value, verify_name, category) {
  node("docker-amd64-xenial") {
    cleanWs()
    dir("tf-m-ci-scripts") {
      git url: '$CI_SCRIPTS_REPO', branch: 'master', credentialsId: 'GIT_SSH_KEY'
    }
    verifyStatusInWorkspace(value, verify_name, category)
  }
}

def verifyStatusInWorkspace(value, verify_name, category) {
  withCredentials([usernamePassword(credentialsId: 'VERIFY_STATUS', passwordVariable: 'VERIFY_PASSWORD', usernameVariable: 'VERIFY_USER')]) {
    sh("""
  if [ -z "\$GERRIT_HOST" ] ; then
    echo Not running for a Gerrit change, skipping vote.
    exit 0
  fi
  if [ ! -d venv ] ; then
    virtualenv -p \$(which python3) venv
  fi
  . venv/bin/activate
  pip -q install requests
  ./tf-m-ci-scripts/jenkins/verify.py --category ${category} --value ${value} --verify-name ${verify_name} --user \$VERIFY_USER
  """)
  }
}

def comment(comment) {
  node("docker-amd64-xenial") {
    cleanWs()
    dir("tf-m-ci-scripts") {
      git url: '$CI_SCRIPTS_REPO', branch: 'master', credentialsId: 'GIT_SSH_KEY'
    }
    commentInWorkspace(comment)
  }
}

def commentInWorkspace(comment) {
  withCredentials([usernamePassword(credentialsId: 'VERIFY_STATUS', passwordVariable: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USER')]) {
    sh("""
  if [ -z "\$GERRIT_HOST" ] ; then
    echo Not running for a Gerrit change, skipping.
    exit 0
  fi
  if [ ! -d venv ] ; then
    virtualenv -p \$(which python3) venv
  fi
  . venv/bin/activate
  pip -q install requests
  ./tf-m-ci-scripts/jenkins/comment.py --comment "${comment}" --user \$GERRIT_USER
  """)
  }
}
