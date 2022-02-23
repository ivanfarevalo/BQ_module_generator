# Bisque Module Generator
##### V1.0.4

Standardizes and automates the process of creating modules that can be integrated in the Bisque web application.
This command line interface (CLI) currently supports any input types supported by Bisque but can only display image and table outputs. 
Custom outputs or interactive parameters will require users to manually edit some files.
Regardless of your application, it is a good idea to follow this guide and use the CLI to automate a big part of the 
process and avoid common bugs. Once you have reached the end of this guide, if you need more customization, please take 
a look at the [Official Bisque Documentation](https://ucsb-vrl.github.io/bisqueUCSB/module-development.html) 
for a full guide on how to build modules from scratch. The [XML section](https://ucsb-vrl.github.io/bisqueUCSB/module-xml.html) 
will provide you with some common features that 
users might want to include in their module and how to define them in the xml. The vision for this project is for users to
build their modules without the need to edit the module files which can be tedious and time consuming to write. 
I will continuously  update this guide and the code to include as many features as possible.

## Before cloning repo:
Before cloning this repo, structure your module in the following manner.
```
-- Modules
    -- {ModuleName}
        -- src
            -- {source_code}
            -- BQ_run_module.py
```
You should create a `Modules` folder which will only  contain the modules that you wish to test in Bisque.
You should name your `{ModuleName}` folder how you would like your module name to appear in bisque, for ex. `EdgeDetection`.
Create a folder named `src` and place all your source code inside it. Finally, create a python file named `BQ_run_module.py` inside the `src` folder. 

#### BQ_run_module.py
Include all necessary data pre-processing 
code in ```BQ_run_module.py``` as well as a function named ```run_module``` that will take ```input_file_path```, ```output_folder_path```, 
and any other tunable parameters to run your algorithm. For now this tunable parameters **must have a default value.** This function should load input data from the ```input_file_path``` parameters 
, save any outputs to the ```output_folder_path```, ***AND return the output file path***. A sample file is shown below:
```
import cv2
import os
from my_source_code import canny_detector

# Tunable parameters must have defaults!
def run_module(input_file_path, output_folder_path, min_hysteresis=10, max_hysteresis=100): 

    ##### Preprocessing #####
    img = cv2.imread(input_file_path, 0)
    
    ##### Run algorithm #####
    edges_detected = canny_detector(img, min_hysteresis, max_hysteresis)
    
    ##### Save output #####
    
    # Get filename
    file_name = os.path.split(input_file_path)[-1][:-4]
    
    # Generate desired output file name and path
    output_file_path = f"{output_folder_path}/{file_name}_out.png"
    cv2.imwrite(output_file_path, edges_detected)
    
    ##### Return output file path #####  -> Important step
    return output_file_path
    
if __name__ == '__main__':
    # Some code to test implementation, test with absolute paths to avoid bugs
    
    root_folder_path = os.path.dirname(os.path.abspath(__file__)) # Absolute path to parent directory 
    input_file_path = os.path.join(root_folder_path, 'bob.jpg')
    output_folder_path = root_folder_path

    output_file_path = run_module(input_file_path, output_folder_path, 100, 200)
    print("Output file saved to: %s" % output_file_path)
    
```

#### Containerizing application 

Test your `run_module` function by placing an input file in the `src` folder, 
calling `python BQ_run_module.py` with the `input_file_path` pointing to the absolute test file path 
and the  `output_folder_path` pointing to the absolute path to the `src` folder. Once `BQ_run_module.py` is
working as expected, you can containerize your application with docker. Follow the instructions on [downloading docker](https://www.docker.com/products/docker-desktop),
[creating a Dockerfile](https://docker-curriculum.com/#dockerfile), and [running a container](https://docker-curriculum.com/#docker-run). 
Here is an example of a Dockerfile for a simple edge detection module.

```
# ==================================================================
# module list
# ------------------------------------------------------------------
# python        3.6    (apt)
# ==================================================================

FROM python:3.6.15-buster

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

# ===================Module Dependencies============================

RUN pip3 install cycler imageio kiwisolver matplotlib numpy opencv-python Pillow pyparsing python-dateutil scipy 

# ===================Copy Source Code===============================

RUN mkdir /module
WORKDIR /module

COPY src /module/src
```
Create your image by running `docker build -t {modulemame}:v0.0.0 .` in your `{ModuleName}` folder. Note that docker
images are only allowed to have lowercase letters.
Run your docker container with `docker run -it {modulemame}:v0.0.0 bash`
and test your application inside the container by calling ```python BQ_run_module.py```. 

## Generating Module Files

Now that you have containerized and tested your application, you are ready to pull this repo and create the Bisque module.

#### Installing the bqmod CLI

First step is to clone this repo and install the CLI. You can create a virtual environment in which to install
the CLI if you wish.
```bash
# Go to a directory outside your Modules folder and clone the rep
ivan@bisque:~/Bisque/Modules$ cd ~/Bisque
ivan@bisque:~/Bisque$ git clone https://github.com/ivanfarevalo/BQ_module_generator.git

# Go into the BQ_module_generator folder
ivan@bisque:~/Bisque$ cd BQ_module_generator

# This is optional
ivan@bisque:~/Bisque/BQ_module_generator$ virtualenv bqvenv
ivan@bisque:~/Bisque/BQ_module_generator$ . bqvenv/bin/activate

# This is required
(bqvenv) ivan@bisque:~/Bisque/BQ_module_generator$ pip3 install --editable .
```
Test the installation by running ```bqmod --help```. You should get a help message. Remember to activate your virtual environment
if you used one during installation, otherwise you wont be able to run the commands.

#### Using the bqmod CLI

First you must copy the following files and folders from the `BQ_module_generator` folder into your `{ModuleName}` folder:
```bash
# Files
PythonScriptWrapper.py
xml_template.xml
runtime-module.cfg

# Folders
bqapi (Only for python3 modules)
public
```
Your folder structure should look like this so far:
```
-- Modules
    -- {ModuleName}
        -- bqapi (Only for python3 modules)
        -- public
            -- thumbnail.png (module icon displayed in bisque)
        -- Dockerfile
        -- PythonScriptWrapper.py
        -- runtime-module.cfg
        -- src
            -- {source_code}
            -- BQ_run_module.py
        -- xml_template.xml
```

The **bqmod** CLI uses simple commands to populate a .json file with the configurations details of your module. 
All commands must be ran in your `{ModuleName}` folder and are preceded with the `bqmod` command.

| Command                   | Options            | Description |
|---------------------------|--------------------|-------------|
| **`bqmod`**               | --help             | Shows help information on how to use the CLI            |
| **`bqmod init`**          |                    | Initializes configuration file for your module. If one already exists, it wills ask whether you would like to overwrite it.|
| **`bqmod set`**           | -n --name          | Sets or changes the {ModuleName} field. This must match the {ModuleName} of your module folder and should not have spaces. Ex: **`bqmod set -n "EdgeDetection"`** |
|                           | -a --authors       | Sets or changes the name of the authors.  Ex: **`bqmod set -a "Ivan"`** |
|                           | -d --description   | Sets or changes a short description of the module. Must be in quotations. Ex: **`bqmod set -d "This module finds edges in images"`** |
| **`bqmod inputs`**        | -i --image            | Sets an input of type image. |
| **`bqmod outputs`**       | -i --image            | Sets and output of type image.|
|                           | -t --table            | Sets and output of type csv. |
|                           | -o --output_name   | Required parameter. Sets the name of the output as will be shown in Bisque results section. Ex: **`bqmod outputs --image -o "Edge Image"`** |
| **`bqmod summary`**       |                    | Prints out the current module configurations. |
| **`bqmod create_module`** |                    | Generates the module .xml. |

Here's an example of creating a simple Edge Detection module:

```bash
ivan@bisque:~/Bisque/Modules$ cd EdgeDetection
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod init
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod set -n "EdgeDetection"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod set -a "Ivan"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod set -d "This module finds edges in images"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod inputs --image
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod outputs --image -o "Edge Image"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod summary
Name: EdgeDetection
Author: Ivan
Description: This module finds edges in images
Inputs: ['image']
Outputs: ['image']
Output_names: ['Edge Image']
ivan@bisque:~/Bisque/Modules/EdgeDetection bqmod create_module
EdgeDetection.xml created
```

#### Module Folder Structure
This should be the resulting folder structure after creating the module.

```
-- Modules
    -- {ModuleName}
        -- bqapi (Only for python3 modules)
        -- public
            -- thumbnail.png (module icon for bisque)
        -- Dockerfile
        -- PythonScriptWrapper.py
        -- runtime-module.cfg
        -- src
            -- {source_code}
            -- BQ_run_module.py
        -- {ModuleName}.xml
        -- xml_template.xml
```
## Testing Module
You can now start testing your module in Bisque. The first step is to edit your Dockerfile to create a new image that
will include all the extra layers required for Bisque communication.

#### Editing Dockerfile
It is necessary to append a few commands to your Dockerfile.
These commands will install dependencies needed for python 3 modules, create the necessary folder structure, 
and copy the required files and folders into your module container.
If your module is written in Python 3, you need to make sure to copy the `bqapi` folder from this repo in your `{ModuleName}` folder as described above. 

Here is the updated Dockerfile for a simple Edge Detection module:

```
# ==================================================================
# module list
# ------------------------------------------------------------------
# python        3.6    (apt)
# ==================================================================

FROM python:3.6.15-buster

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

# ===================Module Dependencies============================

RUN pip3 install cycler imageio kiwisolver matplotlib numpy opencv-python Pillow pyparsing python-dateutil scipy 

# ===================Copy Source Code===============================

RUN mkdir /module
WORKDIR /module

COPY src /module/src

####################################################################
######################## Append From Here Down #####################
####################################################################

# ===============bqapi for python3 Dependencies=====================
# pip install in this exact order
RUN pip3 install six
RUN pip3 install lxml
RUN pip3 install requests==2.18.4
RUN pip3 install requests-toolbelt

# =====================Build Directory Structure====================

COPY PythonScriptWrapper.py /module/
COPY bqapi/ /module/bqapi
COPY EdgeDetection.xml /module/EdgeDetection.xml

ENV PATH /module:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PYTHONPATH $PYTHONPATH:/module/src
```
 

#### Creating Module Image
Once you update the Dockerfile, create a new Docker image by running the following command from your `{ModuleName}` folder.
Note that docker images must have lowercase names and tags. The `biodev.ece.ucsb.edu:5000/` prefix is needed for 
Bisque to pull the image. Once you are ready to deploy your application to production, you will push this image to the
specified repo.
```bash
docker build -t biodev.ece.ucsb.edu:5000/{modulename}:{tagname} .
```
It is good practice to specify a `{tagname}` that identifies the image versions. As you add functionalities and customize your module,
it is a good idea to keep track  of the various stable images of your module. By default, 
Docker will tag the image `latest` if a tag is not provided. The following are a few example of how you could tag your images:
```bash
# First stable module image
docker build -t biodev.ece.ucsb.edu:5000/edgedetection:v1.0.0 .
```
```bash
# Small bugs fixed
docker build -t biodev.ece.ucsb.edu:5000/edgedetection:v1.0.4 .
```
```bash
# Implementing some interactive parameters
docker build -t biodev.ece.ucsb.edu:5000/edgedetection:v1.2.0 .
```
```bash
# Second stable module image with all features implemented
docker build -t biodev.ece.ucsb.edu:5000/edgedetection:v2.0.0 .
```
You can also overwrite images by building with same `{modulename}:{tagname}` until you get to a point in which you want to
keep that specific image as reference.
#### Updating runtime-module-cfg
The runtime module configuration file specifies the image that Bisque will pull when a user runs your module.

The only line that should be updated is `docker.image = {modulename}:{tagname}`. This should specify the Docker image and tag name that you
wish to test or deploy on Bisque. This file will be called when a user hits the `Run` button in your module's page on Bisque. 
Note that the prefix `biodev.ece.ucsb.edu:5000/` is not included in this line, Bisque will prepend it before pulling your local image.

**IMPORTANT: It is very important to update the runtime-module.cfg each time you build an image with a different name or tag
so Bisque pulls the correct image you want to test.**

This is an example of a `runtime-module.cfg` for the EdgeDetection module:
```bash
#  Module configuration file for local execution of modules

module_enabled = True
runtime.platforms = command

[command]
docker.image = edgedetection:v2.0.1     # Only edit this line
environments = Staged,Docker
executable = python PythonScriptWrapper.py
files = pydist, PythonScriptWrapper.py
```

#### Running Bisque Container
Download the latest Bisque module development image by running:
```bash
docker pull amilworks/bisque-module-dev:git
```
The following command will launch a container named `bisque` on `http://{your.private.ip.address}:8080/`. The option `--v $(pwd):/source/modules`
will mount your local module located in your current directory `$(pwd)` to your container at `/source/modules`.
The `-v /var/run/docker.sock:/var/run/docker.sock` option will 
enable access to your local docker containers within the BisQue dev container. This is crucial 
because modules are ran as containers themselves so if you cannot run a container within a container, 
you will get an error.

```bash
# Navigate to the 'Modules' parent directory that holds your {ModuleName} folder.

ivan@bisque:~/Bisque$ cd ~/Bisque/Modules

# It should only contain the modules you intend to test on bisque, for Ex:

ivan@bisque:~/Bisque/Modules$ ls
EdgeDetection

# Run container
ivan@bisque:~/Bisque/Modules$ docker run --name bisque --rm -p 8080:8080 -v $(pwd):/source/modules -v /var/run/docker.sock:/var/run/docker.sock amilworks/bisque-module-dev:git
```
#### Logging Into Bisque
Navigate to `http://{your.private.ip.address}:8080/` on any web browser and Bisque should be up and running.
For example, if my ip address is `192.168.181.345`, you would navigate to `http://192.168.181.345:8080/`. 
You can find your private ip address by running: 
```bash
ifconfig | grep "inet.*broadcast.*" | awk '{print $2}'
```
or
```bash
ifconfig | grep "inet.*Bcast.*" | awk '{print $2}'
```
It will be the address that has twelve digits with a period after every third digit.
You can also read the following [article](https://www.techbout.com/find-public-and-private-ip-address-44552/) to find 
your private ip address if the previous commands didn't work.

If Bisque is not up, go into the container with `docker run -it amilworks/bisque-module-dev:git bash` and check the 
`bisque_8080.log` to debug. Report any issues on the [Bisque GitHub](https://github.com/UCSB-VRL/bisqueUCSB).

Login as admin using the credentials:
```bash
Username: admin
Password: admin
```

#### Upload Data

You can now upload any data that you need to test your module. In the top menu bar, go to `Upload -> Choose files -> Upload (at the bottom)`.
Exit out of the pop-up window and move on to register your module.

#### Register Module

In the top right hand corner, go to `Bisque admin -> Module Manager`. In the right panel, `Engine Modules`, fill in the Engine URL with:
```
http://{your.private.ip.address}:8080/engine_service
```
You can find your private ip address as mentioned above. 

Click `Load` to show all the modules that are in the `Modules` folder you mounted when running the Bisque docker image.
Drag and drop the module you want to test from the right panel to the left and exit out of the setting window.

If you don't see any modules on this list, go throught the following debug process:
* Check that the `Engine URL` is correct. If your ip address is `192.168.181.345` for example, your engine url should be
`http://192.168.181.345:8080/engine_service`.
* Make sure that the mounted folder `-v $(pwd):/source/modules` contains the `{ModuleName}` folders of that you want to test. 
You should be in your `Modules` folder when running the docker container.
* Make sure that the `.xml` file in your `{ModuleName}` folder has the same name as shown in the field 
`<module name="{ModuleName}" type="runtime">` of the xml. For example, for the `EdgeDetection` module, 
the `.xml` file should be named `EdgeDetection.xml` and should have the corresponding `<module name="EdgeDetection" type="runtime">` field.
* Make sure that your `{ModuleName}` folder has a `runtime-module.cfg` file.


#### Running Module

To run your module, click the `Analyse` button from the top menu bar and choose your module. If you don't see your module, 
refresh the page and try again.

Follow the steps to run your module and verify that the result is as expected. If Bisque reports any errors
or seems to be frozen, you can debug it by checking the logs in the Bisque container. Every time you hit the `Run` button,
Bisque starts a new container of your module and saves their corresponding logs in `/source/staging/{mex_id}`. Mex id's start with `00-` followed by
22 alphanumeric characters, Ex: `00-fMqFvjiHRjUfaff6GRy73M`. The `docker_run.log` logs information regarding
the pulling, starting, and stopping of your module container. The `PythonScript.log` logs information
regarding the communication between Bisque and your module. As mentioned at the beginning of these guide, if you would like to 
add custom outputs or interactive parameters, follow the in depth [guide](https://ucsb-vrl.github.io/bisqueUCSB/module-development.html) on creating modules.


