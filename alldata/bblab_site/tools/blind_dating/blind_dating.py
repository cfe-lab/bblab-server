import subprocess
import tempfile
import os
import sys
import pathlib

SELF_PATH = pathlib.Path(__file__).parent.absolute()

# # Add the path to util scripts.
# UTIL_PATH = os.environ.get('BBLAB_UTIL_PATH', 'fail')
# if UTIL_PATH == 'fail':
#     UTIL_PATH = os.path.abspath(
#         os.path.join(SELF_PATH, '..', '..', 'depend', 'util_scripts')
#     )
# sys.path.append(UTIL_PATH)
from depend.util_scripts import mailer

R_SCRIPTS_PATH = os.path.join(SELF_PATH, 'repo', 'src')
ROOT_AND_REGRESS_SCRIPT = os.path.join(R_SCRIPTS_PATH, 'root_and_regress.R')
PLOT_SCRIPT = os.path.join(R_SCRIPTS_PATH, 'plot_divergence_vs_time.R')


# def get_inputs_and_outputs(input_path, output_path):
#     result = {
#         'inputs': {
#             'tree': os.path.join(input_path, 'tree.nwk'),
#             'info': os.path.join(input_path, 'info.csv')
#         }
#     }


def get_regress_cmd(tree, info, output_path):
    jid = generate_job_id()
    cmd = [
        'Rscript',
        ROOT_AND_REGRESS_SCRIPT,
        f'--runid={jid}',
        f'--tree={tree}',
        f'--info={info}',
        f'--rootedtree={os.path.join(output_path, "rooted_tree.nwk")}',
        f'--data={os.path.join(output_path, "data.nwk")}',
        f'--stats={os.path.join(output_path, "stats.nwk")}'
    ]
    return cmd


def get_plot_cmd(output_path):
    jid = generate_job_id()
    cmd = [
        'Rscript',
        ROOT_AND_REGRESS_SCRIPT,
        f'--runid={jid}',
        f'--tree={tree}',
        f'--info={info}',
        f'--rootedtree={os.path.join(output_path, "rooted_tree.nwk")}',
        f'--data={os.path.join(output_path, "data.nwk")}',
        f'--stats={os.path.join(output_path, "stats.nwk")}'
    ]
    return cmd


def run_job(command):
    job = subprocess.Popen(command)
    return job


def generate_job_id():
    return int.from_bytes(os.urandom(2), sys.byteorder)


def get_html_results(tree_file):
    html = (
        f'<h1>{generate_job_id()}</h1>'
        f'tree file: {tree_file.read()}'
    )
    return html


def send_mail(recipient, subject, body):
    mail_sent = mailer.send_sfu_email(
        'BCCFE Blind Dating Webapp',
        recipient,
        subject,
        body
    )
    return mail_sent