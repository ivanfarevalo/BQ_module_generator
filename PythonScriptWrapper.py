import sys
# import io
from lxml import etree
import xml.etree.ElementTree as ET
import optparse
import logging
import os
# import numpy as np

# It is importing from source

logging.basicConfig(filename='PythonScript.log', filemode='a', level=logging.DEBUG)
log = logging.getLogger('bq.modules')

# from bqapi.comm import BQCommError
from bqapi.comm import BQSession
from bqapi.util import fetch_blob

# standardized naming convention for running modules.
from src.BQ_run_module import run_module


class ScriptError(Exception):
    def __init__(self, message):
        self.message = "Script error: %s" % message

    def __str__(self):
        return self.message


class PythonScriptWrapper(object):
    def __init__(self):
        for file in os.listdir(): # Might change it to read parameters from .JSON
            if file.endswith(".xml"):
                # Get xml file name as module name
                if hasattr(self, 'module_name'):
                    raise ScriptError('More than 1 .xml file present in directory, make appropiate changes and rebuild image')
                else:
                    self.module_name = file[:-4]

        tree = ET.parse(self.module_name+'.xml')  # Load module xml as tree
        self.root = tree.getroot()  # Get root node of tree


    # For very simple, image in image out case.  Will extend to more input/output cases.
    # def get_xml_data(self, field, out_xml_value='Default', bq=None):
    #     xml_data = []
    #
    #     for node in self.root:  # Iterate tree to parse necessary information
    #         # print(child.tag, child.attrib)
    #         if field == 'inputs' and node.attrib['name'] == 'inputs':
    #
    #             for input in node:
    #                 if input.attrib['name'] == 'resource_url':
    #                     resource_ulr = bq.load(self.options.resource_url)
    #                     resource_name = resource_ulr.__dict__['name']
    #                     resource_dict = {'resource_url': resource_ulr, 'resource_name':resource_name}
    #                     xml_data.append(resource_dict)
    #
    #         elif field == 'outputs' and node.attrib['name'] == 'outputs':
    #
    #             for output in node:
    #                 if output.attrib['name'] == 'OutImage':
    #                     output.set('value', out_xml_value)
    #                     output_xml = ET.tostring(output).decode('utf-8')
    #                     xml_data.append(output_xml)
    #
    #     log.info(f" xml data for {field} from wrapper is {xml_data}")
    #     return xml_data




    # log.debug('kw is: %s', str(kw))
    # predictor_uniq = predictor_url.split('/')[-1]
    # reducer_uniq = reducer_url.split('/')[-1]
    # table_uniq = table_url.split('/')[-1]
    #
    # predictor_url = bq.service_url('blob_service', path=predictor_uniq)
    # predictor_path = os.path.join(kw.get('stagingPath', ''), 'predictor.sav')
    # predictor_path = bq.fetchblob(predictor_url, path=predictor_path)
    #
    # reducer_url = bq.service_url('blob_service', path=reducer_uniq)
    # reducer_path = os.path.join(kw.get('stagingPath', ''), 'reducer.sav')
    # reducer_path = bq.fetchblob(reducer_url, path=reducer_path)

    def get_xml_outputs(self, out_xml_value):
        xml_data = []

        for node in self.root:  # Iterate tree to parse necessary information
            # print(node.tag, node.attrib)
            if node.attrib['name'] == 'outputs':
                for output in node:
                    if output.attrib['name'] == 'OutImage':
                        output.set('value', out_xml_value)
                        output_xml = ET.tostring(output).decode('utf-8')
                        xml_data.append(output_xml)

        log.info(f"***** Output XML data: {xml_data}")
        return xml_data


    def get_xml_inputs(self, bq): #TODO Not hardcoded resource_url
        xml_data = []

        for node in self.root:  # Iterate tree to parse necessary information
            # print(node.tag, node.attrib)
            if node.attrib['name'] == 'inputs':

                for child in node.iter():
                    # <tag name="resource_url" type="resource">
                    # input_name = ''

                    try:
                        if (child.attrib['name'] and child.attrib['type'] == 'resource'):
                            input_name = child.attrib['name']
                    except KeyError:
                        pass

                    try:
                        if (child.attrib['name'] == 'accepted_type' and child.attrib['value'] == 'image'):
                            print("INPUT OF TYPE IMAGE!")

                            # resource_url = bq.load(self.options.resource_url)
                            log.info(f"***** Input XML data: {xml_data}")
                            resource_url = bq.load(getattr(self.options, input_name))
                            resource_name = resource_url.__dict__['name']
                            resource_dict = {'resource_url': resource_url, 'resource_name': resource_name}
                            xml_data.append(resource_dict)

                    except KeyError:
                        pass

        log.info(f"***** Input XML data: {xml_data}")
        # SAMPLE LOG
        # INFO:bq.modules:***** Input XML data: [{'resource_url': (image:http://128.111.185.163:8080/data_service/00-pkGCYS4SPCtQVcdZUUj4sX), 'resource_name': '500px-Manatee_at_Sea_World_Orlando_Mar_10.jpeg'}]
        return xml_data

    def pre_process(self, bq):
        """
        Ingests and logs xml file inputs and outputs

        :param bq:
        :return:
        """

        log.info('Options: %s' % (self.options))

        self.inputs = self.get_xml_inputs(bq=bq)

        # Saves and log input
        for input in self.inputs:

            log.info("Process resource as %s" % (input['resource_name']))
            log.info("Resource meta: %s" % (input['resource_url']))
            cwd = os.getcwd()
            log.info("Current work directory: %s" % (cwd))

            # SAMPLE LOG
            # INFO:bq.modules:Process resource as 500px-Manatee_at_Sea_World_Orlando_Mar_10.jpeg
            # INFO:bq.modules:Resource meta: (image:name=500px-Manatee_at_Sea_World_Orlando_Mar_10.jpeg,value=file://admin/2022-02-25/500px-Manatee_at_Sea_World_Orlando_Mar_10.jpeg,type=None,uri=http://128.111.185.163:8080/data_service/00-pkGCYS4SPCtQVcdZUUj4sX,ts=2022-02-25T17:05:13.289578,resource_uniq=00-pkGCYS4SPCtQVcdZUUj4sX)
            # INFO:bq.modules:Current work directory: /module

            # Saves resource to module container
            result = fetch_blob(bq, getattr(self.options, input['resource_name']), dest=os.path.join(cwd, input['resource_name']))
            # result = fetch_blob(bq, self.options.resource_url, dest=os.path.join(cwd, input['resource_name']))
            log.info(f"Output of fetch blob in pre_process : {result}")

            # SAMPLE LOG
            # INFO:bq.modules:Output of fetch blob in pre_process : {'http://128.111.185.163:8080/data_service/00-pkGCYS4SPCtQVcdZUUj4sX': './500px-Manatee_at_Sea_World_Orlando_Mar_10.jpeg'}


    def run(self):
        """
        Run Python script

        """
        bq = self.bqSession
        try:
            bq.update_mex('Pre-process the images')
            self.pre_process(bq)
        except (Exception, ScriptError) as e:
            log.exception("Exception during pre_process")
            bq.fail_mex(msg="Exception during pre-process: %s" % str(e))

            return

        #        input_image, heatmap, covid, pna, normal= predict_label(log, self.image_name)
        #        heatmap=np.transpose(heatmap, (1, 2, 0))
        #        input_image=np.transpose(input_image, (1, 2, 0))

        input_file_path = os.path.join(os.getcwd(), self.inputs[0]['resource_name'])
        # output_folder_path = os.path.join(os.path.dirname(os.getcwd()), 'outputs')
        output_folder_path = os.getcwd()

        out_data_path = run_module(input_file_path, output_folder_path)  # Path to output files HARDCODED FOR NOW
        log.info("Output image path: %s" % out_data_path)

        # SAMPLE LOG
        # INFO:bq.modules:Output image path: /module/500px-Manatee_at_Sea_World_Orlando_Mar_10._out.jpg



        #        img = nib.Nifti1Image(input_image*heatmap, np.eye(4))  # Save axis for data (just identity)
        #
        #        img.header.get_xyzt_units()
        #        self.outfiles=self.image_name+'heatmap.nii'
        #        img.to_filename(self.outfiles)  # Save as NiBabel file

        #       z=input_image.shape[2]

        self.bqSession.update_mex('Returning results')

        bq.update_mex('Uploading Mask result')
        self.out_image = self.upload_service(bq, out_data_path, data_type='image')
        #         log.info('Total number of slices:{}.\nNumber of slices predicted as Covid:{}.\nNumber of slices predicted as PNA: {}\nNumber of slices predicted as Normal:{}'.format(z, covid, pna, normal))

        #         self.output_resources.append(out_xml)

        self.output_resources = self.get_xml_outputs(out_xml_value=(str(self.out_image.get('value'))))
        # self.output_resources = self.get_xml_data('outputs', out_xml_value=(str(self.out_image.get('value'))))

        # out_imgxml = """<tag name="EdgeImage" type="image" value="%s">
        #                 <template>
        #                   <tag name="label" value="Edge Image" />
        #                 </template>
        #               </tag>""" % (str(self.out_image.get('value')))

        #        out_xml = """<tag name="Metadata">
        #                    <tag name="Filename" type="string" value="%s"/>
        #                    <tag name="Depth" type="string" value="%s"/>
        #                     <tag name="Covid" type="string" value="%s"/>
        #                     <tag name="Pneumonia" type="string" value="%s"/>
        #                     <tag name="normal" type="string" value="%s"/>
        #                     </tag>""" % (self.image_name, str(z), str(covid), str(pna), str(normal))

        #        outputs = [out_imgxml, out_xml]
        #         outputs = [out_imgxml]
        log.debug(f"***** self.output_resources = {self.output_resources}")
        # SAMPLE LOG
        # ['<tag name="OutImage" type="image" value="http://128.111.185.163:8080/data_service/00-ExhzBeQiaX5F858qNjqXzM">\n               <template>\n                    <tag name="label" value="Edge Image" />\n               </template>\n          </tag>\n     ']


        # save output back to BisQue
        # for output in outputs:
        #     self.output_resources.append(output)

    def setup(self):
        """
        Pre-run initialization
        """
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_resources = []

    def tear_down(self):  # NEED TO GENERALIZE
        """
        Post the results to the mex xml
        """
        self.bqSession.update_mex('Returning results')
        outputTag = etree.Element('tag', name='outputs')
        for r_xml in self.output_resources:
            if isinstance(r_xml, str):
                r_xml = etree.fromstring(r_xml)
            res_type = r_xml.get('type', None) or r_xml.get(
                'resource_type', None) or r_xml.tag
            # append reference to output
            if res_type in ['table', 'image']:
                outputTag.append(r_xml)
                # etree.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))
            else:
                outputTag.append(r_xml)
                # etree.SubElement(outputTag, r_xml.tag, name=r_xml.get('name', '_'), type=r_xml.get('type', 'string'), value=r_xml.get('value', ''))
        log.debug('Output Mex results: %s' %
                  (etree.tostring(outputTag, pretty_print=True)))
        self.bqSession.finish_mex(tags=[outputTag])

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to options attribute (unless already set)

            @param: mex_xml
        """
        # inputs are all non-"script_params" under "inputs" and all params under "script_params"
        mex_inputs = mex_xml.xpath(
            'tag[@name="inputs"]/tag[@name!="script_params"] | tag[@name="inputs"]/tag[@name="script_params"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input':  # skip system input values
                    if not getattr(self.options, tag.get('name', ''), None):
                        log.debug('Set options with %s as %s' % (tag.get('name', ''), tag.get('value', '')))
                        setattr(self.options, tag.get('name', ''), tag.get('value', ''))
        else:
            log.debug('No Inputs Found on MEX!')

    def uploadimgservice(self, bq, filename):
        """
        Upload mask to image_service upon post process
        """
        mex_id = bq.mex.uri.split('/')[-1]

        log.info('Up Mex: %s' % (mex_id))
        log.info('Up File: %s' % (filename))
        resource = etree.Element(
            'image', name='ModuleExecutions/EdgeDetection/' + filename)
        t = etree.SubElement(resource, 'tag', name="datetime", value='time')
        log.info('Creating upload xml data: %s ' %
                 str(etree.tostring(resource, pretty_print=True)))
        # os.path.join("ModuleExecutions","CellSegment3D", filename)
        filepath = filename
        # use import service to /import/transfer activating import service
        r = etree.XML(bq.postblob(filepath, xml=resource)).find('./')
        if r is None or r.get('uri') is None:
            bq.fail_mex(msg="Exception during upload results")
        else:
            log.info('Uploaded ID: %s, URL: %s' %
                     (r.get('resource_uniq'), r.get('uri')))
            bq.update_mex('Uploaded ID: %s, URL: %s' %
                          (r.get('resource_uniq'), r.get('uri')))
            self.furl = r.get('uri')
            self.fname = r.get('name')
            resource.set('value', self.furl)

        return resource

    def upload_service(self, bq, filename, data_type='image'):
        """
        Upload resource to specific service (image, table, blob) upon post process
        """
        mex_id = bq.mex.uri.split('/')[-1]

        log.info('Up Mex: %s' % (mex_id))
        log.info('Up File: %s' % (filename))
        resource = etree.Element(
            data_type, name='ModuleExecutions/' + self.module_name + '/' + filename)
        t = etree.SubElement(resource, 'tag', name="datetime", value='time')
        log.info('Creating upload xml data: %s ' %
                 str(etree.tostring(resource, pretty_print=True)))
        # os.path.join("ModuleExecutions","CellSegment3D", filename)
        filepath = filename
        # use import service to /import/transfer activating import service
        r = etree.XML(bq.postblob(filepath, xml=resource)).find('./')
        if r is None or r.get('uri') is None:
            bq.fail_mex(msg="Exception during upload results")
        else:
            log.info('Uploaded ID: %s, URL: %s' %
                     (r.get('resource_uniq'), r.get('uri')))
            bq.update_mex('Uploaded ID: %s, URL: %s' %
                          (r.get('resource_uniq'), r.get('uri')))
            self.furl = r.get('uri')
            self.fname = r.get('name')
            resource.set('value', self.furl)

        return resource

    def validate_input(self):
        """
            Check to see if a mex with token or user with password was provided.

            @return True is returned if validation credention was provided else
            False is returned
        """
        if (self.options.mexURL and self.options.token):  # run module through engine service
            return True
        if (self.options.user and self.options.pwd and self.options.root):  # run module locally (note: to test module)
            return True
        log.debug('Insufficient options or arguments to start this module')
        return False

    def main(self):
        parser = optparse.OptionParser()
        parser.add_option('--mex_url', dest="mexURL")
        parser.add_option('--module_dir', dest="modulePath")
        parser.add_option('--staging_path', dest="stagingPath")
        parser.add_option('--bisque_token', dest="token")
        parser.add_option('--user', dest="user")
        parser.add_option('--pwd', dest="pwd")
        parser.add_option('--root', dest="root")
        # parser.add_option('--resource_url', dest="resource_url")

        (options, args) = parser.parse_args()

        fh = logging.FileHandler('scriptrun.log', mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
                                      '(%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        log.addHandler(fh)

        try:  # pull out the mex

            if not options.mexURL:
                options.mexURL = sys.argv[-2]
            if not options.token:
                options.token = sys.argv[-1]
        except IndexError:  # no argv were set
            pass

        if not options.stagingPath:
            options.stagingPath = ''

        log.debug('\n\nPARAMS : %s \n\n Options: %s' % (args, options))
        self.options = options

        if self.validate_input():

            # initalizes if user and password are provided
            if (self.options.user and self.options.pwd and self.options.root):

                try:
                    self.bqSession = BQSession().init_local(self.options.user, self.options.pwd,
                                                            bisque_root=self.options.root)
                    self.options.mexURL = self.bqSession.mex.uri

                except:
                    return

            # initalizes if mex and mex token is provided
            elif (self.options.mexURL and self.options.token):

                try:
                    self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)
                except:
                    return



            else:
                raise ScriptError('Insufficient options or arguments to start this module')

            try:
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg="Exception during setup: %s" % str(e))
                return
            ####
            try:
                self.run()
            except (Exception, ScriptError) as e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg="Exception during run: %s" % str(e))
                return
            ##
            try:
                self.tear_down()
            except (Exception, ScriptError) as e:
                log.exception("Exception during tear_down")
                self.bqSession.fail_mex(msg="Exception during tear_down: %s" % str(e))
                return

            self.bqSession.close()
        log.debug('Session Close')


if __name__ == "__main__":
    PythonScriptWrapper().main()
