import platform
from urllib import request
from os import path, mkdir, system
import re
import subprocess
import sys


confdUrl = 'https://github.com/kelseyhightower/confd/releases/download/v0.15.0/confd-0.15.0-windows-amd64.exe'
confdExeExtension = '.exe'
linuxConfdUrl ='https://github.com/kelseyhightower/confd/releases/download/v0.15.0/confd-0.15.0-linux-amd64'
darwinConfdUrl ='https://github.com/kelseyhightower/confd/releases/download/v0.15.0/confd-0.15.0-darwin-amd64'

os = platform.system()
if(os == 'Linux'):
    confdUrl=linuxConfdUrl
    confdExeExtension=''
elif(os == 'Darwin'):
    confdUrl=darwinConfdUrl
    confdExeExtension=''

confdBasePath = path.dirname(path.realpath(__file__))
print (confdBasePath)
confdDevBasePath = path.join(confdBasePath,'dev')
print(confdDevBasePath)
confdTmplRelPath = 'production.tmpl'
confdConfigPath = path.join(confdBasePath, 'production.toml')
confdTmplPath = path.join(confdBasePath, confdTmplRelPath)
devTmplPath = path.join(confdDevBasePath,'templates',confdTmplRelPath)
devConfigPath = path.join(confdDevBasePath, 'conf.d/development.toml')
confdPath = path.join(confdBasePath, f'confd{confdExeExtension}')

def download (uri, filename):
  print(f'Downloading {filename} from {uri}')
  request.urlretrieve(uri,filename)

def downloadIfNotExists (uri, filename):
  print(f'Checking if {filename} exists.')
  if (path.isfile(filename)):
      print(f'{filename} exists, proceeding to the next stage.')
  else:
    print(f'{filename} does not exist.')
    download(uri, filename)
    if (os == 'Linux'):
      system(f'chmod +x {filename}')

def copyFile (src, dest, mutationFunc):
  with open(src,'r') as srcFile:
      data = srcFile.read()
  if(mutationFunc):
      data=mutationFunc(data)
  with open(dest,'w') as destFile:
    destFile.write(data)

def createDirIfNotExists (dir):
  if (not path.isdir(dir)):
    mkdir(dir)

def createDevConfdConfigFile (env):
  createDirIfNotExists(confdDevBasePath)
  createDirIfNotExists(path.join(confdDevBasePath, 'conf.d'))
  createDirIfNotExists(path.join(confdDevBasePath, 'templates'))
  if (not env):
     env = 'default'
  print('Creating a development toml file.')
  mutate= lambda data: re.sub(r'dest = .*', f'dest = "config/{env}.json"',data)
  copyFile(confdTmplPath, devTmplPath,None)
  copyFile(confdConfigPath, devConfigPath, mutate)


def runConfd():
  print('Running confd')
  try:
    subprocess.run([f'{confdPath} -onetime -backend env -confdir {confdDevBasePath}'],shell=True,check=True)
  except:
    print('confd failed to run');

def createTargetDir():
  createDirIfNotExists('config')

def help ():
  print('usage: "node <path to this script> [options]\n')
  print('options:')
  print('--environment <environment name>			generate config file for <environment name> environment instead of default.')
  print('--help			shows this help page.')
  print()
  exit(0)

def main ():
  try:
    sys.argv.index('--help')
    help()
    exit(0)
  except:
    pass
  try:
    envIdx = sys.argv.index('--environment')
    env = sys.argv[envIdx + 1]
  except:
    env = None
  downloadIfNotExists(confdUrl, confdPath)
  createDevConfdConfigFile(env)
  createTargetDir()
  runConfd()

main()
