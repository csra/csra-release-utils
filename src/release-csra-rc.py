#!/usr/bin/env python2
#encoding: UTF-8

###################################################################
#                                                                 #
# Copyright (C) 2016 Divine Threepwood                            #
#                                                                 #
# File   : screenservice.py                                       #
# Authors: Divine Threepwood (Marian Pohling)                     #
#                                                                 #
#                                                                 #
# GNU LESSER GENERAL PUBLIC LICENSE                               #
# This file may be used under the terms of the GNU Lesser General #
# Public License version 3.0 as published by the                  #
#                                                                 #
# Free Software Foundation and appearing in the file LICENSE.LGPL #
# included in the packaging of this file.  Please review the      #
# following information to ensure the license requirements will   #
# be met: http://www.gnu.org/licenses/lgpl-3.0.txt                #
#                                                                 #
###################################################################

# import
from __future__ import print_function
import argparse
from git import *
import os
import os.path
from os.path import expanduser
from termcolor import colored
import json
import getpass
from collections import OrderedDict
import shutil
from citk_version_updater.main import main as citk_main
import coloredlogs, logging

coloredlogs.install()
_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())

# data type definition
class ProjectDescription(object):
    def __init__(self, project_name, project_version):
        self.project_name = project_name
        self.project_version = project_version


class DistributionReport(object):
    def __init__(self, projects_to_upgrade, projects_to_release):
        self.projects_to_upgrade = projects_to_upgrade
        self.projects_to_release = projects_to_release


def prepare_distribution_file(distribution_file):
    _LOGGER.info("=== " + colored("prepare distribution " + str(distribution_file), 'green') + " ===")
    projects_to_upgrade = []
    projects_to_release = []
    version_section_detected = False

    # collect project informations
    # with open(distribution_release_file, 'w') as release_file:
    with open(distribution_file) as dist_file:
        for line in dist_file.readlines():

            if "\"versions\":" in line:
                version_section_detected = True

            if version_section_detected:
                if "\"latest-stable\"" in line:
                    projects_to_upgrade.append(line.split('"')[1])
                    # projects_to_upgrade.append("'" + line.split('"')[1] + "'")
                if "\"master\"" in line and not "\"commit\"" in line and not "\"version-name\"" in line:
                    projects_to_release.append(ProjectDescription(line.split('"')[1], "master"))
                if "\"rc\"" in line:
                    project_name = line.split('"')[1]
                    if project_name != "variant":
                        projects_to_release.append(ProjectDescription(project_name, "rc"))
    return DistributionReport(projects_to_upgrade, projects_to_release)


def release_related_projects(projects_to_release, citk_path, distribution_release_name, release_version):
    _LOGGER.info("=== " + colored("release related projects", 'green') + " ===")
    
    tmp_folder = "/tmp/" + str(getpass.getuser()) + "/csra-release"
    try:
        # release projects
        for project_description in projects_to_release:
            project_repository_url = detect_repository_url(project_description.project_name, citk_path)
            if not project_repository_url:
                _LOGGER.error(colored("ERROR", 'red') + ": " + colored("could not detect repository url", 'red') + " of " + colored(project_description.project_name, 'blue') + "! Skip release of this project!")
                continue

            _LOGGER.info("create release branch " + colored(release_version, 'blue') + " of project " + project_description.project_name + " from branch " + colored(project_description.project_version, 'blue') + "...")
            git_repo = Repo.clone_from(project_repository_url, tmp_folder + "/" + project_description.project_name, branch=project_description.project_version)
            try:
                git_repo.git.checkout(b=str(release_version))
            except Exception as ex:
                _LOGGER.error(colored("ERROR:", 'red') + " Could not branch project " + colored(project_description.project_name, 'blue') + "! Branch " + colored(release_version, 'blue') + " may already exist?")
                _LOGGER.debug(ex, exc_info=True)
                continue
            git_repo.remotes.origin.push(str(release_version))
    # cleanup
    finally:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
    
    # upgrade versions in distribution file
    for project_description in projects_to_release:
        citk_main(["--citk", str(citk_path), "--project", str(project_description.project_name), "--distribution", str(distribution_release_name), "-v", "--version", str(release_version)])

def upgrade_versions_in_new_distribution(projects_to_upgrade, citk_path, distribution_release_name):
    _LOGGER.info("=== " + colored("upgrade versions in new distribution", 'green') + " ===")
    
    for project in projects_to_upgrade:
        citk_main(["--citk", str(citk_path), "--project", str(project), "--distribution", str(distribution_release_name), "-v"])

