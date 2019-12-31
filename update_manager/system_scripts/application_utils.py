#import os
from os import makedirs
from shutil import rmtree

version_control_dir="update_packages/"

def setup_new_application(name, branches, components):
    base_dir = version_control_dir+name

    try:
        makedirs(base_dir)
    except FileExistsError:
        print("Could not create base folders for the application, they already exist.")

    for branch in branches:
        # try:
        #     makedirs(base_dir+"/check/"+branch)
        # except FileExistsError:
        #     print("Could not create 'check' branch folders for the application, they already exist. Branch:" + branch)

        try:
            makedirs(base_dir+"/"+branch)
        except FileExistsError:
            print("Could not create 'download' branch folders for the application, they already exist. Branch:" + branch)

        for component in components:
            # try:
            #     makedirs(base_dir+"/check/"+branch+"/"+component)
            # except FileExistsError:
            #     print("Could not create 'check' branch folders for the application, they already exist. Branch:" + branch)

            try:
                makedirs(base_dir+"/"+branch+"/"+component)
            except FileExistsError:
                print("Could not create 'download' branch folders for the application, they already exist. Branch:" + branch)


def cleanup_application_postdelete(name):
    try:
        rmtree(version_control_dir+name)
    except FileNotFoundError:
        print("Application cleanup not necessary, no application folder found.")
