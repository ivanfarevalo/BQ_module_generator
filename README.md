# Bisque Module Generator
##### V2.0.0

Standardizes and automates the process of creating modules that can be integrated in the Bisque web application.
This command line interface (CLI) supports multiple inputs and outputs of type image, table or file. Output images will be 
displayed in the module results section in Bisque while tables and file outputs will have links to their 
respective resource service where they can be downloaded and visualized.  
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
You should create a `Modules` folder which will only contain the modules that you wish to test in Bisque.
You should name your `{ModuleName}` folder how you would like your module to appear in bisque, for ex. `EdgeDetection`.
Create a folder named `src` and place all your source code inside it. Finally, create a python file named `BQ_run_module.py` inside the `src` folder. 

#### BQ_run_module.py
Include all necessary data reading and pre-processing 
code in `BQ_run_module.py` as well as a function named `run_module` that will take `input_path_dict` and `output_folder_path`.
Hyper parameters for running the module will have to be hardcoded for now but future releases will extend functionality  for theses as well. 
This function should load input resources from `input_path_dict`, do any preprocessing steps, run the algorithm,
save all outputs to `output_folder_path`, ***AND return the `outputs_path_dict`***.

##### input_path_dict
The `input_path_dict` parameter is a dictionary with input names as keys and their corresponding paths as values. 
***It is important to note that these input names will be the labels that Bisque will display in your module web page.***

