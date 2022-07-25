import click
import markdown
import os
import json
import wget
import ast
from tabulate import tabulate
from xml_generator import XMLGenerator


@click.group("bqmod")
@click.pass_context
def bqmod(ctx):
    """
    bqmod is a command line tool that helps users create Bisque modules.

    \b
    For a comprehensive guide go here: https://github.com/ivanfarevalo/BQ_module_generator
    Step 1: Create bqconfig file with 'bqmod init' in {ModuleName} folder
    Step 2: Set module name, author, and short description with 'bqmod set'
    Step 3: Set input resource types and names with 'bqmod inputs'
    Step 4: Set output types and names with 'bqmod outputs'
    Step 5: Review module configurations with 'bqmod summary'
    Step 6: Check BQ_run_module dictionary keys match bqmowd input/output names with 'bqmod check_config'
    Step 7: Create module files with 'bqmod create_module'
    Step 8: Generate help.html from help.md with 'bqmod gen_help_html'
    """
    if ctx.invoked_subcommand == 'init':
        pass
    else:
        try:
            with open('bqconfig.json') as json_data_file:
                config = json.load(json_data_file)
                ctx.obj = config
        except IOError:
            raise click.UsageError("No configuration file 'bqconfig.json' found in %s."
                                   " All bqmod commands must be ran from your {ModuleName} folder."
                                   " Navigate to your {ModuleName} folder and try again or initialize a bqconfig "
                                   "file with `bqmod init` if you  haven't done so." % os.getcwd(), ctx=ctx)


def create_config_file():
    """
    Creates bqconfig.json file in current directory. It will store a dictionary of values used to generate {ModuleName}.xml.
    """

    # with open("bqconfig.json", "w") as json_data_file:
    #     config_data = {'Name': None, 'Author': None, 'Description': None, 'Inputs': {}, 'Outputs': {}}
    #     json.dump(config_data, json_data_file)

    config_data = {'Name': None, 'Author': None, 'Description': None, 'Inputs': {}, 'Outputs': {}}
    update_bqconfig(config_data)


def download_files(): #TODO help url
    """ Download PythonScriptWrapper, xml_template, runtime-module.cgf, thumbnail.jpg, and help.md if not present."""
    python_wrapper_url = "https://raw.githubusercontent.com/ivanfarevalo/BQ_module_generator/main/PythonScriptWrapper.py"
    xml_template_url = "https://raw.githubusercontent.com/ivanfarevalo/BQ_module_generator/main/xml_template"
    runtime_cfg_url = "https://raw.githubusercontent.com/ivanfarevalo/BQ_module_generator/main/runtime-module.cfg"
    thumbnail_url = "https://github.com/ivanfarevalo/BQ_module_generator/raw/main/public/thumbnail.jpg"
    help_url = "https://github.com/ivanfarevalo/BQ_module_generator/raw/main/public/help.md"
    # bqapi_url = "https://github.com/ivanfarevalo/BQ_module_generator/archive/main/bqapi.zip"

    cwd = os.getcwd()
    python_wrapper_path = os.path.join(cwd, 'PythonScriptWrapper.py')
    xml_template_path = os.path.join(cwd, 'xml_template')
    runtime_cfg_path = os.path.join(cwd, 'runtime-module.cfg')

    if not os.path.exists(python_wrapper_path):
        wget.download(python_wrapper_url, python_wrapper_path)
    if not os.path.exists(xml_template_path):
        wget.download(xml_template_url, xml_template_path)
    if not os.path.exists(runtime_cfg_path):
        wget.download(runtime_cfg_url, runtime_cfg_path)

    # Create public folder with thumbnail icon and help.md
    public_dir_path = os.path.join(cwd, 'public')
    if not os.path.exists(public_dir_path):
        os.mkdir(public_dir_path)

    xml_template_path = os.path.join(public_dir_path, 'thumbnail.jpg')
    runtime_cfg_path = os.path.join(public_dir_path, 'help.md')

    if not os.path.exists(xml_template_path):
        wget.download(thumbnail_url, os.path.join(public_dir_path, 'thumbnail.jpg'))
    if not os.path.exists(runtime_cfg_path):
        wget.download(help_url, os.path.join(public_dir_path, 'help.md'))


def update_bqconfig(bqconfig):
    with open("bqconfig.json", "w") as json_data_file:
        json.dump(bqconfig, json_data_file)

