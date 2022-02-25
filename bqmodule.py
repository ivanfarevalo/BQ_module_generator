import click
import json
from xml_generator import XMLGenerator


@click.group("bqmod")
@click.pass_context
def bqmod(ctx):
    """
    bqmod is a command line tool that helps users create Bisque modules.

    \b
    For a comprehensive guide go here: https://github.com/ivanfarevalo/BQ_module_generator
    Step 1: Create bqconfig file with 'bqmod init'
    Step 2: Set module name, author, and short description with 'bqmod set'
    Step 3: Set input types with 'bqmod inputs'
    Step 4: Set output types and names with 'bqmod outputs'
    Step 5: Review module configurations with 'bqmod summary'
    Step 6: Create module files with 'bqmod create_module'
    """
    if ctx.invoked_subcommand == 'init':
        pass
    else:
        try:
            with open('bqconfig.json') as json_data_file:
                config = json.load(json_data_file)
                ctx.obj = config
        except IOError:
            click.echo("bqconfig.json not in folder, initialize a bqconfig file with `bqmod init`")


def create_config_file():
    """ Creates bqconfig.json file which will store a dictionary of values used to generate module files"""
    with open("bqconfig.json", "w") as json_data_file:
        config_data = {'Name': None, 'Author': None, 'Description': None, 'Inputs': {}, 'Outputs': {}}
        json.dump(config_data, json_data_file)


@bqmod.command("init")
@click.pass_context
def init(ctx):
    """  Initializes a bqmodule config file as bqconfig.json

    If one already exits, prompts user if they would like to overwrite it"""
    try:
        with open('bqconfig.json') as _ :
            if click.confirm('Bqmodule config file already in directory. Would you like to overwrite?', abort=True):
                create_config_file()

    except IOError:
        create_config_file()


@bqmod.command("set", no_args_is_help=True)
@click.option("--name", "-n", default=None, help="Module name with no spaces. Same as {ModuleName} folder")
@click.option("--author", "-a", default=None, help="Authors name in quotations")
@click.option("--description", "-d", default=None, help="Write short description in quotations")
# @click.option("--base_docker", "-b", default=None, help="Base docker image used to containarize source code") # TODO
@click.pass_context
def set(ctx, name, author, description):
    """ Set name of module, author, and short description"""

    if name:
        ctx.obj['Name'] = name
    if author:
        ctx.obj['Author'] = author
    if description:
        ctx.obj['Description'] = description

    if name or author or description:
        with open("bqconfig.json", "w") as json_data_file:
            json.dump(ctx.obj, json_data_file)
    else:
        click.echo("Need to include at least on option [--name --author --description]")
        click.echo(ctx.invoked_subcommand)


def check_var_name(name):
    return '_'.join(name.split()).lower()


@bqmod.command("inputs", no_args_is_help=True)
@click.option("--image", is_flag=True, default=False, help="Flag to indicate input of type image")
@click.option("--blob", is_flag=True, default=False, help="Flag to indicate an input that is not of type image")
@click.option("--input_name", "-n", required=True, default=None, help="Name of the input to be shown in Bisque result. Ex. Input Image")
@click.pass_context
def inputs(ctx, image, blob, input_name):  #  NEED TO ADD FUNCTIONALITY TO CHANGE INPUT
    """Sets the type of input.

    Supported inputs include : --image"""

    if image:
        input_type = 'image'
    elif blob:
        input_type = 'blob'  # Unsure if this works
    else:
        # raise click.BadOptionUsage(image, 'You must specify an input type. Use bqmod inputs --help for more info', ctx=ctx)
        raise click.UsageError('Must include input type: --image', ctx=ctx)

    try:
        if check_var_name(ctx.obj['Inputs'][input_name]) == check_var_name(input_name):
            if click.confirm('An input with the name "%s" has already been set (case-insensitive). Would you like to overwrite?' % input_name, abort=True):
                ctx.obj['Inputs'][input_name] = input_type
    except KeyError:
        ctx.obj['Inputs'][input_name] = input_type


    with open("bqconfig.json", "w") as json_data_file:
        json.dump(ctx.obj, json_data_file)