def push_distribution(citk_path, distribution_release_file, distribution_version):
    _LOGGER.info("=== " + colored("push distribution", 'green') + " ===")
    repo = Repo(citk_path)
    index = repo.index
    relative_dist_path = "distributions/" + distribution_release_file + ".distribution"
    _LOGGER.debug("add distrubtion_file " + relative_dist_path)

    index.add([relative_dist_path])
    index.commit("released version " + distribution_version + " from rc")
    _LOGGER.debug("remote " + str(repo.remotes[0]))
    try:
        repo.remotes[0].push()
    except Exception as ex:
        _LOGGER.info("Could not push commit: " + str(ex))


def print_info():
    _LOGGER.info("=== " + colored("release script successfully finished", 'green') + " ===")
    _LOGGER.info("=== "+colored("your next steps should be", 'blue')+" ===")
    _LOGGER.info("     "+colored("*", 'blue')+"  backup local models, images and data stored at the core machines!")
    _LOGGER.info("     "+colored("*", 'blue')+"  create jenkins release sync and generate distribution scripts.")
    _LOGGER.info("     "+colored("*", 'blue')+"  inform the other developers about the new release!")


def detect_repository_url(project_name, citk_path):
    _LOGGER.debug("detect repository url of project "+colored(project_name, 'blue'))
    project_file_name = citk_path + "/projects/" + project_name + ".project"
    _LOGGER.debug("try to open project: "+colored(project_file_name, 'blue'))

    if not os.path.isfile(project_file_name):
        print(colored("ERROR", 'red') + ": detected project file "+colored(project_file_name, 'blue') + " does not exists!")
        raise ValueError('Error 22')

    with open(project_file_name, "r+") as project_file:
        data = json.load(project_file, object_pairs_hook=OrderedDict, encoding="utf-8")

        # check if repository is defined

        if not 'repository' in data["variables"]:
            print(colored("ERROR", 'red') + ": no scm repository was not declared in project file "+colored(project_file_name, 'blue') + " which is needed for the auto project release!")
            raise ValueError('Error 23')


        if data["variables"]["repository"]:
             return data["variables"]["repository"]
        else:
            _LOGGER.error(colored("ERROR", 'red') + ": no scm repository was not declared in project file "+colored(project_file_name, 'blue') + " which is needed for the auto project release!")
            raise ValueError('Error 23')


def entry_point():
    exit(main())


def main(argv=None):

    # pre init
    distribution_name = "lsp-csra"
    distribution_version = "rc"

    try:
        
        # init
        citk_path = expanduser("~") + "/workspace/csra/citk"

        # parse command line
        parser = argparse.ArgumentParser(description='Script release the current release candidate.')
        parser.add_argument("--citk", default=citk_path, help='Path to the citk project which contains the project and distribution descriptions.')
        parser.add_argument("--distribution", default=distribution_name, help='The name and version of the release candidate distribution. e.g. lsp-csra')
        parser.add_argument("--version", help='The version to release.', required=True)
        parser.add_argument("-v", help='Enable this verbose flag to get more logging and exception printing during application errors.', action='store_true')
        args = parser.parse_args()
        citk_path = args.citk
        distribution_name = args.distribution
        distribution_version = args.version

        # config logger
        if args.v:
            _LOGGER.info("verbose mode enabled")
            _LOGGER.setLevel(logging.DEBUG)
        else:
            _LOGGER.info("verbose mode disabled")
            _LOGGER.setLevel(logging.INFO)

        # post init
        distribution_release_name = distribution_name + "-" + distribution_version
        distribution_file_uri = citk_path + "/distributions/" + distribution_release_name + ".distribution"

        # start release pipeline
        distribution_report = prepare_distribution_file(distribution_file_uri)
        release_related_projects(distribution_report.projects_to_release, citk_path, distribution_release_name, "release-" + str(distribution_version))
        upgrade_versions_in_new_distribution(distribution_report.projects_to_upgrade, citk_path, distribution_release_name)

        # auto push disabled because a manual validation should be performed first.
        # push_distribution(citk_path, distribution_release_name, distribution_version)
        print_info()
    except Exception as ex:
        _LOGGER.error("could not release " + colored("rc", 'red') + "!")
        if ex.message:
            _LOGGER.error(colored("ERROR", 'red') + ": " + ex.message)
        _LOGGER.info(ex, exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    main(sys.argv)