@bqmod.command("init")
@click.pass_context
def init(ctx):
    """  Initializes bqconfig.json and pulls needed files into current directory.

    If one already exits, prompts user if they would like to overwrite it."""

    if click.confirm('bqmod init will pull files into current directory, are you in your {ModuleName} folder?', abort=True):
        try:
            with open('bqconfig.json') as _ :
                if click.confirm('bqconfig.json with module configuration already in directory. Would you like to overwrite it?', abort=True):
                    create_config_file()
                if click.confirm("If you also wish to update any of the following files: "
                                 "(PythonScriptWrapper, xml_template, runtime-module.cfg, thumbnail.jpg, help.md), "
                                 "manually delete them and run bqmod init again. Have you already deleted any files "
                                 "you wish to update and wish to continue?",
                                     abort=True):
                    download_files()

        except IOError:
            create_config_file()
            download_files()


@bqmod.command("set", no_args_is_help=True)
@click.option("--name", "-n", default=None, help="Module name with no spaces. Same as {ModuleName} folder")
@click.option("--author", "-a", default=None, help="Authors' names in quotations")
@click.option("--description", "-d", default=None, help="Write short description in quotations")
@click.pass_context
def set(ctx, name, author, description):
    """ Set name of module, authors, and short description"""

    if name:
        ctx.obj['Name'] = name
    if author:
        ctx.obj['Author'] = author
    if description:
        ctx.obj['Description'] = description

    update_bqconfig(ctx.obj)

    # if name or author or description:
    #     with open("bqconfig.json", "w") as json_data_file:
    #         json.dump(ctx.obj, json_data_file)
    # else:
    #     click.echo("Need to include at least on option: --name, --author, --description")
    #     click.echo(ctx.invoked_subcommand)


@bqmod.command("inputs", no_args_is_help=True)
@click.option("--remove", is_flag=True, default=False, help="Flag to remove input")
@click.option("--image", "-i", is_flag=True, default=False, help="Flag to indicate input of type image")
@click.option("--table", "-t", is_flag=True, default=False, help="Flag to indicate input of type table")
@click.option("--file", "-f", is_flag=True, default=False, help="Flag to indicate input of any other type besides image or table")
@click.option("--name", "-n", required=True, default=None, help="Descriptive name of the input resource to be processed by Bisque. Ex. 'Input Image'")
@click.pass_context
def inputs(ctx, image, table, file, name, remove):  #  NEED TO ADD FUNCTIONALITY TO DELETE INPUT
    """Sets  an input type and name. Removes an input with --remove  flag.

    \b
    Supported inputs types : --image, --file, --table
    Ex. bqmod inputs --image --name "Segmented Image" """

    if remove:
        try:
            if ctx.obj['Inputs'][name]:
                if click.confirm('Removing input "%s". Would you like to continue?' % name, abort=True):
                    del ctx.obj['Inputs'][name]
        except KeyError:
            click.secho("No input named '%s' found." % name, fg='red')
    else:
        if image:
            input_type = 'image'
        elif file:
            input_type = 'file'  # Unsure if this works
        elif table:
            input_type = 'table'  # Unsure if this works
        else:
            raise click.UsageError('Must include input_resource type: --image, --table, --file', ctx=ctx)

        try:
            if ctx.obj['Inputs'][name]:
                if click.confirm('An input_resource with the name "%s" has already been set. Would you like to overwrite?' % name, abort=True):
                    ctx.obj['Inputs'][name] = input_type
        except KeyError:
            ctx.obj['Inputs'][name] = input_type

        update_bqconfig(ctx.obj)

        # with open("bqconfig.json", "w") as json_data_file:
        #     json.dump(ctx.obj, json_data_file)


