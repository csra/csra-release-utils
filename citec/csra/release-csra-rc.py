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
import os
import shutil
from termcolor import colored
import getpass
import json
from collections import OrderedDict
import json
from os import system
from os.path import expanduser

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
    with open(distribution_release_file, 'w') as release_file:
        with open(distribution_file) as dist_file:
            for line in dist_file.readlines():
                if "\"latest-stable\"" in line:
                    print("found latest stable " + line)
                if "\"master\"" in line:
                    print("found master " + line)
                if "\"rc\"" in line:
                    print("found rc " + line)
                if "\"name\"" in line:
                    context = line.split(':')
                    context[1] = " \"lsp-csra-" + distribution_version + "\",\n"
                    line = ':'.join(context)
                if "\"variant\"" in line:
                    print("found variant " + line)
                    context = line.split(':')
                    context[1] = " \"" + distribution_version + "\",\n"
                    line = ':'.join(context)
                release_file.write(line)

    return DistributionReport(['jul', 'bco.dal'], [ProjectDescription("lsp-csra.system-startup", "rc"), ProjectDescription("bco.registry.csra-db", "master")])

def release_related_projects(projects_to_release):
    print ("release releated projects...")

def upgrade_versions_in_new_distribution(projects_to_upgrade, citk_path, distribution_release_name):
    print ("upgrade versions in new distribution...")
    for project in projects_to_upgrade:
        system("citk-version-updater --citk "+str(citk_path)+" --project "+str(project)+" --distribution "+str(distribution_release_name))
    
def appliy_custom_release_modifications():
    print ("prepare new distribution for release...")
    
def verify_new_distribution():
    print ("verify new distribution...")
    
def push_distribution():
    print ("push distribution...")
    
def create_release_folder_structure():
    print ("create release folder structure")
    
def create_new_jenkins_entries():
    print ("create jenkins entries...")
    system("./test-script.py")
        
if __name__ == "__main__":
    
    # pre init
    distribution_name = "lsp-csra-rc"
    distribution_version = "0.4"
    
    try:
        
        # init
        citk_path = expanduser("~") + "/workspace/csra/citk"

        # parse command line
        parser = argparse.ArgumentParser(description='Script release the current release candidate.')
        parser.add_argument("--citk", default=citk_path, help='Path to the citk project which contains the project and distribution descriptions.')
        parser.add_argument("--distribution", default=distribution_name, help='The name of the release candidate distribution.')
        parser.add_argument("--version", default=distribution_version, help='The version which is used for the release.')
        args = parser.parse_args()
        citk_path = args.citk
        distribution_name = args.distribution
        distribution_version = args.version
        
        # post init
        tmp_repo_directory = "/tmp/" + str(getpass.getuser()) + "/"
        distribution_file_uri = citk_path + "/distributions/" + distribution_name + ".distribution"
        distribution_tmp_file_uri = citk_path + "/distributions/." + distribution_name + ".distribution.tmp"
        distribution_release_name = "lsp-csra-" + distribution_version
        distribution_release_uri = citk_path + "/distributions/" + distribution_release_name + ".distribution"
        
        # start release pipeline
        distribution_report = create_distribution_file(distribution_file_uri, distribution_release_uri, distribution_version)
        release_related_projects(distribution_report.projects_to_release)
        upgrade_versions_in_new_distribution(distribution_report.projects_to_upgrade, citk_path, distribution_release_name)
        appliy_custom_release_modifications()
        verify_new_distribution()
        push_distribution()
        create_release_folder_structure()
        create_new_jenkins_entries()
    except Exception as ex:
        print("could not release " + colored("rc", 'red') + "!")
        if ex.message:
            print("error: "+ex.message)
        exit(1)
    print ("successfully finished.")
    exit(0)
  
                   
                