![Input Example](https://github.com/ivanfarevalo/BQ_module_generator/raw/main/public/input_ex.png)

***These input names must also match the input names specified with the cli in a later step.*** This will become clear later, 
for now, just choose some descriptive 
and unique input names that you would like Bisque to display in the module web page. You will use these input names to 
index the `input_path_dict` dictionary and load each resource from its respective path. Ex:
```python
input_img_path = input_path_dict['Input Image']
img = cv2.imread(input_img_path, 0)
```

##### output_folder_path
The `output_folder_path` parameter is a path to the directory where output results should be saved. 

##### output_paths_dict
You should save all output result paths into a dictionary with descriptive and unique output names as keys. ***These 
output names will be used by Bisque as labels in your module results web page.*** Ex:
```bash
output_paths_dict = {}
output_paths_dict['Output Image'] = output_img_path
```

![Output Example](https://github.com/ivanfarevalo/BQ_module_generator/raw/main/public/output_ex.png)

These output paths must also be the same names used to specify 
outputs with the cli at a later step. The `run_module` function must return this dictionary of output paths in order for
Bisque to read and post results back to the module web page.

A sample BQ_run_module.py is shown below:
```python
import cv2
import os
from detection import canny_detector

# input_path_dict will have input file paths with keys corresponding to the input names set in the cli.
def run_module(input_path_dict, output_folder_path, min_hysteresis=100, max_hysteresis=200):
    """
    This function should load input resources from input_path_dict, do any pre-processing steps, run the algorithm,
    save all outputs to output_folder_path, AND return the outputs_path_dict.
    
    :param input_path_dict: Dictionary of input resource paths indexed by input names. 
    :param output_folder_path: Directory where to save output results.
    :param min_hysteresis: Tunable parameter must have default values.
    :param max_hysteresis: Tunable parameter  must have default values.
    :return: Dictionary of output result paths.
    """
    
    ##### Preprocessing #####

    # Get input file paths from dictionary
    input_img_path = input_path_dict['Input Image'] # KEY MUST BE DESCRIPTIVE, UNIQUE, AND MATCH INPUT NAME SET IN CLI

    # Load data
    img = cv2.imread(input_img_path, 0)

    ##### Run algorithm #####

    edges_detected = canny_detector(img, min_hysteresis, max_hysteresis)


    ##### Save output #####

    # Get filename
    input_img_name = os.path.split(input_img_path)[-1][:-4]

    # Generate desired output file names and paths
    output_img_path = "%s/%s_out.jpg" % (output_folder_path, input_img_name) # CHECK FILE EXTENSION!

    # Save output files
    cv2.imwrite(output_img_path, edges_detected)

    # Create dictionary of output paths
    output_paths_dict = {}
    output_paths_dict['Output Image'] = output_img_path  # KEY MUST BE DESCRIPTIVE, UNIQUE, AND MATCH OUTPUT NAME SET IN CLI

    ##### Return output paths dictionary #####  -> IMPORTANT STEP
    return output_paths_dict

if __name__ == '__main__':
    # Place some code to test implementation
    
    # Define input_path_dict and output_folder_path
    input_path_dict = {}
    current_directory = os.getcwd()
    # Place test image in current directory
    input_path_dict['Input Image'] = os.path.join(current_directory,'test_image.jpg') # KEY MUST MATCH INPUT NAME SET IN CLI
    output_folder_path = current_directory
    
    # Run algorithm and return output_paths_dict
    output_paths_dict = run_module(input_path_dict, output_folder_path, min_hysteresis=100, max_hysteresis=200)
    
    # Get outPUT file path from dictionary
    output_img_path = output_paths_dict['Output Image'] # KEY MUST MATCH OUTPUT NAME SET IN CLI
    # Load data
    out_img = cv2.imread(output_img_path, 0)
    # Display output image and ensure correct output
    cv2.imshow("Results",out_img)
```

***IT IS IMPORTANT TO TRIPLE CHECK OUTPUT FILE EXTENSIONS TO AVOID BUGS WHEN UPLOADING RESULTS BACK TO BISQUE!***

#### Containerizing application 

Test your `BQ_run_module.py` file by writing some test code in the `if __name__ == '__main__':` code block. 
A simple test implementation is shown above. Once `BQ_run_module.py` is
working as expected, you can containerize your application with docker. Follow the instructions on [downloading docker](https://www.docker.com/products/docker-desktop),
[creating a Dockerfile](https://docker-curriculum.com/#dockerfile), and [running a container](https://docker-curriculum.com/#docker-run). 
Here is an example of a Dockerfile for a simple edge detection module. 

***You must include the section `Copy Source Code` in your own Dockerfile.*** 

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
and test your application inside the container by calling `python BQ_run_module.py`. 

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

***For Python3 modules, you must copy the bqapi folder from the `BQ_module_generator` folder into your `{ModuleName}` folder.***
Your folder structure should look like this so far:
```
-- Modules
    -- {ModuleName}
        -- bqapi (Only for python3 modules)
        -- Dockerfile
        -- src
            -- {source_code}
            -- BQ_run_module.py
```

The **bqmod** CLI uses simple commands to populate a .json file with the configurations details of your module. 
All commands must be ran in your `{ModuleName}` folder and are preceded with the `bqmod` command.

| Command                   | Options            | Description |
|---------------------------|--------------------|-------------|
| **`bqmod`**               | --help             | Shows help information on how to use the CLI            |
| **`bqmod init`**          |                    | Initializes configuration file for your module and pulls necessary files from repo. If one already exists, it wills ask whether you would like to overwrite it.|
| **`bqmod set`**           | -n --name          | Sets or changes the {ModuleName} field. This must match the {ModuleName} of your module folder and should not have spaces. Ex: **`bqmod set -n "EdgeDetection"`** |
|                           | -a --authors       | Sets or changes the name of the authors.  Ex: **`bqmod set -a "Ivan"`** |
|                           | -d --description   | Sets or changes a short description of the module. Must be in quotations. Ex: **`bqmod set -d "This module finds edges in images"`** |
| **`bqmod inputs`**        | -i --image         | Flag that sets an input of type image. |
|                           | -t --table         | Flag that sets an input of type table. |
|                           | -f --file          | Flag that sets an input of type file. |
|                           | -n --name          | Required parameter. Sets the name of the input as will be shown in Bisque module page. ***Input names MUST match input_path_dict keys in BQ_module_run.py.*** |
| **`bqmod outputs`**       | -i --image         | Flag that sets and output of type image.|
|                           | -t --table         | Flag that sets and output of type table. |
|                           | -f --file          | Flag that sets and output of type file. |
|                           | -n --name          | Required parameter. Sets the name of the output as will be shown in Bisque results section. ***Output names MUST match output_paths_dict keys in BQ_module_run.py.*** |
| **`bqmod summary`**       |                    | Prints out the current module configurations. |
| **`bqmod gen_help_html`** |                    | Generates help.html from help.md. |
| **`bqmod create_module`** |                    | Generates the module .xml. |

***It is crucial to note that the names for inputs and outputs MUST match the dictionary keys of input_path_dict and 
output_paths_dict respectively!*** Failure to ensure this will result in an error at runtime.

![Dictionary Keys Example](https://github.com/ivanfarevalo/BQ_module_generator/raw/main/public/dict_name_ex.png)

Here's an example of creating a simple Edge Detection module:

```bash
ivan@bisque:~/Bisque/Modules$ cd EdgeDetection
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod init
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod set -n "EdgeDetection"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod set -a "Ivan"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod set -d "This module finds edges in images"
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod inputs --image -n "Input Image"   # THIS MUST MATCH DICTIONARY KEYS in input_path_dict
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod outputs --image -n "Output Image"   # THIS MUST MATCH DICTIONARY KEYS in output_paths_dict
ivan@bisque:~/Bisque/Modules/EdgeDetection$ bqmod summary
Name: EdgeDetection
Author: Ivan
Description: This module finds edges in images
Inputs: {'Input Image': 'image'}
Outputs: {'Output Image': 'image'}
ivan@bisque:~/Bisque/Modules/EdgeDetection bqmod create_module
EdgeDetection.xml created
```

#### Generating help html file
Edit the `help.md` [markdown](https://www.markdownguide.org/basic-syntax/) file in the `public` folder to include any documentation and examples you want to provide users.
When you are done, generate the html file by running `bqmod gen_help_html` from the `{ModuleName}` folder.



#### Module Folder Structure
This should be the resulting folder structure after creating the module.

```
-- Modules
    -- {ModuleName}
        -- bqapi (Only for python3 modules)
        -- bqconfig.json
        -- public
            -- thumbnail.png (module icon for bisque)
            -- help.md (Help markdown)
            -- help.html (Help html)
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
***Remeber to change the .xml file name to your {ModuleName}.xml file***

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

# Replace the following line with your {ModuleName}.xml
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
docker.image = edgedetection:v2.0.0     # Only edit this line
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
You can also read the following [article (Windows, Mac)](https://www.techbout.com/find-public-and-private-ip-address-44552/) 
or [article (Linux)](https://phoenixnap.com/kb/how-to-find-ip-address-linux) to find 
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
* Make sure that the mounted folder `-v $(pwd):/source/modules` contains the `{ModuleName}` folders of the modules you want to test. 
You should be in your `Modules` folder when running the docker container.
* Make sure that the `.xml` file in your `{ModuleName}` folder and the `{ModuleName}` folder have the same name.
For example, for the `EdgeDetection` module, {ModuleName} should be `EdgeDetection` and the `.xml` should be named `EdgeDetection.xml`.
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