@bqmod.command("outputs", no_args_is_help=True)
@click.option("--remove", is_flag=True, default=False, help="Flag to remove output") # NEED TO ADD TABLE FUNCT
@click.option("--image", "-i", is_flag=True, default=False, help="Flag to indicate output of type image") # NEED TO ADD TABLE FUNCT
@click.option("--table", "-t", is_flag=True, default=False, help="Flag to indicate table output")
@click.option("--file", "-f", is_flag=True, default=False, help="Flag to indicate output of any other type besides image or table")
@click.option("--name", "-n", required=True, default=None, help="Descriptive name of the output to be shown in Bisque result. Ex. 'Segmented Image'")
@click.pass_context
def outputs(ctx, image, table, file, name, remove):  #  NEED TO ADD FUNCTIONALITY TO DELETE OUTPUT
    """Set an output type and name. Removes an output with --remove  flag.

        \b
        Supported outputs include : --image, --table, --file
        Ex. bqmod outputs --image --name "Segmented Image" """

    if remove:
        try:
            if ctx.obj['Outputs'][name]:
                if click.confirm('Removing output "%s". Would you like to continue?' % name, abort=True):
                    del ctx.obj['Outputs'][name]
        except KeyError:
            click.secho("No output named '%s' found." % name, fg='red')
    else:
        if image:
            output_type = 'image'
        elif table:
            output_type = 'table'
        elif file:
            output_type = 'file'
        else:
            raise click.UsageError('Must include an output type: --image, --table, --file', ctx=ctx)

        try:
            if ctx.obj['Outputs'][name]:
                if click.confirm(
                        'An input_resource with the name "%s" has already been set. Would you like to overwrite?' % name,
                        abort=True):
                    ctx.obj['Outputs'][name] = output_type
        except KeyError:
            ctx.obj['Outputs'][name] = output_type

        update_bqconfig(ctx.obj)

        # with open("bqconfig.json", "w") as json_data_file:
        #     json.dump(ctx.obj, json_data_file)


@bqmod.command("summary")
@click.pass_context
def summary(ctx):
    """ Print bqmodule configuration settings."""
    for key in ctx.obj:
        click.secho("%s: %s" % (key, ctx.obj[key]), fg='green')


