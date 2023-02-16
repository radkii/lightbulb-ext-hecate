import argparse
import os.path as osp
from distutils.dir_util import copy_tree

parser = argparse.ArgumentParser(description='Acts upon existing lightbulb extension modules.', prog='lightbulb.ext.hecate')
parser.add_argument('--template', metavar='EXT_PATH', dest='ext_path',
                help='generates template files for the extension file at EXT_PATH')

args = parser.parse_args()
if not osp.exists(args.ext_path) or not args.ext_path.endswith('.py'):
    raise FileNotFoundError("The path provided is not a python file")

copy_tree(osp.join(osp.dirname(__file__), 'template'), osp.dirname(args.ext_path))
print(f"Generated template for extension '{osp.basename(args.ext_path)}' successfully")
