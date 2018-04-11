#!/usr/bin/env python2
#encoding: UTF-8

###################################################################
#                                                                 #
# Copyright (C) 2016 Divine Threepwood                            #
#                                                                 #
# File   : csra-release.py                                        #
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
from git import *
from git.objects.base import *
import shutil
from termcolor import colored
import getpass
import json
import json



if __name__ == "__main__":

    temp_folder = "/tmp/"+str(getpass.getuser())+"/csra-release"
    config_file_uri = "./csra-release-whitelist.cfg"

    try:
        # load config file
        with open(config_file_uri, "r+") as config_file:
            release_config = json.load(config_file)
            release_version = release_config['version']
            for repo in release_config['repos']:
                project_name = repo['url'].rsplit('/', 1)[-1]
                print("release "+release_version+" of project "+project_name+" from branch["+repo['branch']+"]...")
                
                git_repo = Repo.clone_from(repo['url'], temp_folder+"/"+project_name, branch=repo['branch'])
                try:
                    new_tag = git_repo.create_tag(release_version, message='Automatic release of tag "{0}"'.format(release_version)) 

                except Exception as ex:
                    print(colored("ERROR:", 'red') +" Could not tag project "+colored(project_name, 'blue')+"! Tag "+colored(release_version, 'blue')+" may already exist?")
                    continue
                git_repo.remotes.origin.push(new_tag)
                

        # cleanup
    finally:
        shutil.rmtree(temp_folder)