@bqmod.command("gen_help_html")
def gen_help_html():
    """ Creates help.html from help.md"""
    public_dir = os.path.join(os.getcwd(), 'public')

    try:
        with open(os.path.join(public_dir, 'help.md'), 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        with open(os.path.join(public_dir, 'help.html'), 'w') as f:
            f.write(html)
    except FileNotFoundError:
        raise click.FileError("No help file found at %s" % os.path.join(public_dir, 'help.md'))


@bqmod.command("create_module")
@click.pass_context
def create_module(ctx):
    """ Create module xml file from configurations set in bqconfig.json"""

    # Check whether there are any inconsistencies between dictionary keys in BQ_run_module and input/output fields set with bqmod
    config_error_flag = check_config_main(ctx.obj)

    if config_error_flag:

        if click.confirm(
            'Dictionary key mismatches were found in BQ_run_module.py. It is adviced to double check that the '
            'dictionary keys used in BQ_run_module.py match the input names set with bqmod. You should also check'
            'that the dictionary variable names are "input_path_dictionary" and "output_paths_dictionary" '
            'respectively. Do you still wish to continue creating the module?',
            abort=True):
            pass

    # The following lines, fill in xml_template with inputs, outputs, author name, module name, and description from
    # configuration file bqmconfig.json set with bqmod.

    BQ_module_xml = XMLGenerator(ctx.obj['Name'])
    BQ_module_xml.xml_set_module_name()

    for input_name in ctx.obj['Inputs']: # If empty, don't add
        BQ_module_xml.add_input(type=ctx.obj['Inputs'][input_name], input_name=input_name)

    BQ_module_xml.add_input(type='mex')
    BQ_module_xml.add_input(type='bisque_token')

    for output_name in ctx.obj['Outputs']: # If empty, don't add
        BQ_module_xml.add_output(output_name=output_name, type=ctx.obj['Outputs'][output_name])

    BQ_module_xml.edit_xml('title', ctx.obj['Name'])
    BQ_module_xml.edit_xml('authors', ctx.obj['Author'])
    BQ_module_xml.edit_xml('description', ctx.obj['Description'])
    BQ_module_xml.write_xml()

    click.secho("%s.xml created" % ctx.obj['Name'], fg='green')


def check_config_main(bqconfig_dict):
    """ Check module configurations for inconsistencies.

    Check module configurations and ensures keys used in the BQ_run_module.py
    dictionaries match input/output names set with bqmod CLI
    """

    # Standardized Input and Output dictionary names as described in documentation
    input_dictionary_name = 'input_path_dict'
    output_dictionary_name = 'output_paths_dict'

    valid_in_keys = []
    valid_out_keys = []

    check_mssg_input = []
    check_mssg_output = []
    dict_keys_mismatch = False
    missing_config_field = False

    for key in bqconfig_dict:

        # Check that bqconfig.json has all fields set
        if bqconfig_dict[key]:
            pass
        elif key == 'Inputs':
            if click.confirm("No input has been set. Do you wish to continue?", abort=True):
                pass
        else:
            click.secho("Required field '%s' was not set.", fg='red')
            missing_config_field = True

        if missing_config_field:
            click.secho("Run `bqmod summary` to review missing fields and run respective commands to set fields.")
            return

        if key == 'Inputs':
            valid_in_keys = list(bqconfig_dict[key].keys())

        if key == 'Outputs':
            valid_out_keys = list(bqconfig_dict[key].keys())

    # Open and parse BQ_run_module.py, find run_module function, and check that indexed keys match bq configuration.
    try:
        with open('test_keys.py') as bqrun:
            BQ_run_module = bqrun.read()

    except IOError:
        mssg = "No 'BQ_run_module.py' file found in %s" % os.path.join(os.getcwd(), 'src/BQ_run_module.py')
        click.secho("%s" % mssg, fg='red')
        return

    run_fn = []
    bq_tree = ast.parse(BQ_run_module)
    for n in ast.iter_child_nodes(bq_tree):
        try:
            if n.name == 'run_module':
                run_fn.append(n)
        except AttributeError:  # Anything without a name
            pass

    assert len(run_fn) == 1, "There should be exactly 1 'run_module' function. None or multiple found."

    run_fn = run_fn[0]

    used_inkeys = {1}
    used_inkeys.remove(1)  # Some bug on Click doesn't allow for instantiating empty set
    used_outkeys = {1}
    used_outkeys.remove(1)  # Some bug on Click doesn't allow for instantiating empty set

    for node in ast.walk(run_fn):
        if isinstance(node, ast.Subscript) and node.value.id in (input_dictionary_name, output_dictionary_name):
            try:
                key = node.slice.value.s  # Python < 3.9
            except AttributeError:
                key = node.slice.value  # Python => 3.9

            if node.value.id == input_dictionary_name:
                if key not in valid_in_keys:
                    check_mssg_input.append("Invalid %s key '%s' used in BQ_run_module.py on line %s" % (
                    input_dictionary_name, key, node.lineno))
                used_inkeys.add(key)
            else:
                if key not in valid_out_keys:
                    check_mssg_output.append("Invalid %s key '%s' used in BQ_run_module.py on line %s" % (
                    output_dictionary_name, key, node.lineno))
                used_outkeys.add(key)

    # Sets seem to have some problem  with Click if initialized with set(). This is a workaround.
    missed_inkeys = {1}
    missed_inkeys.remove(1)
    for k in valid_in_keys:
        missed_inkeys.add(k)
    missed_inkeys = missed_inkeys - used_inkeys

    missed_outkeys = {1}
    missed_outkeys.remove(1)
    for k in valid_out_keys:
        missed_outkeys.add(k)
    missed_outkeys = missed_outkeys - used_outkeys


    for k in missed_inkeys:
        check_mssg_input.append("Missing input key '%s' in BQ_run_module.py" % k)

    for k in missed_outkeys:
        check_mssg_output.append("Missing output key '%s' in BQ_run_module.py" % k)

    print(tabulate(
        {"Input Names set with bqmod": valid_in_keys,
         "Input Dictionary Keys used in BQ_run_module.py": used_inkeys}, headers="keys", tablefmt="orgtbl"))

    print('\n')
    if check_mssg_input:
        click.secho("Mismatched input dictionary keys found", fg='red')
        for mssg in check_mssg_input:
            click.secho("%s" % mssg, fg='red')
            # print(mssg)
            dict_keys_mismatch = True
    else:
        click.secho("No mismatched input dictionary keys found", fg='green')

    print('\n')
    print(tabulate(
        {"Output Names set with bqmod": valid_out_keys,
         "Output Dictionary Keys used in BQ_run_module.py": used_outkeys}, headers="keys", tablefmt="orgtbl"))

    print('\n')
    if check_mssg_output:
        click.secho("Mismatched ouput dictionary keys found", fg='red')
        for mssg in check_mssg_output:
            click.secho("%s" % mssg, fg='red')
            dict_keys_mismatch = True
    else:
        click.secho("No mismatched dictionary keys found", fg='green')

    return dict_keys_mismatch



@bqmod.command("check_config")
@click.pass_context
def check_config(ctx):
    """ Check module configurations for inconsistencies."""

    return check_config_main(ctx.obj)



if __name__ == '__main__':
    bqmod()