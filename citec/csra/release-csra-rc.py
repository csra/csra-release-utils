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
from git.objects.base import *
from os import system
from os.path import expanduser
from termcolor import colored

# data type definition
class ProjectDescription(object):
    def __init__(self, project_name, project_version):
        self.project_name = project_name
        self.project_version = project_version
        
class DistributionReport(object):
    def __init__(self, projects_to_upgrade, projects_to_release):
        self.projects_to_upgrade = projects_to_upgrade
        self.projects_to_release = projects_to_release

def create_distribution_file(distribution_file, distribution_release_file, distribution_version):
    print ("create distribution " + str(distribution_release_file) + " ...")
    projects_to_upgrade = []
    projects_to_release = []
    with open(distribution_release_file, 'w') as release_file:
        with open(distribution_file) as dist_file:
            for line in dist_file.readlines():
                if "\"latest-stable\"" in line:
                    #print("found latest stable " + line.split('"')[1])
                    projects_to_upgrade.append("'" + line.split('"')[1] + "'")
                if "\"master\"" in line:
                    #print("found master " + line.split('"')[1])
                    projects_to_release.append(ProjectDescription(line.split('"')[1], "master"))
                if "\"rc\"" in line:
                    project_name = line.split('"')[1]
                    if project_name != "variant":
                        #print("found rc " + line.split('"')[1])
                        projects_to_release.append(ProjectDescription(project_name, "rc"))
                if "\"name\"" in line:
                    context = line.split(':')
                    context[1] = " \"lsp-csra-" + distribution_version + "\",\n"
                    line = ':'.join(context)
                if "\"variant\"" in line:
                    context = line.split(':')
                    context[1] = " \"" + distribution_version + "\",\n"
                    line = ':'.join(context)
                release_file.write(line)

    return DistributionReport(projects_to_upgrade, projects_to_release)

def release_related_projects(projects_to_release, citk_path, distribution_release_name, release_version):
    print ("release releated projects...")
    for project_description in projects_to_release:
        system("citk-version-updater --citk " + str(citk_path) + " --project " + str(project_description.project_name) + " --distribution " + str(distribution_release_name) + " -v --version " + str(release_version))

def upgrade_versions_in_new_distribution(projects_to_upgrade, citk_path, distribution_release_name):
    print ("upgrade versions in new distribution...")
    for project in projects_to_upgrade:
        system("citk-version-updater --citk " + str(citk_path) + " --project " + str(project) + " -v --distribution " + str(distribution_release_name))
    
#def appliy_custom_release_modifications():
#    print ("prepare new distribution for release...")
    
#def verify_new_distribution():
#    print ("verify new distribution...")
    
def push_distribution(citk_path, distribution_release_file, distribution_version):
    print ("push distribution...")
    repo = Repo(citk_path)
    index = repo.index
    relative_dist_path = "distributions/" + distribution_release_file + ".distribution"
    #print("add distrubtion_file " + relative_dist_path)
    index.add([relative_dist_path])
    index.commit("released version " + distribution_version + " from rc")
    #print("remote " + str(repo.remotes[0]))
    try:
        repo.remotes[0].push()
    except Exception as ex:
        print("Could not push commit: " + str(ex))
    
def print_info():
    print ("=== " + colored("release scipt successfully finished", 'green') + " ===")
    print ("=== your next steps should be:")
    print ("     *  backup local models, images and data stored at the core maschines!")
    print ("     *  create jenkins scripts")
    print ("     *  informe the other developer about the new release!")
        
if __name__ == "__main__":
    
    # pre init
    distribution_name = "lsp-csra-rc"
    distribution_version = ""
    verbose_flag = False
    
    try:
        
        # init
        citk_path = expanduser("~") + "/workspace/csra/citk"

        # parse command line
        parser = argparse.ArgumentParser(description='Script release the current release candidate.')
        parser.add_argument("--citk", default=citk_path, help='Path to the citk project which contains the project and distribution descriptions.')
        parser.add_argument("--distribution", default=distribution_name, help='The name of the release candidate distribution.')
        parser.add_argument("--version", help='The version which is used for the release.', required=True)
        parser.add_argument("-v", default=verbose_flag, help='Enable this verbose flag to get more logging and exception printing during application errors.', action='store_true')
        args = parser.parse_args()
        citk_path = args.citk
        distribution_name = args.distribution
        distribution_version = args.version
        verbose_flag = args.v
        
        # post init
        distribution_file_uri = citk_path + "/distributions/" + distribution_name + ".distribution"
        distribution_release_name = "lsp-csra-" + distribution_version
        distribution_release_uri = citk_path + "/distributions/" + distribution_release_name + ".distribution"
        
        # start release pipeline
        distribution_report = create_distribution_file(distribution_file_uri, distribution_release_uri, distribution_version)
        release_related_projects(distribution_report.projects_to_release, citk_path, distribution_release_name, distribution_version)
        upgrade_versions_in_new_distribution(distribution_report.projects_to_upgrade, citk_path, distribution_release_name)
        #push_distribution(citk_path, distribution_release_name, distribution_version)
        print_info()
    except Exception as ex:
        print("could not release " + colored("rc", 'red') + "!")
        if ex.message:
            print("error: " + ex.message)
            if verbose_flag:
                print (ex)
        exit(1)
    
    exit(0)
  
                   
                