@bqmod.command("outputs", no_args_is_help=True)
@click.option("--image", "-i", is_flag=True, default=False, help="Flag to indicate output of type image") # NEED TO ADD TABLE FUNCT
@click.option("--csv", "-c", is_flag=True, default=False, help="Flag to indicate csv output which will be uploaded to files in Bisque")
@click.option("--output_name", "-n", required=True, default=None, help="Name of the output to be shown in Bisque result. Ex. Segmented Image")
@click.pass_context
def outputs(ctx, image, csv,  output_name):  #  NEED TO ADD FUNCTIONALITY TO CHANGE OUTPUT
    """Set the types of outputs and their respective output names.

        \b
        Supported outputs include : --image
        Ex. bqmod outputs --image --output_name "Segmented Image" """

    if image:
        output_type = 'image'
    elif csv:
        output_type = 'csv'
    else:
        raise click.UsageError('Must include an output type: --image, --csv', ctx=ctx)

    try:
        if check_var_name(ctx.obj['Outputs'][output_name]) ==  check_var_name(output_name):
            if click.confirm('An input with the name "%s" has already been set. Would you like to overwrite it?' % output_name, abort=True):
                ctx.obj['Inputs'][output_name] = output_type
    except KeyError:
        ctx.obj['Outputs'][output_name] = output_type

    with open("bqconfig.json", "w") as json_data_file:
        json.dump(ctx.obj, json_data_file)


@bqmod.command("summary")
@click.pass_context
def summary(ctx):
    """ Print bqmodule configuration settings."""
    for key in ctx.obj:
        click.secho("%s: %s" % (key, ctx.obj[key]), fg='green')


@bqmod.command("create_module")
@click.pass_context
def create_module(ctx):
    """ Create module files"""

    BQ_module_xml = XMLGenerator(ctx.obj['Name'])

    BQ_module_xml.xml_set_module_name()
    for input_name in ctx.obj['Inputs']:
        BQ_module_xml.edit_xml('inputs', ctx.obj['Inputs'][input_name])

    BQ_module_xml.edit_xml('inputs', ctx.obj['Inputs'][0])
    BQ_module_xml.edit_xml('inputs', 'mex')
    BQ_module_xml.edit_xml('inputs', 'bisque_token')
    BQ_module_xml.edit_xml('outputs', ctx.obj['Outputs'][0], out_name=ctx.obj['Output_names'][0])
    BQ_module_xml.edit_xml('title', ctx.obj['Name'])
    BQ_module_xml.edit_xml('authors', ctx.obj['Author'])
    BQ_module_xml.edit_xml('description', ctx.obj['Description'])
    BQ_module_xml.write_xml()

    click.secho("{%s.xml created" % ctx.obj['Name'], fg='green')


@bqmod.command("create_module_pro")
@click.pass_context
def create_module_pro(ctx):
    """ Create module files"""

    BQ_module_xml = XMLGenerator(ctx.obj['Name'])

    BQ_module_xml.xml_set_module_name()

    for input_name in ctx.obj['Inputs']:
        BQ_module_xml.add_input(ctx.obj['Inputs'][input_name])

    BQ_module_xml.edit_xml('inputs', 'mex')
    BQ_module_xml.edit_xml('inputs', 'bisque_token')

    for output_name in ctx.obj['Outputs']:
        BQ_module_xml.add_output(ctx.obj['Outputs'][output_name])

    BQ_module_xml.edit_xml('title', ctx.obj['Name'])
    BQ_module_xml.edit_xml('authors', ctx.obj['Author'])
    BQ_module_xml.edit_xml('description', ctx.obj['Description'])
    BQ_module_xml.write_xml()

    click.secho("{%s.xml created" % ctx.obj['Name'], fg='green')



# Create module: create xml, copy PythonScriptWrapper,

# 2 options: 1) Git repo with xml template, PythonScriptWrapper, runtime_config, setup.py, bqmodule.py, generatexml.
#            2) Have the click library pull these templates from a repo when calling a create_module.
#               *)  Need to build new image based on module image


if __name__ == '__main__':
    bqmod()