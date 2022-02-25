import xml.etree.ElementTree as ET
from xml.dom import minidom


# Return a pretty-printed XML string for the Element.

class XMLGenerator():
    def __init__(self, module_name):
        self.module_name = module_name
        # Read in template xml into string to and remove newlines for proper formatting.
        with open('xml_template.xml', "r") as xml_template:
            xml_string = xml_template.read().replace("\n", "")
        # Build xml tree from formatted string.
        self.root = ET.fromstring(xml_string)
        # Set module name in xml
        self.xml_set_module_name()

    def write_xml(self):
        INDENT = "     "
        rough_string = ET.tostring(self.root)
        reparsed = minidom.parseString(rough_string)
        # prettified_xmlStr is a byte object in order to include the encoding
        prettified_xmlStr = reparsed.toprettyxml(indent=INDENT, newl='\n', encoding='utf-8')

        # prettified_xmlStr = prettify(my_root)
        # print(prettified_xmlStr.decode().replace('\n\n',''))
        with open(self.module_name + '.xml', "w") as output_file:
            # Change byte object to string
            str_xml = prettified_xmlStr.decode()
            output_file.write(str_xml)

    def xml_set_module_name(self):
        self.root.attrib['name'] = self.module_name


        # <tag name="inputs">
        #         <tag name="table_url" type="resource">
        #             <template>
        #                 <tag name="accepted_type" value="table" />
        #                 <tag name="accepted_type" value="dataset" />
        #                 <tag name="label" value="Table to extract metadata" />
        #                 <tag name="prohibit_upload" value="true" type="boolean" />
        #             </template>
        #         </tag>


        # <tag name="reducer_url"  type="resource">
        #     <template>
        #         <tag name="label" value="Select a PyTorch Model" />
        #         <tag name="accepted_type" value="file" />
        #         <tag name="prohibit_upload" value="true" />
        #          <tag name="query" value="filename:*.pt" />
        #          <tag name="example_query" value="default_reducer:true" />
        #          <tag name="example_type" value="file" />
        #     </template>
        # </tag>

    def add_input(self, type, input_name):

        input_var_name = '_'.join(input_name.split()).lower()

        for child in self.root:

            if child.attrib['name'] == 'inputs':
                if type == 'image':
                    input_name_tag = ET.SubElement(child, 'tag', attrib={'name': input_var_name, 'type': 'resource'})
                    template_tag = ET.SubElement(input_name_tag, 'template')
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': input_name})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'image'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'dataset'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'prohibit_upload', 'value': 'True'})
                elif type == 'blob':
                    input_name_tag = ET.SubElement(child, 'tag', attrib={'name': input_var_name, 'type': 'resource'})
                    template_tag = ET.SubElement(input_name_tag, 'template')
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': input_name})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'file'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'prohibit_upload', 'value': 'True'})
                elif type == 'table':
                    input_name_tag = ET.SubElement(child, 'tag', attrib={'name': input_var_name, 'type': 'resource'})
                    template_tag = ET.SubElement(input_name_tag, 'template')
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': input_name})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'table'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'dataset'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'prohibit_upload', 'value': 'True'})
                elif type == 'mex':
                    ET.SubElement(child, 'tag', attrib={'name': 'mex_url', 'type': 'system-input'})
                elif type == 'bisque_token':
                    ET.SubElement(child, 'tag', attrib={'name': 'bisque_token', 'type': 'system-input'})

    def add_output(self, type, output_name):

        outut_var_name = '_'.join(output_name.split()).lower()

        for child in self.root:
            if type == 'image':
                output_name_tag = ET.SubElement(child, 'tag', attrib={'name': outut_var_name, 'type': 'image'})
                template_tag = ET.SubElement(output_name_tag, 'template')
                ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': output_name})
            if type == 'csv':
                output_name_tag = ET.SubElement(child, 'tag', attrib={'name': outut_var_name, 'type': 'table'})
                template_tag = ET.SubElement(output_name_tag, 'template')
                ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': output_name})
            if type == 'blob':
                output_name_tag = ET.SubElement(child, 'tag', attrib={'name': outut_var_name})
                template_tag = ET.SubElement(output_name_tag, 'template')
                ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': output_name})




    def edit_xml(self, field, value, out_name='Output'):

        for child in self.root:
            # print(child.tag, child.attrib)
            # print(child.attrib)

            if field == 'inputs' and child.attrib['name'] == 'inputs':
                if value == 'image':
                    input_name_tag = ET.SubElement(child, 'tag', attrib={'name': 'resource_url', 'type': 'resource'})
                    template_tag = ET.SubElement(input_name_tag, 'template')
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': 'Select Image'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'image'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'accepted_type', 'value': 'dataset'})
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'prohibit_upload', 'value': 'True'})
                elif value == 'mex':
                    ET.SubElement(child, 'tag', attrib={'name': 'mex_url', 'type': 'system-input'})
                elif value == 'bisque_token':
                    ET.SubElement(child, 'tag', attrib={'name': 'bisque_token', 'type': 'system-input'})

            elif field == 'outputs' and child.attrib['name'] == 'outputs':
                if value == 'image':
                    output_name_tag = ET.SubElement(child, 'tag', attrib={'name': 'OutImage', 'type': 'image'})
                    template_tag = ET.SubElement(output_name_tag, 'template')
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': out_name})
                if value == 'csv': # TEMPORARY FOR CONVINIENCE -> FILL IN  INFO YOURSELF
                    output_name_tag = ET.SubElement(child, 'tag', attrib={'name': 'OutCsv'})
                    template_tag = ET.SubElement(output_name_tag, 'template')
                    ET.SubElement(template_tag, 'tag', attrib={'name': 'label', 'value': out_name})


            elif field == 'title' and child.attrib['name'] == 'title':
                child.attrib['value'] = value

            elif field == 'authors' and child.attrib['name'] == 'authors':
                child.attrib['value'] = value

            elif field == 'description' and child.attrib['name'] == 'description':
                child.attrib['value'] = value


if __name__ == '__main__':
    module_name = 'EdgeDetection'
    authors = 'Ivan'
    description = 'Edge detector'

    BQ_module_xml = XMLGenerator(module_name)

    BQ_module_xml.xml_set_module_name()
    BQ_module_xml.edit_xml('inputs', 'image')
    BQ_module_xml.edit_xml('inputs', 'mex')
    BQ_module_xml.edit_xml('inputs', 'bisque_token')
    BQ_module_xml.edit_xml('outputs', 'image', out_name='Edge Image')
    BQ_module_xml.edit_xml('title', module_name)
    BQ_module_xml.edit_xml('authors', authors)
    BQ_module_xml.edit_xml('description', description)
    BQ_module_xml.write_xml()
