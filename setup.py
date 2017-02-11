from config import config
import os
import requests
import subprocess
import sys
import tarfile


def download_archive(url):
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as f:
            print "Downloading %s" % file_name
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.flush()
    print "Download successful!"
    return file_name


def extract_archive(archive_path):
    extraction_path = os.sep.join(archive_path.split(os.sep)[:-1])
    archive_name = os.path.sep.join(
        archive_path.split(os.path.sep)[-1:]).split(".tar")[0]
    print "Extracting %s" % (archive_path)
    tar = tarfile.open(archive_path, 'r')
    for item in tar:
        tar.extract(item, extraction_path)
    return os.path.join(extraction_path, archive_name)


def add_environvent_path(value):
    print "Adding %s to '$PATH'" % (value)
    if os.name is 'posix':
        sys.path.append(value)


def _run_command(command):
    p = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
    output, err = p.communicate()
    if err is not None:
        print "An error occured while running command:\n%s" % command


def add_firewall_rules():
    print "Adding firewall rules"
    if os.name is 'posix':
        _run_command('sudo iptables -A INPUT -m state --state NEW -s 0.0.0.0 -m tcp -p tcp --dport 9999 -j ACCEPT')
        _run_command('sudo iptables-save')


def set_hostname(hostname):
    if os.name is 'posix':
        command = "hostname %s" % hostname
    subprocess.call(command.split(" "))
    print "Set hostname %s" % hostname

def run_on_startup():
    print "Adding app to run at startup"

if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args(sys.argv[1:])

    CONF = config.compute_config(parsed_arguments.config, "browser")
    url = CONF.driver_download
    path = download_archive(url)
    path = extract_archive(path)
    add_environvent_path(path)
    add_firewall_rules()
    print "Done!"
