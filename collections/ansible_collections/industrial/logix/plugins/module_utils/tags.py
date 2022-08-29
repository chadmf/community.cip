from typing import Type, Tuple
from ansible_collections.industrial.logix.plugins.module_utils.logix import LogixUtil
from pycomm3 import Tag


class TagCheck:
    def __init__(self, logix_util: Type[LogixUtil], tag_name: str):
        self.logix_util = logix_util
        self.tag_name = tag_name
        self.msg = ''

    def check_tag_exists(self):
        response = self.logix_util.plc.read(self.tag_name)
        if response.error:
            raise Exception('Tag %s read error: %s' % (self.tag_name, response.error))

    def check_tag_permissions(self):
         # External access value of 'Read/Write' permits us to modify the value. 'Read Only' or 'None' does not.
         # https://rockwellautomation.custhelp.com/app/answers/answer_view/a_id/67071/loc/en_US#__highlight
        tag_info = self.logix_util.plc.get_tag_info(self.tag_name)
        if tag_info['external_access'] != 'Read/Write':
            raise Exception('Tag %s does not have correct permissions' % self.tag_name)

    def verify(self) -> Tuple[bool, str]:
        try:
            self.check_tag_exists()
            self.check_tag_permissions()
            return (True, self.msg)
        except Exception as e:
            self.msg = e
            return (False, self.msg)


# can add type validation for plc_tag for all compare statements
class TagValueCheck():
    def __init__(self, param_tag_value: any, plc_tag: Type[Tag]):
        self.param_tag_value = param_tag_value
        self.plc_tag_value = plc_tag.value
        self.plc_data_type = plc_tag.type
        self.int_data_types = ['INT', 'DINT', 'SINT', 'LINT', 'USINT', 'UINT', 'UDINT', 'ULINT']

    def update_plc_tag(self, plc_tag: Type[Tag]):
        self.plc_tag_value = plc_tag.value
        self.plc_tag_type = plc_tag.type

    def compare_str(self):
        return self.param_tag_value == self.plc_tag_value

    def compare_bool(self):
        return self.param_tag_value == self.plc_tag_value

    # TODO: implement support for precision
    def compare_float(self):
        return str(self.param_tag_value) in str(self.plc_tag_value)

    # TODO: implement support for ranges
    def compare_int(self):
        return self.param_tag_value == self.plc_tag_value

    def compare(self) -> bool:
        if self.plc_data_type == 'STRING':
            return self.compare_string()
        elif self.plc_data_type == 'BOOL':
            return self.compare_bool()
        elif self.plc_data_type == 'REAL' or self.plc_data_type == 'FLOAT':
            return self.compare_float()
        elif self.plc_data_type in self.int_data_types:
            return self.compare_int()
        return False
